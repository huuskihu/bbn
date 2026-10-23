"""
稳态突触缩放（Turrigiano 机制）。

规则：
    ratio = r_target / max(r_avg, floor)
    w <- clip(w * ratio^alpha, w_min, w_max)

生理对应：
    神经元通过 Ca2+ 依赖传感器检测自身平均放电率，乘性调节兴奋性突触强度，
    使放电率回到目标范围。它是负反馈稳定器，不是奖励信号。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class HomeostasisConfig:
    target_rate_hz: float = 20.0
    alpha: float = 0.1
    w_min: float = 2.0
    w_max: float = 40.0
    rate_floor_hz: float = 1.0
    # v0.17.0：功能带目标（带内不缩放）。use_band=False 时行为与旧版逐位一致。
    use_band: bool = False
    band_low_hz: float = 5.0
    band_high_hz: float = 30.0


class HomeostaticScaler:
    def __init__(self, weights: np.ndarray, cfg: HomeostasisConfig | None = None):
        self.cfg = cfg or HomeostasisConfig()
        self.weights = np.asarray(weights, dtype=np.float64).copy()

    def scale(self, rate_hz: float) -> float:
        """按当前平均放电率缩放权重；返回缩放因子。"""
        r = max(float(rate_hz), self.cfg.rate_floor_hz)
        if self.cfg.use_band:
            low = self.cfg.band_low_hz
            high = self.cfg.band_high_hz
            if low <= r <= high:
                return 1.0
            target = low if r < low else high
        else:
            target = self.cfg.target_rate_hz
        factor = (target / r) ** self.cfg.alpha
        self.weights = np.clip(
            self.weights * factor, self.cfg.w_min, self.cfg.w_max
        )
        return float(factor)
