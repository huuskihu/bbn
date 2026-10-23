"""
阶段 3：单细胞闭环学习（STDP / 三因子 / 稳态）。

与 Phase 1 的区别：
    - 感觉突触有可塑权重 w_eff = w_base * syn.w；
    - 每个 10 ms tick 内生成精确的 pre spike 时间，交给 FastHH.run_events；
    - 记录精确 post spike 时间，按时间顺序更新 STDP / 资格迹；
    - 命中/未命中产生全局调制信号 D(t) 或仅作为刺激；
    - 每 1 s 做一次稳态缩放。

条件映射：
    phase3a_full      : STDP + 稳态；反馈只作刺激
    phase3b_full      : 资格迹 + 三因子 + 稳态
    phase3b_no_feedback / silent / shuffled : 三因子对照
    static_full       : 固定权重；反馈刺激
    random_paddle     : 忽略细胞输出
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from src.cell.hh_numba import FastHH, HHParams
from src.env.pong import PongConfig, PongEnv
from src.plasticity.homeostasis import HomeostasisConfig, HomeostaticScaler
from src.plasticity.stdp import EligibilitySynapse, STDPConfig, STDPSynapse


@dataclass
class Phase3Config:
    tick_ms: float = 10.0
    duration_s: float = 120.0

    readout_window_ms: float = 300.0
    rate_smoothing: float = 0.2
    reference_rate_hz: float = 20.0
    velocity_gain: float = 0.15
    max_velocity: float = 4.0

    rate_min_hz: float = 4.0
    rate_max_hz: float = 40.0
    place_sigma_bins: float = 1.0
    syn_weight_nS: float = 40.0
    syn_tau_ms: float = 5.0
    E_syn_mV: float = 0.0

    predictable_rate_hz: float = 100.0
    predictable_duration_ms: float = 100.0
    predictable_weight_nS: float = 5.0
    unpredictable_rate_hz: float = 5.0
    unpredictable_duration_s: float = 4.0
    unpredictable_weight_nS: float = 60.0
    rest_after_miss_s: float = 4.0

    # 可塑性
    a_plus: float = 0.01
    a_minus: float = 0.012
    tau_plus_ms: float = 20.0
    tau_minus_ms: float = 20.0
    w_min: float = 0.05
    w_max: float = 1.5
    w_init: float = 1.0
    w_jitter: float = 0.2
    tau_e_ms: float = 1000.0
    eta: float = 0.1
    reward_plus: float = 1.0
    reward_minus: float = -1.0

    # 稳态
    homeostasis_enabled: bool = True
    target_rate_hz: float = 20.0
    hs_alpha: float = 0.05
    hs_interval_s: float = 1.0
    hs_w_min: float = 0.05
    hs_w_max: float = 1.5

    shuffle_rate_hz: float = 0.5


class Phase3Loop:
    def __init__(
        self,
        condition: str,
        cfg: Phase3Config | None = None,
        cell_params: HHParams | None = None,
        pong_cfg: PongConfig | None = None,
        seed: int = 0,
    ):
        self.cfg = cfg or Phase3Config()
        self.condition = condition
        self.rng = np.random.default_rng(seed)

        # 条件解析
        if condition.startswith("phase3a"):
            self.mode = "stdp"
        elif condition.startswith("phase3b"):
            self.mode = "three_factor"
        else:
            self.mode = "none"

        if "shuffled" in condition:
            self.feedback_mode = "shuffled"
        elif "silent" in condition:
            self.feedback_mode = "silent"
        elif "no_feedback" in condition:
            self.feedback_mode = "none"
        elif condition == "random_paddle":
            self.feedback_mode = "none"
        elif condition in ("always_up", "always_down"):
            self.feedback_mode = "none"
        else:
            self.feedback_mode = "full"

        self.cell = FastHH(params=cell_params or HHParams(), dt_ms=0.01, n_channels=8)
        self.env = PongEnv(pong_cfg or PongConfig(), rng=self.rng)

        stdp_cfg = STDPConfig(
            a_plus=self.cfg.a_plus,
            a_minus=self.cfg.a_minus,
            tau_plus_ms=self.cfg.tau_plus_ms,
            tau_minus_ms=self.cfg.tau_minus_ms,
            w_min=self.cfg.w_min,
            w_max=self.cfg.w_max,
            tau_e_ms=self.cfg.tau_e_ms,
            eta=self.cfg.eta,
        )
        self.syn: STDPSynapse
        if self.mode == "three_factor":
            self.syn = EligibilitySynapse(8, stdp_cfg, w_init=self.cfg.w_init)
        else:
            self.syn = STDPSynapse(8, stdp_cfg, w_init=self.cfg.w_init)

        # 初始异质性
        jitter = self.cfg.w_jitter
        self.syn.w *= 1.0 + jitter * self.rng.uniform(-1.0, 1.0, size=8)
        self.syn.w = np.clip(self.syn.w, self.cfg.w_min, self.cfg.w_max)
        self.w_initial = self.syn.w.copy()

        self.scaler = HomeostaticScaler(
            self.syn.w,
            HomeostasisConfig(
                target_rate_hz=self.cfg.target_rate_hz,
                alpha=self.cfg.hs_alpha,
                w_min=self.cfg.hs_w_min,
                w_max=self.cfg.hs_w_max,
                rate_floor_hz=1.0,
            ),
        )
        self.use_homeostasis = (
            self.cfg.homeostasis_enabled
            and self.mode in ("stdp", "three_factor")
            and "no_hs" not in condition
        )
        self.last_hs_t = 0.0

        self.spike_hist: deque[float] = deque()
        self.tick_t_ms = 0.0
        self.fb_kind: str | None = None
        self.fb_until_ms = 0.0
        self.rest_until_ms = 0.0
        self.traces: list[tuple] = []
        self._rate_smooth = 0.0

    # ------------------------------------------------------------------
    # 感觉 / 反馈事件
    # ------------------------------------------------------------------

    def _sensory_events(self):
        """返回 (times_abs, channels, weights)；rest 期间为空。"""
        times, channels, weights = [], [], []
        if self.tick_t_ms < self.rest_until_ms:
            return times, channels, weights

        x = self.env.ball_x
        y = self.env.ball_y
        rate_factor = self.cfg.rate_min_hz + (
            self.cfg.rate_max_hz - self.cfg.rate_min_hz
        ) * (1.0 - x)
        tick_s = self.cfg.tick_ms / 1000.0

        for i in range(8):
            g = np.exp(-0.5 * ((y - (i + 1.0)) / self.cfg.place_sigma_bins) ** 2)
            rate = rate_factor * g
            n = self.rng.poisson(rate * tick_s)
            for _ in range(n):
                times.append(self.tick_t_ms + self.rng.uniform(0.0, self.cfg.tick_ms))
                channels.append(i)
                weights.append(self.cfg.syn_weight_nS * self.syn.w[i])
        return times, channels, weights

    def _feedback_events(self):
        times, channels, weights = [], [], []
        if self.fb_kind is None or self.tick_t_ms >= self.fb_until_ms:
            return times, channels, weights

        tick_s = self.cfg.tick_ms / 1000.0
        if self.fb_kind == "predictable":
            for i in range(8):
                times.append(self.tick_t_ms + self.rng.uniform(0.0, self.cfg.tick_ms))
                channels.append(i)
                weights.append(self.cfg.predictable_weight_nS)
        elif self.fb_kind == "unpredictable":
            for i in range(8):
                n = self.rng.poisson(self.cfg.unpredictable_rate_hz * tick_s)
                for _ in range(n):
                    times.append(self.tick_t_ms + self.rng.uniform(0.0, self.cfg.tick_ms))
                    channels.append(i)
                    weights.append(self.cfg.unpredictable_weight_nS)
        return times, channels, weights

    def _schedule_predictable(self):
        self.fb_kind = "predictable"
        self.fb_until_ms = self.tick_t_ms + self.cfg.predictable_duration_ms

    def _schedule_unpredictable(self, with_rest=True):
        self.fb_kind = "unpredictable"
        self.fb_until_ms = self.tick_t_ms + self.cfg.unpredictable_duration_s * 1000.0
        if with_rest:
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
    # 可塑性
    # ------------------------------------------------------------------

    def _process_plasticity(self, pre_times, pre_channels, post_times, reward_d, reward_t):
        if self.mode == "none":
            return

        events = []
        for t, ch in zip(pre_times, pre_channels):
            events.append((float(t), "pre", int(ch)))
        for t in post_times:
            events.append((float(t), "post", -1))
        if self.mode == "three_factor" and reward_d != 0.0:
            events.append((float(reward_t), "reward", 0))
        events.sort(key=lambda x: x[0])

        for t, kind, ch in events:
            if kind == "pre":
                self.syn.pre_spike(ch, t)
            elif kind == "post":
                self.syn.post_spike(t)
            elif kind == "reward":
                self.syn.reward(t, reward_d)

    def _apply_homeostasis(self):
        if not self.use_homeostasis:
            return
        if self.tick_t_ms - self.last_hs_t < self.cfg.hs_interval_s * 1000.0:
            return
        self.last_hs_t = self.tick_t_ms
        rate = len(self.spike_hist) / (self.cfg.readout_window_ms / 1000.0)
        # 先同步当前 STDP 权重，再做乘性缩放
        self.scaler.weights = self.syn.w.copy()
        self.scaler.scale(rate)
        self.syn.w = self.scaler.weights.copy()

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------

    def run(self) -> tuple[dict, np.ndarray]:
        n_ticks = int(round(self.cfg.duration_s * 1000.0 / self.cfg.tick_ms))
        window_ms = self.cfg.readout_window_ms

        for _ in range(n_ticks):
            t = self.tick_t_ms

            # 1) 感觉事件
            s_times, s_ch, s_w = self._sensory_events()
            # 2) 反馈事件（驱动细胞，但不进入 STDP 资格迹）
            f_times, f_ch, f_w = self._feedback_events()

            all_times = s_times + f_times
            all_ch = s_ch + f_ch
            all_w = s_w + f_w

            # 3) 块内精确事件仿真
            new_spikes = self.cell.run_events(
                self.cfg.tick_ms,
                event_times_rel_ms=[x - t for x in all_times],
                event_channels=all_ch,
                event_weights=all_w,
                tau_syn_ms=self.cfg.syn_tau_ms,
                E_syn_mV=self.cfg.E_syn_mV,
            )
            for sp in new_spikes:
                self.spike_hist.append(float(sp))

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

            # 4) 动作与环境
            # rest 期间暂停整个游戏（球与球拍都冻结）。旧实现只冻结球拍、
            # 让球继续前进，会在每次 miss 时不断延长 rest，导致永久休息态。
            if t < self.rest_until_ms:
                velocity = 0.0
                event = None
            else:
                velocity = self._action(rate_used)
                event = self.env.step(self.cfg.tick_ms / 1000.0, velocity)

            # 5) 反馈调度 + 全局调制信号
            reward_d = 0.0
            if event == "hit":
                if self.feedback_mode == "full":
                    self._schedule_predictable()
                if self.mode == "three_factor" and self.feedback_mode == "full":
                    reward_d = self.cfg.reward_plus
            elif event == "miss":
                if self.feedback_mode == "full":
                    self._schedule_unpredictable()
                elif self.feedback_mode == "silent":
                    self._schedule_rest()
                if self.mode == "three_factor" and self.feedback_mode == "full":
                    reward_d = self.cfg.reward_minus

            # shuffled 对照：随机时间给刺激，D=0
            if (
                self.feedback_mode == "shuffled"
                and self.fb_kind is None
                and t >= self.fb_until_ms
                and self.rng.random() < self.cfg.shuffle_rate_hz * self.cfg.tick_ms / 1000.0
            ):
                if self.rng.random() < 0.5:
                    self._schedule_predictable()
                else:
                    self._schedule_unpredictable()

            # 6) 可塑性更新（pre/post 按精确时间排序；reward 在 tick 末）
            self._process_plasticity(
                s_times,
                s_ch,
                new_spikes,
                reward_d,
                reward_t=t + self.cfg.tick_ms,
            )

            # 7) 稳态
            self._apply_homeostasis()

            # 8) 记录
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
                    float(np.mean(self.syn.w)),
                    float(np.min(self.syn.w)),
                    float(np.max(self.syn.w)),
                    reward_d,
                )
            )
            self.tick_t_ms += self.cfg.tick_ms

        self.env.finalize()
        trace = np.array(self.traces, dtype=object)

        w_final = self.syn.w.copy()
        w_delta = w_final - self.w_initial
        # 通道序号与最终权重的相关（是否形成 y 梯度）
        if np.std(w_final) > 0 and np.std(np.arange(8)) > 0:
            w_r = float(np.corrcoef(np.arange(8), w_final)[0, 1])
        else:
            w_r = 0.0
        if np.std(self.w_initial) > 0 and np.std(np.arange(8)) > 0:
            w0_r = float(np.corrcoef(np.arange(8), self.w_initial)[0, 1])
        else:
            w0_r = 0.0

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
            "w_initial_mean": float(np.mean(self.w_initial)),
            "w_final_mean": float(np.mean(w_final)),
            "w_final_std": float(np.std(w_final)),
            "w_delta_mean": float(np.mean(w_delta)),
            "w_delta_absmean": float(np.mean(np.abs(w_delta))),
            "w_channel_corr": w_r,
            "w_initial_channel_corr": w0_r,
            "n_rewards": int(np.sum(trace[:, 12] != 0)) if len(trace) else 0,
        }
        return metrics, trace
