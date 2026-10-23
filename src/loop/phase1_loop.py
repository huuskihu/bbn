"""
阶段 1：静态闭环（无可塑性）。

数据流：
    Pong 环境 -> 8 通道感觉编码（place + rate） -> FastHH 细胞
    -> 放电率（滑动窗口） -> 球拍速度 -> Pong 环境
    命中/未命中 -> 可预测/不可预测反馈 -> 同一组 8 通道

本阶段只验证闭环与对照，不包含 STDP/稳态/通道可塑性。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from src.cell.hh_numba import FastHH, HHParams
from src.env.pong import PongConfig, PongEnv


@dataclass
class Phase1Config:
    # 时间
    tick_ms: float = 10.0
    duration_s: float = 60.0

    # 运动读出
    readout_window_ms: float = 300.0
    rate_smoothing: float = 0.2      # 0 = 不平滑，1 = 完全跟随瞬时值
    reference_rate_hz: float = 20.0
    velocity_gain: float = 0.15       # bins/s per Hz
    max_velocity: float = 4.0         # bins/s

    # 感觉编码
    rate_min_hz: float = 4.0
    rate_max_hz: float = 40.0
    place_sigma_bins: float = 1.0
    syn_weight_nS: float = 40.0
    syn_weight_jitter: float = 0.4
    syn_tau_ms: float = 5.0
    E_syn_mV: float = 0.0

    # 反馈
    predictable_rate_hz: float = 100.0
    predictable_duration_ms: float = 100.0
    predictable_weight_nS: float = 10.0
    unpredictable_rate_hz: float = 5.0
    unpredictable_duration_s: float = 4.0
    unpredictable_weight_nS: float = 60.0
    rest_after_miss_s: float = 4.0


class Phase1Loop:
    def __init__(
        self,
        condition: str,
        cfg: Phase1Config | None = None,
        cell_params: HHParams | None = None,
        pong_cfg: PongConfig | None = None,
        seed: int = 0,
    ):
        self.cfg = cfg or Phase1Config()
        self.condition = condition
        self.rng = np.random.default_rng(seed)

        self.cell = FastHH(params=cell_params or HHParams(), dt_ms=0.01, n_channels=8)
        self.env = PongEnv(pong_cfg or PongConfig(), rng=self.rng)

        base = self.cfg.syn_weight_nS
        jitter = self.cfg.syn_weight_jitter
        self.w_syn = base * (1.0 + jitter * self.rng.uniform(-1.0, 1.0, size=8))

        self.spike_hist: deque[float] = deque()

        self.tick_t_ms = 0.0
        self.fb_kind: str | None = None
        self.fb_until_ms = 0.0
        self.rest_until_ms = 0.0

        self.traces: list[tuple] = []
        self._last_velocity = 0.0
        self._rate_smooth = 0.0

    # ------------------------------------------------------------------
    # 感觉与反馈
    # ------------------------------------------------------------------

    def _sensory_increments(self) -> np.ndarray:
        x = self.env.ball_x
        y = self.env.ball_y
        rate_factor = self.cfg.rate_min_hz + (
            self.cfg.rate_max_hz - self.cfg.rate_min_hz
        ) * (1.0 - x)

        inc = np.zeros(8, dtype=np.float64)
        tick_s = self.cfg.tick_ms / 1000.0
        for i in range(8):
            centre = i + 1.0
            g = np.exp(-0.5 * ((y - centre) / self.cfg.place_sigma_bins) ** 2)
            rate = rate_factor * g
            n = self.rng.poisson(rate * tick_s)
            inc[i] = n * self.w_syn[i]
        return inc

    def _feedback_increments(self) -> np.ndarray:
        inc = np.zeros(8, dtype=np.float64)
        if self.fb_kind is None or self.tick_t_ms >= self.fb_until_ms:
            return inc

        tick_s = self.cfg.tick_ms / 1000.0
        if self.fb_kind == "predictable":
            n = self.cfg.predictable_rate_hz * tick_s
            inc[:] = n * self.cfg.predictable_weight_nS
        elif self.fb_kind == "unpredictable":
            p = self.cfg.unpredictable_rate_hz * tick_s
            mask = self.rng.random(8) < p
            inc[mask] = self.cfg.unpredictable_weight_nS
        return inc

    def _schedule_predictable(self):
        self.fb_kind = "predictable"
        self.fb_until_ms = self.tick_t_ms + self.cfg.predictable_duration_ms

    def _schedule_unpredictable(self):
        self.fb_kind = "unpredictable"
        self.fb_until_ms = self.tick_t_ms + self.cfg.unpredictable_duration_s * 1000.0
        self.rest_until_ms = (
            self.tick_t_ms
            + self.cfg.unpredictable_duration_s * 1000.0
            + self.cfg.rest_after_miss_s * 1000.0
        )

    def _schedule_rest(self):
        self.fb_kind = None
        self.rest_until_ms = self.tick_t_ms + self.cfg.rest_after_miss_s * 1000.0

    # ------------------------------------------------------------------
    # 动作
    # ------------------------------------------------------------------

    def _action(self, rate_hz: float) -> float:
        if self.condition == "random_paddle":
            return float(self.rng.uniform(-self.cfg.max_velocity, self.cfg.max_velocity))
        if self.condition == "always_up":
            return self.cfg.max_velocity
        if self.condition == "always_down":
            return -self.cfg.max_velocity

        v = self.cfg.velocity_gain * (rate_hz - self.cfg.reference_rate_hz)
        return float(np.clip(v, -self.cfg.max_velocity, self.cfg.max_velocity))

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------

    def run(self) -> tuple[dict, np.ndarray]:
        n_ticks = int(round(self.cfg.duration_s * 1000.0 / self.cfg.tick_ms))
        window_ms = self.cfg.readout_window_ms

        for _ in range(n_ticks):
            t = self.tick_t_ms

            # 感觉输入：rest 期间关闭
            inc = np.zeros(8, dtype=np.float64)
            if t >= self.rest_until_ms:
                inc += self._sensory_increments()

            # 反馈：与 rest 独立；rest 会覆盖感觉，但反馈仍可在前 4 s 内存在
            inc += self._feedback_increments()

            self.cell.add_syn(inc)
            new_spikes = self.cell.run(
                self.cfg.tick_ms,
                tau_syn_ms=self.cfg.syn_tau_ms,
                E_syn_mV=self.cfg.E_syn_mV,
            )
            for s in new_spikes:
                self.spike_hist.append(float(s))

            t_cut = t + self.cfg.tick_ms - window_ms
            while self.spike_hist and self.spike_hist[0] < t_cut:
                self.spike_hist.popleft()

            rate_hz = len(self.spike_hist) / (window_ms / 1000.0)
            alpha = self.cfg.rate_smoothing
            if alpha > 0:
                self._rate_smooth = (1.0 - alpha) * self._rate_smooth + alpha * rate_hz
                rate_used = self._rate_smooth
            else:
                rate_used = rate_hz

            # rest 期间暂停整个游戏（球与球拍都冻结）。旧实现只冻结球拍、
            # 让球继续前进，会在每次 miss 时不断延长 rest，导致永久休息态。
            if t < self.rest_until_ms:
                velocity = 0.0
                event = None
            else:
                velocity = self._action(rate_used)
                event = self.env.step(self.cfg.tick_ms / 1000.0, velocity)

            if event == "hit":
                if self.condition == "full_feedback":
                    self._schedule_predictable()
            elif event == "miss":
                if self.condition == "full_feedback":
                    self._schedule_unpredictable()
                elif self.condition == "silent":
                    self._schedule_rest()
                # no_feedback / controls: 不安排任何刺激

            self.traces.append(
                (
                    t,
                    self.env.ball_x,
                    self.env.ball_y,
                    self.env.paddle_y,
                    rate_hz,
                    rate_used,
                    velocity,
                    event if event is not None else "",
                    len(new_spikes),
                )
            )
            self._last_velocity = velocity
            self.tick_t_ms += self.cfg.tick_ms

        self.env.finalize()

        trace = np.array(self.traces, dtype=object)
        metrics = {
            "condition": self.condition,
            "duration_s": self.cfg.duration_s,
            "hits": self.env.hits,
            "misses": self.env.misses,
            "n_rallies": self.env.n_rallies,
            "average_rally_length": self.env.average_rally_length,
            "aces": self.env.aces,
            "long_rallies": self.env.long_rallies,
            "mean_impact_error": self.env.mean_impact_error,
            "mean_rate_hz": float(np.mean(trace[:, 4])) if len(trace) else 0.0,
            "max_rate_hz": float(np.max(trace[:, 4])) if len(trace) else 0.0,
            "paddle_range": float(np.max(trace[:, 3]) - np.min(trace[:, 3]))
            if len(trace)
            else 0.0,
            "mean_abs_velocity": float(np.mean(np.abs(trace[:, 6]))) if len(trace) else 0.0,
            "total_spikes": int(self.cell.spike_count),
        }
        return metrics, trace
