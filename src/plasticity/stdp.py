"""
Pair-based STDP 与资格迹（三因子）规则。

生理对应：
    - 双相 STDP：NMDAR coincidence detector；pre-before-post -> LTP，post-before-pre -> LTD。
    - 资格迹：Ca2+/CaMKII 等局部痕迹，把毫秒级 pre-post 事件带到秒级，供延迟反馈使用。
    - 三因子：局部资格迹 × 全局神经调质信号 D(t)。

单位：时间 ms，权重无量纲（Phase 2 验证用）；Phase 3 会映射到 nS。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class STDPConfig:
    a_plus: float = 0.01
    a_minus: float = 0.012
    tau_plus_ms: float = 20.0
    tau_minus_ms: float = 20.0
    w_min: float = 0.0
    w_max: float = 1.0

    # 资格迹 / 三因子
    tau_e_ms: float = 1000.0
    eta: float = 0.1


class STDPSynapse:
    """多通道 pair-based STDP；每个通道是一个独立突触。"""

    def __init__(self, n: int, cfg: STDPConfig | None = None, w_init: float = 0.5):
        self.cfg = cfg or STDPConfig()
        self.w = np.full(n, float(w_init), dtype=np.float64)
        self.pre_trace = np.zeros(n, dtype=np.float64)
        self.post_trace = 0.0
        self.last_t = 0.0

    def _clip(self):
        self.w = np.clip(self.w, self.cfg.w_min, self.cfg.w_max)

    def _decay(self, t: float):
        dt = t - self.last_t
        if dt > 0:
            self.pre_trace *= np.exp(-dt / self.cfg.tau_plus_ms)
            self.post_trace *= np.exp(-dt / self.cfg.tau_minus_ms)
            self.last_t = t

    def pre_spike(self, i: int, t: float):
        """突触前脉冲：post-before-pre -> LTD。"""
        self._decay(t)
        self.w[i] -= self.cfg.a_minus * self.post_trace
        self.pre_trace[i] += 1.0
        self._clip()

    def post_spike(self, t: float):
        """突触后脉冲：pre-before-post -> LTP（对所有通道）。"""
        self._decay(t)
        self.w += self.cfg.a_plus * self.pre_trace
        self.post_trace += 1.0
        self._clip()

    def reset(self, w_init: float = 0.5):
        self.w[:] = w_init
        self.pre_trace[:] = 0.0
        self.post_trace = 0.0
        self.last_t = 0.0


class EligibilitySynapse(STDPSynapse):
    """STDP 事件先写入资格迹；奖励/惩罚到来时再按 D(t) 更新权重。"""

    def __init__(self, n: int, cfg: STDPConfig | None = None, w_init: float = 0.5):
        super().__init__(n, cfg, w_init)
        self.eligibility = np.zeros(n, dtype=np.float64)
        self.last_e_t = 0.0

    def _decay_e(self, t: float):
        dt = t - self.last_e_t
        if dt > 0:
            self.eligibility *= np.exp(-dt / self.cfg.tau_e_ms)
            self.last_e_t = t

    def pre_spike(self, i: int, t: float):
        self._decay(t)
        self._decay_e(t)
        self.eligibility[i] -= self.cfg.a_minus * self.post_trace
        self.pre_trace[i] += 1.0

    def post_spike(self, t: float):
        self._decay(t)
        self._decay_e(t)
        self.eligibility += self.cfg.a_plus * self.pre_trace
        self.post_trace += 1.0

    def reward(self, t: float, d: float, consume: bool = True):
        """全局调制信号 D(t)；返回本步权重变化。"""
        self._decay_e(t)
        dw = self.cfg.eta * d * self.eligibility
        self.w += dw
        self._clip()
        if consume:
            self.eligibility[:] = 0.0
        return dw.copy()

    def reset(self, w_init: float = 0.5):
        super().reset(w_init)
        self.eligibility[:] = 0.0
        self.last_e_t = 0.0
