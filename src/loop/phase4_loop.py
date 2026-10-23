"""
阶段 4：两池差分读出（push-pull）。

结构：
    up 池 / down 池，各自是一个 Pospischil RS 细胞。两个池接收**同一组**感觉
    事件时间与同一套反馈刺激（相当于同一输入纤维支配两个细胞），但各自持有
    独立的 STDP / 资格迹权重和稳态缩放器。

读出：
    v_paddle = clip(k * (rate_up - rate_down), ±v_max)

    共同的距离驱动（ball_x）和共同的感觉/反馈刺激在差分中抵消，只剩两个池对
    ball_y 的差异响应。Phase 1/3 的瓶颈正是单细胞率几乎不携带 ball_y。

条件：
    phase4_pushpull_3b       : 反对称初始权重 + 资格迹三因子 + 稳态
    phase4_pushpull_3b_no_hs : 同上，关闭稳态（消融）
    phase4_pushpull_static   : 反对称初始权重，无可塑性
    phase4_random_3b         : 独立随机初始权重 + 三因子 + 稳态
    phase4_symmetric_static  : 两池权重完全相同，无可塑性（差分恒为 0 对照）
    phase4_random_paddle     : 忽略细胞输出

注意：
    - 反对称初始权重 w_up = 1 + span*x, w_down = 1 - span*x, x=(ch-4.5)/3.5；
      这给了 push-pull 一个先验的 y 方向，因此 pushpull_static 本身就可能显著
      好于 random_paddle。plasticity 的增益必须相对 *static* 来评估。
    - 不调参凑曲线；负结果如实记录。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from src.cell.hh_numba import FastHH, HHParams
from src.env.pong import PongConfig, PongEnv
from src.plasticity.homeostasis import HomeostasisConfig, HomeostaticScaler
from src.plasticity.stdp import EligibilitySynapse, STDPConfig
from src.loop.phase3_loop import Phase3Config


@dataclass
class Phase4Config(Phase3Config):
    # 两池初始权重
    pushpull_span: float = 0.2       # w_up/w_down 相对 1.0 的最大偏移
    random_init_jitter: float = 0.2  # random_3b 的独立均匀扰动幅度

    # 记录
    snapshot_interval_s: float = 1.0

    # 抑制性中间神经元（v0.10.0 共享；v0.11.0 交叉）
    inhibitory_enabled: bool = False
    inh_input_weight: float = 1.0   # 共享模式：I 细胞感觉权重（相对 syn_weight_nS）
    inh_weight_nS: float = 10.0     # 每个 I spike 投递到 motor 池的抑制电导
    inh_tau_ms: float = 10.0
    E_inh_mV: float = -80.0
    # 交叉抑制（v0.11.0）：up→I_up→down，down→I_down→up；10 ms 环路延迟
    cross_inhibition_enabled: bool = False
    cross_rec_weight_nS: float = 40.0
    cross_rec_tau_ms: float = 5.0
    # 差分调谐抑制（v0.12.0）：I 接收 8 通道感觉，按 push-pull 权重调谐
    tuned_inhibition_enabled: bool = False
    tuned_inh_gain: float = 1.0
    # 归一化读出（v0.14.0）：v = k_norm·(up−down)/(up+down+eps)
    normalized_readout: bool = False
    velocity_gain_norm: float = 5.0
    norm_eps_hz: float = 1e-3
    # 背景自发活动（v0.15.0）：每个 motor 池独立 Poisson 事件，play/rest 都存在
    bg_noise_hz: float = 3.0
    bg_noise_weight_nS: float = 40.0
    # 局部信用分配（v0.16.0）由条件名（含 "local"）选择，见 Phase4Loop.__init__
    # 动态稳态目标带（v0.17.0）：由条件名（含 "dyn"）选择；仅 play 期应用
    hs_target_low_hz: float = 5.0
    hs_target_high_hz: float = 30.0
    # 短时程突触可塑性（v0.18.0）：由条件名（含 "stp"）选择；仅感觉事件
    stp_u: float = 0.4
    stp_tau_rec_ms: float = 200.0
    stp_tau_fac_ms: float = 1000.0
    # 10 细胞 E/I 前馈网络（v0.19.0）：由条件名（含 "net"）选择
    # 校准（2026-10-23，30 s × 3 seeds，按存活准则）：g_S→E=40 nS（E 15.4/15.0 Hz），
    # g_E→M=40 nS（play motor 14.1 Hz，最接近 17.5 Hz 的预注册网格点）
    net_se_weight_nS: float = 40.0   # S spike → E/I（校准后冻结）
    net_em_weight_nS: float = 40.0   # E spike → motor（校准后冻结）
    net_sigma_bins: float = 1.5       # S 细胞高斯调谐宽度
    # PD 读出（v0.20.0）：由条件名（含 "pd"）选择；τ_pred 预注册为 50 ms
    pd_tau_ms: float = 50.0
    # 帧式延迟编码（v0.21.0）：由条件名（含 "lat"）选择
    lat_frame_ms: float = 100.0
    lat_max_ms: float = 100.0
    lat_gain: float = 1.0   # bins/s per ms；6a 校准后冻结
    # 递归 E-I 网络（v0.22.0）：由条件名（含 "rec"）选择
    rec_w_se_nS: float = 20.0
    rec_w_ee_nS: float = 0.0    # 7a 校准
    rec_w_ei_nS: float = 20.0
    rec_g_ie_nS: float = 10.0
    rec_bg_hz: float = 3.0
    rec_bg_weight_nS: float = 80.0
    rec_w_em_nS: float = 5.0   # 8 E × ~15 Hz ≈ 20 Hz × 40 nS 的等效输入


class _Pool:
    """一个 motor 池：细胞 + 可塑突触 + 稳态 + 自己的读出窗口。"""

    def __init__(
        self,
        cell: FastHH,
        syn: EligibilitySynapse,
        scaler: HomeostaticScaler,
        use_homeostasis: bool,
    ):
        self.cell = cell
        self.syn = syn
        self.scaler = scaler
        self.use_homeostasis = bool(use_homeostasis)
        self.spike_hist: deque[float] = deque()
        self.rate_smooth = 0.0
        self.w_initial = syn.w.copy()
        self.last_hs_t = 0.0
        # 短时程状态（每通道独立的突触前终末；u=利用率，R=可用资源）
        self.stp_u = np.full(8, 0.4, dtype=float)
        self.stp_r = np.ones(8, dtype=float)
        self.stp_t = np.zeros(8, dtype=float)


class Phase4Loop:
    def __init__(
        self,
        condition: str,
        cfg: Phase4Config | None = None,
        cell_params: HHParams | None = None,
        pong_cfg: PongConfig | None = None,
        seed: int = 0,
    ):
        self.cfg = cfg or Phase4Config()
        self.condition = condition
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        # 背景噪声用每个池独立的 RNG，避免改变感觉/环境随机流，也避免两池共享背景事件
        self.bg_rngs = [
            np.random.default_rng(seed + 10_000_000),
            np.random.default_rng(seed + 20_000_000),
        ]

        # 条件解析
        self.mode = "three_factor" if "3b" in condition else "none"
        # 信用分配由条件名决定（v0.16.0）：含 "local" 才用池特异 D。
        # 若用全局开关，同一批次里非 local 的对照臂会被静默污染。
        self.local_credit = "local" in condition
        self.feedback_mode = "none" if condition == "random_paddle" else "full"
        self.use_homeostasis = (
            self.cfg.homeostasis_enabled
            and self.mode == "three_factor"
            and "no_hs" not in condition
        )
        # 机制对照：只在游戏进行时施加稳态。rest 是无刺激的人工超时，
        # 若在此期间也按 20 Hz 目标缩放，细胞沉默会触发权重的乘性上调，
        # 数秒内推到 w_max，抹平两池差异（60 s 内 up/down 权重会完全相同）。
        # v0.17.0：dyn 条件把目标改成 [5,30] Hz 功能带，且同样只在 play 期应用。
        self.hs_dynamic = "dyn" in condition
        self.hs_play_only = "play_hs" in condition or self.hs_dynamic
        # v0.18.0：短时程可塑性按条件名启用，只作用于感觉事件
        self.stp_enabled = "stp" in condition
        # v0.19.0：10 细胞 E/I 前馈网络按条件名启用
        self.net_mode = "net" in condition
        # v0.20.0：PD 读出按条件名启用（τ_pred 固定）
        self.pd_enabled = "pd" in condition
        self.prev_rate_diff = 0.0
        self.deriv_smooth = 0.0
        # v0.21.0：帧式延迟编码；frozen 表示只测量读出、冻结球拍（6a 开环）
        self.lat_mode = "lat" in condition
        self.frozen_action = "frozen" in condition
        self.pending_sensory: list[tuple[float, int]] = []
        self.frame_first: list[float | None] = [None, None]
        self.lat_delta = 0.0
        self.lat_trace: list[tuple] = []
        # v0.22.0：递归 E-I 网络
        self.rec_mode = "rec" in condition
        self.rec_s_cells: list[FastHH] = []
        self.rec_e_cells: list[FastHH] = []
        self.rec_i_cells: list[FastHH] = []
        self.rec_e_hist: list[list[float]] = []
        self.rec_i_hist: list[list[float]] = []
        self.rec_e_counts: list[np.ndarray] = []
        self.rec_i_counts: list[np.ndarray] = []
        self.prev_rec_e = [np.zeros(0, dtype=float) for _ in range(8)]
        self.prev_rec_i = [np.zeros(0, dtype=float) for _ in range(8)]
        self.rec_w_se = np.zeros((4, 8), dtype=float)

        if "pushpull" in condition:
            self.init_mode = "pushpull"
        elif "symmetric" in condition:
            self.init_mode = "symmetric"
        elif condition == "random_paddle":
            self.init_mode = "symmetric"
        else:
            self.init_mode = "random"

        self.cell_params = cell_params or HHParams()
        self.pong_cfg = pong_cfg or PongConfig()
        self.env = PongEnv(self.pong_cfg, rng=self.rng)

        self.stdp_cfg = STDPConfig(
            a_plus=self.cfg.a_plus,
            a_minus=self.cfg.a_minus,
            tau_plus_ms=self.cfg.tau_plus_ms,
            tau_minus_ms=self.cfg.tau_minus_ms,
            w_min=self.cfg.w_min,
            w_max=self.cfg.w_max,
            tau_e_ms=self.cfg.tau_e_ms,
            eta=self.cfg.eta,
        )

        self.pools = [self._make_pool() for _ in range(2)]
        self._init_weights()

        # 抑制性网络：none / shared（v0.10.0）/ cross（v0.11.0）/ tuned（v0.12.0）
        # v0.19.0：net_i 使用 10 细胞网络自带的 I 细胞（I_up→down，I_down→up）
        if self.net_mode:
            self.inhibition_mode = "net_i"
        elif self.cfg.tuned_inhibition_enabled:
            self.inhibition_mode = "tuned"
        elif self.cfg.cross_inhibition_enabled:
            self.inhibition_mode = "cross"
        elif self.cfg.inhibitory_enabled:
            self.inhibition_mode = "shared"
        else:
            self.inhibition_mode = "none"
        self.inhibitory = self.inhibition_mode != "none"

        self.inh_cell: FastHH | None = None
        self.inh_w = np.zeros(0, dtype=float)
        self.inh_spike_hist: deque[float] = deque()
        self.inh_rate_smooth = 0.0
        self.inh_cells: list[FastHH] = []
        self.inh_spike_hists: list[deque] = []
        self.inh_rates = [0.0, 0.0]
        self.inh_up_counts: list[int] = []
        self.inh_down_counts: list[int] = []
        self.tuned_inh_w: list[np.ndarray] = []
        self.prev_inh_spikes = [np.zeros(0, dtype=float), np.zeros(0, dtype=float)]

        if self.inhibition_mode == "shared":
            self.inh_cell = FastHH(
                params=self.cell_params, dt_ms=0.01, n_channels=8
            )
            self.inh_cell.tau_inh_ms = self.cfg.inh_tau_ms
            self.inh_cell.E_inh_mV = self.cfg.E_inh_mV
            self.inh_w = np.full(8, self.cfg.inh_input_weight, dtype=float)
        elif self.inhibition_mode == "cross":
            for _ in range(2):
                cell = FastHH(params=self.cell_params, dt_ms=0.01, n_channels=1)
                cell.tau_inh_ms = self.cfg.inh_tau_ms
                cell.E_inh_mV = self.cfg.E_inh_mV
                self.inh_cells.append(cell)
                self.inh_spike_hists.append(deque())
        elif self.inhibition_mode == "tuned":
            # 与 motor 初始 push-pull 权重一致：I_up: 1+0.2x, I_down: 1-0.2x
            x = (np.arange(1.0, 9.0) - 4.5) / 3.5
            self.tuned_inh_w = [
                self.cfg.tuned_inh_gain * (1.0 + self.cfg.pushpull_span * x),
                self.cfg.tuned_inh_gain * (1.0 - self.cfg.pushpull_span * x),
            ]
            for _ in range(2):
                cell = FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
                cell.tau_inh_ms = self.cfg.inh_tau_ms
                cell.E_inh_mV = self.cfg.E_inh_mV
                self.inh_cells.append(cell)
                self.inh_spike_hists.append(deque())

        # v0.19.0：10 细胞 E/I 前馈网络（S1–S4 → E1/E2 + I1/I2 → motor）
        self.s_cells: list[FastHH] = []
        self.e_cells: list[FastHH] = []
        self.i_cells: list[FastHH] = []
        self.e_spike_hists: list[deque] = []
        self.net_s_tuning = np.zeros((4, 8), dtype=float)
        self.net_e_w = [np.ones(4), np.ones(4)]
        self.net_i_w = [np.ones(4), np.ones(4)]
        self.e_rates = [0.0, 0.0]
        self.i_rates = [0.0, 0.0]
        self.net_rates = {"s": [0.0] * 4, "e": [0.0, 0.0], "i": [0.0, 0.0]}
        if self.net_mode:
            for _ in range(4):
                self.s_cells.append(
                    FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
                )
            for _ in range(2):
                self.e_cells.append(
                    FastHH(params=self.cell_params, dt_ms=0.01, n_channels=4)
                )
            for _ in range(2):
                cell = FastHH(params=self.cell_params, dt_ms=0.01, n_channels=4)
                cell.tau_inh_ms = self.cfg.inh_tau_ms
                cell.E_inh_mV = self.cfg.E_inh_mV
                self.i_cells.append(cell)
            centers = [1.5, 3.5, 5.5, 7.5]
            for k, mu in enumerate(centers):
                g = np.exp(
                    -0.5
                    * ((np.arange(1.0, 9.0) - mu) / self.cfg.net_sigma_bins) ** 2
                )
                self.net_s_tuning[k] = g / g.max()
            x = (np.arange(4.0) - 1.5) / 1.5
            self.net_e_w = [
                1.0 + self.cfg.pushpull_span * x,
                1.0 - self.cfg.pushpull_span * x,
            ]
            self.net_i_w = [
                1.0 - self.cfg.pushpull_span * x,
                1.0 + self.cfg.pushpull_span * x,
            ]
            for _ in range(2):
                self.e_spike_hists.append(deque())
                self.inh_spike_hists.append(deque())

        # v0.22.0：递归 E-I（4 S → 8 E ↔ 8 I → 2 motor）
        if self.rec_mode:
            for _ in range(4):
                self.rec_s_cells.append(
                    FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
                )
            for _ in range(8):
                self.rec_e_cells.append(
                    FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
                )
            for _ in range(8):
                cell = FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
                cell.tau_inh_ms = self.cfg.inh_tau_ms
                cell.E_inh_mV = self.cfg.E_inh_mV
                self.rec_i_cells.append(cell)
            centers = [1.5, 3.5, 5.5, 7.5]
            for k, mu in enumerate(centers):
                g = np.exp(
                    -0.5 * ((np.arange(1.0, 9.0) - mu) / self.cfg.net_sigma_bins) ** 2
                )
                self.net_s_tuning[k] = g / g.max()
            e_centers = np.arange(1.0, 9.0)
            for s in range(4):
                for k in range(8):
                    self.rec_w_se[s, k] = self.cfg.rec_w_se_nS * np.exp(
                        -0.5 * ((e_centers[k] - centers[s]) / self.cfg.net_sigma_bins) ** 2
                    )
            self.rec_e_hist = [[] for _ in range(8)]
            self.rec_i_hist = [[] for _ in range(8)]
            self.rec_bg_rngs = [
                np.random.default_rng(self.seed + 30_000_000 + j)
                for j in range(16)
            ]

        self.tick_t_ms = 0.0
        self.fb_kind: str | None = None
        self.fb_until_ms = 0.0
        self.rest_until_ms = 0.0

        self.traces: list[tuple] = []
        self.impacts: list[tuple] = []
        self.weight_snapshots: list[tuple] = []
        self.recent: deque[tuple] = deque(maxlen=30)  # 300 ms @ 10 ms tick
        self.quiet_rest_rates: list[float] = []
        self._next_snapshot_t = 0.0

    # ------------------------------------------------------------------
    # 构造 / 初始化
    # ------------------------------------------------------------------

    def _make_pool(self) -> _Pool:
        cell = FastHH(params=self.cell_params, dt_ms=0.01, n_channels=8)
        syn = EligibilitySynapse(8, self.stdp_cfg, w_init=self.cfg.w_init)
        scaler = HomeostaticScaler(
            syn.w,
            HomeostasisConfig(
                target_rate_hz=self.cfg.target_rate_hz,
                alpha=self.cfg.hs_alpha,
                w_min=self.cfg.hs_w_min,
                w_max=self.cfg.hs_w_max,
                rate_floor_hz=1.0,
                use_band=self.hs_dynamic,
                band_low_hz=self.cfg.hs_target_low_hz,
                band_high_hz=self.cfg.hs_target_high_hz,
            ),
        )
        pool = _Pool(cell, syn, scaler, self.use_homeostasis)
        pool.stp_u = np.full(8, self.cfg.stp_u, dtype=float)
        return pool

    def _init_weights(self):
        x = (np.arange(1.0, 9.0) - 4.5) / 3.5  # [-1, +1]
        if self.net_mode:
            # 只有通道 0/1 参与（E_up / E_down）；其余置为 w_init 且永不更新
            w_up = np.full(8, self.cfg.w_init, dtype=float)
            w_down = np.full(8, self.cfg.w_init, dtype=float)
            s = self.cfg.pushpull_span
            w_up[0], w_up[1] = self.cfg.w_init + s, self.cfg.w_init - s
            w_down[0], w_down[1] = self.cfg.w_init - s, self.cfg.w_init + s
        elif self.rec_mode or self.init_mode == "pushpull":
            w_up = self.cfg.w_init + self.cfg.pushpull_span * x
            w_down = self.cfg.w_init - self.cfg.pushpull_span * x
        elif self.init_mode == "symmetric":
            w_up = np.full(8, self.cfg.w_init, dtype=float)
            w_down = np.full(8, self.cfg.w_init, dtype=float)
        else:
            j = self.cfg.random_init_jitter
            w_up = self.cfg.w_init + j * self.rng.uniform(-1.0, 1.0, size=8)
            w_down = self.cfg.w_init + j * self.rng.uniform(-1.0, 1.0, size=8)
        for pool, w in zip(self.pools, (w_up, w_down)):
            pool.syn.w = np.clip(w, self.cfg.w_min, self.cfg.w_max)
            pool.scaler.weights = pool.syn.w.copy()
            pool.w_initial = pool.syn.w.copy()

    # ------------------------------------------------------------------
    # 感觉 / 反馈事件
    # ------------------------------------------------------------------

    def _sensory_events(self):
        """两池共享的事件时间与通道；权重在仿真前按各池 w 计算。"""
        times, channels = [], []
        if self.tick_t_ms < self.rest_until_ms:
            return times, channels

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
        return times, channels

    def _rec_background(self, idx: int, t: float):
        """递归网络的独立背景 Poisson 事件（v0.22.0）。"""
        rng = self.rec_bg_rngs[idx]
        tick_s = self.cfg.tick_ms / 1000.0
        n = rng.poisson(self.cfg.rec_bg_hz * tick_s)
        times = [t + rng.uniform(0.0, self.cfg.tick_ms) for _ in range(n)]
        return times, [self.cfg.rec_bg_weight_nS] * n

    def _queue_latency_volley(self, t: float):
        """帧式延迟编码（v0.21.0）：每帧 8 通道各 1 个事件，延迟由 ball_y 决定。

        事件按绝对到达时间进入 pending 队列；可能在本帧后续 tick 甚至下一帧到达，
        因此时间分辨率不受 10 ms tick 限制。rest 期不发 volley。
        """
        if t < self.rest_until_ms:
            return
        y = self.env.ball_y
        for i in range(8):
            delay = self.cfg.lat_max_ms * abs((i + 1.0) - y) / 7.5
            self.pending_sensory.append((t + delay, i))

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

    def _background_events(self, t: float, pool_idx: int):
        """指定池独立抽取的本 tick 背景事件；时间为绝对时间。"""
        times, channels, weights = [], [], []
        if self.cfg.bg_noise_hz <= 0.0:
            return times, channels, weights
        rng = self.bg_rngs[pool_idx]
        tick_s = self.cfg.tick_ms / 1000.0
        n = rng.poisson(self.cfg.bg_noise_hz * tick_s)
        for _ in range(n):
            times.append(t + rng.uniform(0.0, self.cfg.tick_ms))
            channels.append(0)
            weights.append(self.cfg.bg_noise_weight_nS)
        return times, channels, weights

    def _stp_sensory_weights(self, pool: _Pool, times, channels):
        """Tsodyks–Markram 短时程可塑性：返回每个感觉事件的有效电导（v0.18.0）。

        每个通道是独立的突触前终末，按各自的事件间隔更新 u/R。
        电导除以 U 归一化，使低频（间隔 ≫ τ）时的效力等于基线 w·g0，
        因此只有高频段才出现疲劳，不会整体削弱输入。
        """
        cfg = self.cfg
        out = [0.0] * len(times)
        by_ch: dict[int, list[tuple[float, int]]] = {}
        for k, (tt, ch) in enumerate(zip(times, channels)):
            by_ch.setdefault(int(ch), []).append((float(tt), k))

        for ch, items in by_ch.items():
            items.sort(key=lambda x: x[0])
            u = float(pool.stp_u[ch])
            r = float(pool.stp_r[ch])
            last = float(pool.stp_t[ch])
            for tt, k in items:
                dt = max(0.0, tt - last)
                if dt > 0.0:
                    u = cfg.stp_u + (u - cfg.stp_u) * np.exp(
                        -dt / cfg.stp_tau_fac_ms
                    )
                    r = 1.0 + (r - 1.0) * np.exp(-dt / cfg.stp_tau_rec_ms)
                release = u * r / cfg.stp_u
                out[k] = cfg.syn_weight_nS * pool.syn.w[ch] * release
                r *= (1.0 - u)
                u += cfg.stp_u * (1.0 - u)
                last = tt
            pool.stp_u[ch] = u
            pool.stp_r[ch] = r
            pool.stp_t[ch] = last
        return out

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
    # 动作 / 可塑性
    # ------------------------------------------------------------------

    def _action(self, rate_diff_hz: float, rate_sum_hz: float, lat_delta_ms: float = 0.0) -> float:
        if self.condition == "random_paddle":
            return float(self.rng.uniform(-self.cfg.max_velocity, self.cfg.max_velocity))
        if self.lat_mode:
            v = self.cfg.lat_gain * lat_delta_ms
        elif self.cfg.normalized_readout:
            v = self.cfg.velocity_gain_norm * rate_diff_hz / max(
                rate_sum_hz, self.cfg.norm_eps_hz
            )
        elif self.pd_enabled:
            # v = Kp·Δr + Kp·τ_pred·dΔr/dt（微分已同 α 低通）
            v = self.cfg.velocity_gain * (
                rate_diff_hz
                + (self.cfg.pd_tau_ms / 1000.0) * self.deriv_smooth
            )
        else:
            v = self.cfg.velocity_gain * rate_diff_hz
        return float(np.clip(v, -self.cfg.max_velocity, self.cfg.max_velocity))

    def _process_plasticity(self, pool: _Pool, pre_times, pre_channels, post_times, reward_d):
        if self.mode == "none" or reward_d is None:
            return

        events = []
        for t, ch in zip(pre_times, pre_channels):
            events.append((float(t), "pre", int(ch)))
        for t in post_times:
            events.append((float(t), "post", -1))
        if reward_d != 0.0:
            events.append((float(self.tick_t_ms + self.cfg.tick_ms), "reward", 0))
        events.sort(key=lambda x: x[0])

        for t, kind, ch in events:
            if kind == "pre":
                pool.syn.pre_spike(ch, t)
            elif kind == "post":
                pool.syn.post_spike(t)
            else:
                pool.syn.reward(t, reward_d)

    def _apply_homeostasis(self, pool: _Pool, playing: bool):
        if not pool.use_homeostasis:
            return
        if self.hs_play_only and not playing:
            return
        if self.tick_t_ms - pool.last_hs_t < self.cfg.hs_interval_s * 1000.0:
            return
        pool.last_hs_t = self.tick_t_ms
        rate = len(pool.spike_hist) / (self.cfg.readout_window_ms / 1000.0)
        pool.scaler.weights = pool.syn.w.copy()
        pool.scaler.scale(rate)
        pool.syn.w = pool.scaler.weights.copy()

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------

    def run(self) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
        n_ticks = int(round(self.cfg.duration_s * 1000.0 / self.cfg.tick_ms))
        window_ms = self.cfg.readout_window_ms
        alpha = self.cfg.rate_smoothing
        snapshot_every = max(1, int(round(
            self.cfg.snapshot_interval_s * 1000.0 / self.cfg.tick_ms
        )))
        self._next_snapshot_t = 0.0

        for tick_idx in range(n_ticks):
            t = self.tick_t_ms
            # 每 tick 显式初始化，保证关闭抑制时也有确定值
            inh_spikes = np.zeros(0, dtype=float)
            inh_rate_used = 0.0

            # 1) 共享的感觉事件（时间/通道）
            if self.lat_mode:
                frame_ms = self.cfg.lat_frame_ms
                if int(round(t)) % int(round(frame_ms)) == 0:
                    self._queue_latency_volley(t)
                    self.frame_first = [None, None]
                horizon = t + self.cfg.tick_ms
                delivered = [e for e in self.pending_sensory if e[0] < horizon - 1e-9]
                self.pending_sensory = [
                    e for e in self.pending_sensory if e[0] >= horizon - 1e-9
                ]
                s_times = [e[0] for e in delivered]
                s_ch = [e[1] for e in delivered]
            else:
                s_times, s_ch = self._sensory_events()
            # 2) 共享的反馈事件（时间/通道/权重）
            f_times, f_ch, f_w = self._feedback_events()

            all_times = s_times + f_times
            all_ch = s_ch + f_ch

            # 2a) 10 细胞 E/I 前馈网络（v0.19.0）：S → E/I
            s_spikes_all: list[np.ndarray] = []
            e_spikes_all: list[np.ndarray] = []
            i_spikes_all: list[np.ndarray] = []
            e_times_all: list[float] = []
            e_ch_all: list[int] = []
            if self.net_mode:
                for k, cell in enumerate(self.s_cells):
                    w_s = [
                        self.cfg.syn_weight_nS * self.net_s_tuning[k][ch]
                        for ch in s_ch
                    ]
                    s_spikes_all.append(
                        cell.run_events(
                            self.cfg.tick_ms,
                            event_times_rel_ms=[x - t for x in s_times],
                            event_channels=s_ch,
                            event_weights=w_s,
                            tau_syn_ms=self.cfg.syn_tau_ms,
                            E_syn_mV=self.cfg.E_syn_mV,
                        )
                    )
                s_in_times = [float(x) for sp in s_spikes_all for x in sp]
                s_in_ch = [k for k, sp in enumerate(s_spikes_all) for _ in sp]
                for j in range(2):
                    e_spikes_all.append(
                        self.e_cells[j].run_events(
                            self.cfg.tick_ms,
                            event_times_rel_ms=[x - t for x in s_in_times],
                            event_channels=s_in_ch,
                            event_weights=[
                                self.cfg.net_se_weight_nS * self.net_e_w[j][k]
                                for k in s_in_ch
                            ],
                            tau_syn_ms=self.cfg.syn_tau_ms,
                            E_syn_mV=self.cfg.E_syn_mV,
                        )
                    )
                for j in range(2):
                    i_spikes_all.append(
                        self.i_cells[j].run_events(
                            self.cfg.tick_ms,
                            event_times_rel_ms=[x - t for x in s_in_times],
                            event_channels=s_in_ch,
                            event_weights=[
                                self.cfg.net_se_weight_nS * self.net_i_w[j][k]
                                for k in s_in_ch
                            ],
                            tau_syn_ms=self.cfg.syn_tau_ms,
                            E_syn_mV=self.cfg.E_syn_mV,
                        )
                    )
                e_times_all = [float(x) for sp in e_spikes_all for x in sp]
                e_ch_all = [j for j, sp in enumerate(e_spikes_all) for _ in sp]
            # 2a-rec) 22 细胞递归 E-I（v0.22.0，用户已授权 §6T）：S → 8E ↔ 8I → motor
            elif self.rec_mode:
                # S 细胞：接收原始感觉事件（8 通道高斯调谐）
                for s_idx, cell in enumerate(self.rec_s_cells):
                    w_s = [
                        self.cfg.syn_weight_nS * self.net_s_tuning[s_idx][ch]
                        for ch in s_ch
                    ]
                    s_spikes_all.append(
                        cell.run_events(
                            self.cfg.tick_ms,
                            event_times_rel_ms=[x - t for x in s_times],
                            event_channels=s_ch,
                            event_weights=w_s,
                            tau_syn_ms=self.cfg.syn_tau_ms,
                            E_syn_mV=self.cfg.E_syn_mV,
                        )
                    )
                # E 细胞：S（本 tick）+ 其它 E（上一 tick，无自连）+ I（上一 tick，抑制）+ 背景
                # 必须在循环前快照上一 tick 的 E/I spike：否则 e_idx 递增时
                # prev_rec_e[pre_idx] 对已运行的 pre_idx 已被本 tick 覆盖，
                # 递归会退化成零延迟，破坏 §6T 的“上一 tick”约定。
                prev_e_snap = [np.asarray(a, dtype=float).copy() for a in self.prev_rec_e]
                prev_i_snap = [np.asarray(a, dtype=float).copy() for a in self.prev_rec_i]
                for e_idx in range(8):
                    ev_t: list[float] = []
                    ev_ch: list[int] = []
                    ev_w: list[float] = []
                    # S → E（固定 rec_w_se）
                    for s_idx, sp in enumerate(s_spikes_all):
                        for x in sp:
                            ev_t.append(float(x - t))
                            ev_ch.append(e_idx)
                            ev_w.append(float(self.rec_w_se[s_idx, e_idx]))
                    # E → E（上一 tick，不含自身）
                    for pre_idx in range(8):
                        if pre_idx == e_idx:
                            continue
                        for x in prev_e_snap[pre_idx]:
                            ev_t.append(float(x - t + self.cfg.tick_ms))
                            ev_ch.append(e_idx)
                            ev_w.append(self.cfg.rec_w_ee_nS)
                    # 独立背景 Poisson
                    bg_t, bg_w = self._rec_background(e_idx, t)
                    for x, w in zip(bg_t, bg_w):
                        ev_t.append(float(x - t))
                        ev_ch.append(e_idx)
                        ev_w.append(float(w))
                    # I → E 抑制（上一 tick）
                    inh_rel = [
                        float(x - t + self.cfg.tick_ms)
                        for x in prev_i_snap[e_idx]
                    ]
                    spikes_e = self.rec_e_cells[e_idx].run_events(
                        self.cfg.tick_ms,
                        event_times_rel_ms=ev_t,
                        event_channels=ev_ch,
                        event_weights=ev_w,
                        tau_syn_ms=self.cfg.syn_tau_ms,
                        E_syn_mV=self.cfg.E_syn_mV,
                        inh_event_times_rel_ms=inh_rel,
                        inh_event_weights=[self.cfg.rec_g_ie_nS] * len(inh_rel),
                        tau_inh_ms=self.cfg.inh_tau_ms,
                        E_inh_mV=self.cfg.E_inh_mV,
                    )
                    self.prev_rec_e[e_idx] = np.asarray(spikes_e, dtype=float)
                    for x in spikes_e:
                        self.rec_e_hist[e_idx].append(float(x))
                        e_times_all.append(float(x))
                        e_ch_all.append(e_idx)
                    e_spikes_all.append(spikes_e)
                # I 细胞：E（本 tick，固定 w_ei）+ 背景
                for i_idx in range(8):
                    ev_t_i: list[float] = []
                    ev_ch_i: list[int] = []
                    ev_w_i: list[float] = []
                    for x in e_spikes_all[i_idx]:
                        ev_t_i.append(float(x - t))
                        ev_ch_i.append(i_idx)
                        ev_w_i.append(self.cfg.rec_w_ei_nS)
                    bg_t, bg_w = self._rec_background(8 + i_idx, t)
                    for x, w in zip(bg_t, bg_w):
                        ev_t_i.append(float(x - t))
                        ev_ch_i.append(i_idx)
                        ev_w_i.append(float(w))
                    spikes_i = self.rec_i_cells[i_idx].run_events(
                        self.cfg.tick_ms,
                        event_times_rel_ms=ev_t_i,
                        event_channels=ev_ch_i,
                        event_weights=ev_w_i,
                        tau_syn_ms=self.cfg.syn_tau_ms,
                        E_syn_mV=self.cfg.E_syn_mV,
                    )
                    self.prev_rec_i[i_idx] = np.asarray(spikes_i, dtype=float)
                    for x in spikes_i:
                        self.rec_i_hist[i_idx].append(float(x))
                    i_spikes_all.append(spikes_i)

            # 2b) 抑制网络
            # shared（v0.10.0）：I 接收与 motor 相同的感觉/反馈，同 tick 抑制两池；
            # cross（v0.11.0）：tick k 的 motor spike 驱动 I，I 在 tick k+1 抑制对侧；
            # tuned（v0.12.0）：I_up/I_down 只接收感觉事件，按 push-pull 权重调谐，
            # 同 tick 交叉抑制对侧 motor。
            inh_spikes = np.zeros(0, dtype=float)
            new_inh_spikes: list[np.ndarray] = []
            if self.net_mode:
                new_inh_spikes = list(i_spikes_all)
                inh_spikes = (
                    np.concatenate(i_spikes_all)
                    if i_spikes_all else np.zeros(0, dtype=float)
                )
            elif self.inhibition_mode == "shared":
                inh_weights = [
                    self.cfg.syn_weight_nS * self.inh_w[ch] for ch in s_ch
                ] + f_w
                inh_spikes = self.inh_cell.run_events(
                    self.cfg.tick_ms,
                    event_times_rel_ms=[x - t for x in all_times],
                    event_channels=all_ch,
                    event_weights=inh_weights,
                    tau_syn_ms=self.cfg.syn_tau_ms,
                    E_syn_mV=self.cfg.E_syn_mV,
                )
            elif self.inhibition_mode == "tuned":
                for j in range(2):
                    w_j = self.tuned_inh_w[j]
                    weights_j = [
                        self.cfg.syn_weight_nS * w_j[ch] for ch in s_ch
                    ]
                    spikes_j = self.inh_cells[j].run_events(
                        self.cfg.tick_ms,
                        event_times_rel_ms=[x - t for x in s_times],
                        event_channels=s_ch,
                        event_weights=weights_j,
                        tau_syn_ms=self.cfg.syn_tau_ms,
                        E_syn_mV=0.0,
                    )
                    new_inh_spikes.append(spikes_j)
                if new_inh_spikes:
                    inh_spikes = np.concatenate(new_inh_spikes)

            new_spikes = []
            for idx, pool in enumerate(self.pools):
                if self.net_mode:
                    # motor 只接收 E spike（可塑权重）+ 反馈；不再直接接收感觉事件
                    weights = [
                        self.cfg.net_em_weight_nS * pool.syn.w[ch]
                        for ch in e_ch_all
                    ] + f_w
                    base_times = e_times_all + f_times
                    base_ch = e_ch_all + f_ch
                elif self.rec_mode:
                    # v0.22.0：motor 只接收 8 个 E 细胞的 spike（8 通道可塑权重）+ 反馈
                    weights = [
                        self.cfg.rec_w_em_nS * pool.syn.w[ch]
                        for ch in e_ch_all
                    ] + f_w
                    base_times = e_times_all + f_times
                    base_ch = e_ch_all + f_ch
                else:
                    if self.stp_enabled:
                        s_weights = self._stp_sensory_weights(pool, s_times, s_ch)
                    else:
                        s_weights = [
                            self.cfg.syn_weight_nS * pool.syn.w[ch] for ch in s_ch
                        ]
                    weights = s_weights + f_w
                    base_times = all_times
                    base_ch = all_ch
                # 每个池独立背景事件（play/rest 都存在；独立 RNG 流）
                bg_t, bg_ch, bg_w = self._background_events(t, idx)
                ev_times = base_times + bg_t
                ev_ch = base_ch + bg_ch
                ev_weights = weights + bg_w
                if self.inhibition_mode == "shared":
                    inh_times_rel = [float(x - t) for x in inh_spikes]
                elif self.inhibition_mode == "cross":
                    # up (idx=0) 接收 I_down (idx=1)；down 接收 I_up；10 ms 延迟
                    src = self.prev_inh_spikes[1 - idx]
                    inh_times_rel = [
                        float(x + self.cfg.tick_ms - t) for x in src
                    ]
                elif self.inhibition_mode == "tuned":
                    # up 接收 I_down；down 接收 I_up；同 tick
                    src = new_inh_spikes[1 - idx]
                    inh_times_rel = [float(x - t) for x in src]
                elif self.inhibition_mode == "net_i":
                    # I_up (0) → down；I_down (1) → up；同 tick
                    src = new_inh_spikes[1 - idx]
                    inh_times_rel = [float(x - t) for x in src]
                else:
                    inh_times_rel = []
                spikes = pool.cell.run_events(
                    self.cfg.tick_ms,
                    event_times_rel_ms=[x - t for x in ev_times],
                    event_channels=ev_ch,
                    event_weights=ev_weights,
                    tau_syn_ms=self.cfg.syn_tau_ms,
                    E_syn_mV=self.cfg.E_syn_mV,
                    inh_event_times_rel_ms=inh_times_rel,
                    inh_event_weights=[self.cfg.inh_weight_nS] * len(inh_times_rel),
                    tau_inh_ms=self.cfg.inh_tau_ms,
                    E_inh_mV=self.cfg.E_inh_mV,
                )
                new_spikes.append(spikes)

            # v0.21.0：帧内首脉冲延迟差（ms，相对帧起点）
            if self.lat_mode:
                for j, sp in enumerate(new_spikes):
                    if len(sp) and self.frame_first[j] is None:
                        self.frame_first[j] = float(np.min(sp))
                frame_start = t - (t % self.cfg.lat_frame_ms)
                lat_up = (
                    self.frame_first[0] - frame_start
                    if self.frame_first[0] is not None
                    else self.cfg.lat_frame_ms
                )
                lat_down = (
                    self.frame_first[1] - frame_start
                    if self.frame_first[1] is not None
                    else self.cfg.lat_frame_ms
                )
                self.lat_delta = float(lat_down - lat_up)

            # cross：motor spike → 对应 I 细胞（当前 tick），供下一 tick 使用
            if self.inhibition_mode == "cross":
                for j, motor_spikes in enumerate(new_spikes):
                    rec_times = [float(x - t) for x in motor_spikes]
                    spikes = self.inh_cells[j].run_events(
                        self.cfg.tick_ms,
                        event_times_rel_ms=rec_times,
                        event_channels=[0] * len(rec_times),
                        event_weights=[self.cfg.cross_rec_weight_nS]
                        * len(rec_times),
                        tau_syn_ms=self.cfg.cross_rec_tau_ms,
                        E_syn_mV=0.0,
                    )
                    new_inh_spikes.append(spikes)
                self.prev_inh_spikes = [
                    np.asarray(sp, dtype=float) for sp in new_inh_spikes
                ]
                if new_inh_spikes:
                    inh_spikes = np.concatenate(new_inh_spikes)

            # 3) 各自的放电率（先原始窗口，再平滑）
            rates_raw = []
            t_cut = t + self.cfg.tick_ms - window_ms
            for pool, spikes in zip(self.pools, new_spikes):
                for sp in spikes:
                    pool.spike_hist.append(float(sp))
                while pool.spike_hist and pool.spike_hist[0] < t_cut:
                    pool.spike_hist.popleft()
                rate_hz = len(pool.spike_hist) / (window_ms / 1000.0)
                rates_raw.append(rate_hz)
                if alpha > 0:
                    pool.rate_smooth = (1.0 - alpha) * pool.rate_smooth + alpha * rate_hz
                else:
                    pool.rate_smooth = rate_hz

            up, down = self.pools
            rate_diff_raw = rates_raw[0] - rates_raw[1]
            rate_diff_used = up.rate_smooth - down.rate_smooth

            # v0.20.0：PD 的微分状态每 tick 更新（rest 期也更新，避免恢复时假脉冲）
            if self.pd_enabled:
                raw_deriv = (
                    rate_diff_used - self.prev_rate_diff
                ) / (self.cfg.tick_ms / 1000.0)
                self.deriv_smooth = (
                    (1.0 - alpha) * self.deriv_smooth + alpha * raw_deriv
                )
                self.prev_rate_diff = rate_diff_used

            # 3b) I 细胞的读出窗口（仅用于指标，不参与动作）
            inh_up_rate_used = 0.0
            inh_down_rate_used = 0.0
            if self.inhibition_mode == "shared":
                for sp in inh_spikes:
                    self.inh_spike_hist.append(float(sp))
                while self.inh_spike_hist and self.inh_spike_hist[0] < t_cut:
                    self.inh_spike_hist.popleft()
                inh_rate_hz = len(self.inh_spike_hist) / (window_ms / 1000.0)
                if alpha > 0:
                    self.inh_rate_smooth = (
                        (1.0 - alpha) * self.inh_rate_smooth + alpha * inh_rate_hz
                    )
                else:
                    self.inh_rate_smooth = inh_rate_hz
                inh_rate_used = self.inh_rate_smooth
                inh_up_rate_used = inh_rate_used
            elif self.inhibition_mode in ("cross", "tuned", "net_i"):
                rates_i = []
                for j in range(2):
                    hist = self.inh_spike_hists[j]
                    for sp in new_inh_spikes[j]:
                        hist.append(float(sp))
                    while hist and hist[0] < t_cut:
                        hist.popleft()
                    rate_j = len(hist) / (window_ms / 1000.0)
                    if alpha > 0:
                        self.inh_rates[j] = (
                            (1.0 - alpha) * self.inh_rates[j] + alpha * rate_j
                        )
                    else:
                        self.inh_rates[j] = rate_j
                    rates_i.append(self.inh_rates[j])
                inh_up_rate_used, inh_down_rate_used = rates_i
                inh_rate_hz = 0.5 * (rates_i[0] + rates_i[1])
                inh_rate_used = inh_rate_hz
            else:
                inh_rate_hz = 0.0
                inh_rate_used = 0.0

            # 每 tick 的 I_up/I_down spike 计数（用于差分调谐指标）
            if self.inhibition_mode == "shared":
                self.inh_up_counts.append(len(inh_spikes))
                self.inh_down_counts.append(0)
            elif self.inhibition_mode in ("cross", "tuned", "net_i"):
                self.inh_up_counts.append(len(new_inh_spikes[0]))
                self.inh_down_counts.append(len(new_inh_spikes[1]))
            else:
                self.inh_up_counts.append(0)
                self.inh_down_counts.append(0)

            # v0.19.0：E 细胞放电率（H1 存活检查）
            if self.net_mode:
                for j in range(2):
                    hist = self.e_spike_hists[j]
                    for sp in e_spikes_all[j]:
                        hist.append(float(sp))
                    while hist and hist[0] < t_cut:
                        hist.popleft()
                    rate_j = len(hist) / (window_ms / 1000.0)
                    if alpha > 0:
                        self.e_rates[j] = (
                            (1.0 - alpha) * self.e_rates[j] + alpha * rate_j
                        )
                    else:
                        self.e_rates[j] = rate_j

            # 4) 动作与环境
            # rest 期间暂停整个游戏（球与球拍都冻结）。旧实现只冻结球拍、
            # 让球继续前进，会在每次 miss 时不断延长 rest，导致永久休息态。
            ball_y_before = self.env.ball_y
            paddle_y_before = self.env.paddle_y
            playing = t >= self.rest_until_ms
            # 安静 rest：rest 且不可预测反馈已结束（用于自发率指标）
            if (not playing) and t >= self.fb_until_ms:
                self.quiet_rest_rates.append(
                    0.5 * (up.rate_smooth + down.rate_smooth)
                )
            if not playing:
                velocity = 0.0
                event = None
            else:
                if self.frozen_action:
                    velocity = 0.0
                else:
                    velocity = self._action(
                        rate_diff_used,
                        up.rate_smooth + down.rate_smooth,
                        self.lat_delta,
                    )
                event = self.env.step(self.cfg.tick_ms / 1000.0, velocity)

            # v0.21.0：延迟差记录（6a 开环验证用）
            if self.lat_mode:
                self.lat_trace.append(
                    (
                        t,
                        self.lat_delta,
                        ball_y_before,
                        1.0 if playing else 0.0,
                        len(new_spikes[0]),
                        len(new_spikes[1]),
                    )
                )

            # 5) 冲击前读出窗口（最近 300 ms 的均值）
            self.recent.append((rate_diff_used, up.rate_smooth, down.rate_smooth))
            if event is not None:
                r = np.array(self.recent, dtype=float)
                self.impacts.append(
                    (
                        t,
                        ball_y_before,
                        float(np.mean(r[:, 0])),
                        float(np.mean(r[:, 1])),
                        float(np.mean(r[:, 2])),
                        1.0 if event == "hit" else 0.0,
                    )
                )

            # 6) 反馈调度 + 全局/局部调制
            reward_d = 0.0
            reward_up = 0.0
            reward_down = 0.0
            if event == "hit":
                if self.feedback_mode == "full":
                    self._schedule_predictable()
                if self.mode == "three_factor" and self.feedback_mode == "full":
                    reward_d = self.cfg.reward_plus
                    reward_up = reward_d
                    reward_down = reward_d
            elif event == "miss":
                if self.feedback_mode == "full":
                    self._schedule_unpredictable()
                if self.mode == "three_factor" and self.feedback_mode == "full":
                    reward_d = self.cfg.reward_minus
                    if self.local_credit:
                        # 球在上方漏掉 → Up 该负责（+），Down 抑制（−）；反之亦然
                        if ball_y_before > paddle_y_before:
                            reward_up = self.cfg.reward_plus
                            reward_down = self.cfg.reward_minus
                        else:
                            reward_up = self.cfg.reward_minus
                            reward_down = self.cfg.reward_plus
                    else:
                        reward_up = reward_d
                        reward_down = reward_d

            # 7) 每个池独立可塑性 + 稳态
            # 局部信用：Up/Down 各用自己的 D；非局部时两者都等于 reward_d
            for j, (pool, spikes) in enumerate(zip(self.pools, new_spikes)):
                d_pool = reward_up if j == 0 else reward_down
                if self.net_mode:
                    # 可塑突触的前端是 E 细胞（通道 0/1）
                    self._process_plasticity(
                        pool, e_times_all, e_ch_all, spikes, d_pool
                    )
                elif self.rec_mode:
                    # v0.22.0：可塑突触前端是 8 个 E 细胞（通道 0–7）
                    self._process_plasticity(
                        pool, e_times_all, e_ch_all, spikes, d_pool
                    )
                else:
                    self._process_plasticity(pool, s_times, s_ch, spikes, d_pool)
                self._apply_homeostasis(pool, playing)

            # 8) 权重快照（每 snapshot_interval_s）
            if t + 1e-9 >= self._next_snapshot_t:
                self.weight_snapshots.append(
                    tuple([t] + list(up.syn.w) + list(down.syn.w))
                )
                self._next_snapshot_t += self.cfg.snapshot_interval_s * 1000.0

            # 9) 记录
            self.traces.append(
                (
                    t,
                    self.env.ball_x,
                    self.env.ball_y,
                    self.env.paddle_y,
                    rates_raw[0],
                    rates_raw[1],
                    up.rate_smooth,
                    down.rate_smooth,
                    rate_diff_raw,
                    rate_diff_used,
                    velocity,
                    event if event is not None else "",
                    len(new_spikes[0]),
                    len(new_spikes[1]),
                    float(np.mean(up.syn.w)),
                    float(np.mean(down.syn.w)),
                    float(np.mean(up.syn.w - down.syn.w)),
                    reward_d,
                    1.0 if playing else 0.0,
                    len(inh_spikes) if self.inhibitory else 0,
                    inh_rate_used if self.inhibitory else 0.0,
                )
            )
            self.tick_t_ms += self.cfg.tick_ms

        self.env.finalize()
        trace = np.array(self.traces, dtype=object)
        impacts = np.array(self.impacts, dtype=float)
        weights = np.array(self.weight_snapshots, dtype=float)

        w_up0 = self.pools[0].w_initial
        w_down0 = self.pools[1].w_initial
        w_up = self.pools[0].syn.w.copy()
        w_down = self.pools[1].syn.w.copy()

        ch = np.arange(1.0, 9.0)

        def _corr(a, b):
            a = np.asarray(a, dtype=float)
            b = np.asarray(b, dtype=float)
            m = np.isfinite(a) & np.isfinite(b)
            if m.sum() < 3 or np.std(a[m]) == 0.0 or np.std(b[m]) == 0.0:
                return 0.0
            return float(np.corrcoef(a[m], b[m])[0, 1])

        rate_diff_used = trace[:, 9].astype(float)
        ball_y = trace[:, 2].astype(float)
        ball_x = trace[:, 1].astype(float)
        velocity_arr = trace[:, 10].astype(float)
        playing = trace[:, 18].astype(float) > 0.5

        up_counts = np.asarray(self.inh_up_counts, dtype=float)
        down_counts = np.asarray(self.inh_down_counts, dtype=float)
        if len(up_counts) != len(trace):
            up_counts = np.zeros(len(trace), dtype=float)
            down_counts = np.zeros(len(trace), dtype=float)

        rate_sum_arr = (
            trace[:, 6].astype(float) + trace[:, 7].astype(float)
            + self.cfg.norm_eps_hz
        )
        norm_diff = rate_diff_used / rate_sum_arr
        early_mask = playing & (ball_x > 0.5)
        late_mask = playing & (ball_x <= 0.5)
        rest_mask = ~playing
        motor_rate_arr = 0.5 * (
            trace[:, 6].astype(float) + trace[:, 7].astype(float)
        )

        if len(impacts):
            imp_y = impacts[:, 1]
            imp_diff = impacts[:, 2]
            imp_up = impacts[:, 3]
            imp_down = impacts[:, 4]
        else:
            imp_y = imp_diff = imp_up = imp_down = np.array([])

        spikes_up = trace[:, 12].astype(float)
        spikes_down = trace[:, 13].astype(float)

        inh_up_total = 0
        inh_down_total = 0
        if self.inhibition_mode == "shared":
            inh_up_total = int(self.inh_cell.spike_count)
        elif self.inhibition_mode in ("cross", "tuned", "net_i"):
            inh_up_total = int(self.inh_cells[0].spike_count) if self.inh_cells else 0
            inh_down_total = int(self.inh_cells[1].spike_count) if self.inh_cells else 0
            if self.net_mode:
                inh_up_total = int(self.i_cells[0].spike_count)
                inh_down_total = int(self.i_cells[1].spike_count)

        # net 模式只有通道 0/1 参与可塑读出；其余通道恒为 w_init
        wsel = slice(0, 2) if self.net_mode else slice(None)
        wchan = np.arange(1.0, 3.0) if self.net_mode else ch
        wu0, wd0 = w_up0[wsel], w_down0[wsel]
        wu, wd = w_up[wsel], w_down[wsel]
        play_s = max(
            float(playing.sum()) * self.cfg.tick_ms / 1000.0, 1e-9
        )

        # v0.21.0：延迟编码的读出统计（6a gate 用）
        lat_corr = 0.0
        lat_p95 = 0.0
        lat_zero = 0.0
        if self.lat_mode and len(self.lat_trace):
            lat_arr = np.asarray(self.lat_trace, dtype=float)
            lat_play = lat_arr[:, 3] > 0
            if lat_play.any():
                d_play = lat_arr[lat_play, 1]
                lat_corr = _corr(d_play, lat_arr[lat_play, 2])
                lat_p95 = float(np.percentile(np.abs(d_play), 95))
                lat_zero = float(np.mean(
                    (lat_arr[lat_play, 4] == 0) & (lat_arr[lat_play, 5] == 0)
                ))

        # v0.22.0：递归 E-I 的 7a Gate 指标（与 net_* 一致，只用 play 期；
        # rest 是人工超时，若纳入会污染放电率、ISI 的 CV 和前后半段漂移）
        rec_e_mean_rate = 0.0
        rec_e_min_rate = 0.0
        rec_e_max_rate = 0.0
        rec_i_mean_rate = 0.0
        rec_s_mean_rate = 0.0
        rec_max_cell_rate = 0.0
        rec_cv_isi = 0.0
        rec_pair_corr = 0.0
        rec_drift = 0.0
        if self.rec_mode:
            t_arr = trace[:, 0].astype(float)
            play = trace[:, 18].astype(float) > 0.5
            segs: list[tuple[float, float]] = []
            seg_start: float | None = None
            for i in range(len(play)):
                if play[i] and seg_start is None:
                    seg_start = float(t_arr[i])
                if seg_start is not None and (
                    (not play[i]) or i == len(play) - 1
                ):
                    seg_end = float(t_arr[i]) + (
                        self.cfg.tick_ms if play[i] else 0.0
                    )
                    segs.append((seg_start, seg_end))
                    seg_start = None
            play_s = max(sum(e - s for s, e in segs) / 1000.0, 1e-9)

            def _in_play(x: float) -> bool:
                return any(s <= x < e for s, e in segs)

            play_spikes = [
                [x for x in h if _in_play(x)] for h in self.rec_e_hist
            ]
            e_counts = [len(h) for h in play_spikes]
            rec_e_mean_rate = float(np.mean(e_counts) / play_s)
            rec_e_min_rate = float(np.min(e_counts) / play_s)
            rec_e_max_rate = float(np.max(e_counts) / play_s)
            i_counts = [
                sum(1 for x in h if _in_play(x)) for h in self.rec_i_hist
            ]
            rec_i_mean_rate = float(np.mean(i_counts) / play_s)
            rec_s_mean_rate = float(
                np.mean([c.spike_count for c in self.rec_s_cells]) / play_s
            )
            rec_max_cell_rate = float(
                max(max(e_counts), max(i_counts)) / play_s
            )
            # ISI 的 CV：只在 play 段内计算相邻 spike 间隔
            cvs = []
            for h in play_spikes:
                isis: list[float] = []
                for s, e in segs:
                    xs = [x for x in h if s <= x < e]
                    if len(xs) >= 3:
                        isis.extend(np.diff(np.asarray(xs, dtype=float)))
                if len(isis) >= 2:
                    isi = np.asarray(isis, dtype=float)
                    m = float(np.mean(isi))
                    if m > 0:
                        cvs.append(float(np.std(isi) / m))
            rec_cv_isi = float(np.mean(cvs)) if cvs else 0.0
            # E 细胞两两 10 ms 计数相关（只用 play 内的 bin）
            bin_ms = 10.0
            nb = int(max(1, np.floor(self.cfg.duration_s * 1000.0 / bin_ms)))
            counts_bin = np.zeros((8, nb), dtype=float)
            for j, h in enumerate(self.rec_e_hist):
                idx = np.clip(
                    (np.asarray(h, dtype=float) / bin_ms).astype(int), 0, nb - 1
                )
                if len(idx):
                    counts_bin[j] = np.bincount(idx, minlength=nb)[:nb]
            bin_t = (np.arange(nb) + 0.5) * bin_ms
            play_bins = np.array([_in_play(float(bt)) for bt in bin_t])
            corrs = []
            for a in range(8):
                for b in range(a + 1, 8):
                    xa = counts_bin[a, play_bins]
                    xb = counts_bin[b, play_bins]
                    if np.std(xa) > 0.0 and np.std(xb) > 0.0:
                        corrs.append(float(np.corrcoef(xa, xb)[0, 1]))
            rec_pair_corr = float(np.mean(corrs)) if corrs else 0.0
            # 前/后半段 E 群体率差：按累计 play 时长切分（不含 rest 间隔）
            total_play = max(sum(e - s for s, e in segs), 1e-9)
            half = total_play / 2.0
            cum = 0.0
            h1 = 0
            h2 = 0
            for s, e in segs:
                xs = [x for h in play_spikes for x in h if s <= x < e]
                dur = e - s
                if cum + dur <= half:
                    h1 += len(xs)
                elif cum >= half:
                    h2 += len(xs)
                else:
                    mid = s + (half - cum)
                    h1 += sum(1 for x in xs if x < mid)
                    h2 += sum(1 for x in xs if x >= mid)
                cum += dur
            rec_drift = abs(h2 - h1) / max(h1, 1)

        metrics = {
            "condition": self.condition,
            "seed": self.seed,
            "duration_s": self.cfg.duration_s,
            "init_mode": self.init_mode,
            "hits": self.env.hits,
            "misses": self.env.misses,
            "n_rallies": self.env.n_rallies,
            "average_rally_length": self.env.average_rally_length,
            "aces": self.env.aces,
            "long_rallies": self.env.long_rallies,
            "mean_impact_error": self.env.mean_impact_error,

            "mean_rate_up_hz": float(np.mean(trace[:, 6])),
            "mean_rate_down_hz": float(np.mean(trace[:, 7])),
            "mean_abs_rate_diff_hz": float(np.mean(np.abs(rate_diff_used))),
            "rate_diff_sd": float(np.std(rate_diff_used)),
            "play_fraction": float(np.mean(playing)),
            "play_mean_rate_up_hz": float(np.mean(trace[playing, 6]))
            if playing.any() else 0.0,
            "play_mean_rate_down_hz": float(np.mean(trace[playing, 7]))
            if playing.any() else 0.0,
            "play_mean_abs_rate_diff_hz": float(np.mean(np.abs(rate_diff_used[playing])))
            if playing.any() else 0.0,
            "play_tick_rate_diff_corr": _corr(rate_diff_used[playing], ball_y[playing])
            if playing.any() else 0.0,
            "play_tick_rate_updown_corr": _corr(
                trace[playing, 6].astype(float), trace[playing, 7].astype(float)
            ) if playing.any() else 0.0,
            "paddle_range": float(np.max(trace[:, 3]) - np.min(trace[:, 3])),
            "mean_abs_velocity": float(np.mean(np.abs(velocity_arr))),

            # 读出信息量：冲击前 300 ms 的差分率 vs 球位置
            "impact_rate_diff_corr": _corr(imp_diff, imp_y),
            "impact_rate_diff_r2": _corr(imp_diff, imp_y) ** 2,
            "impact_rate_up_corr": _corr(imp_up, imp_y),
            "impact_rate_down_corr": _corr(imp_down, imp_y),
            # 逐 tick 相关（包含休息与共同驱动，作为参考）
            "tick_rate_diff_corr": _corr(rate_diff_used, ball_y),
            "tick_rate_diff_ballx_corr": _corr(rate_diff_used, ball_x),
            "tick_velocity_bally_corr": _corr(velocity_arr, ball_y),
            "tick_rate_updown_corr": _corr(trace[:, 6].astype(float), trace[:, 7].astype(float)),
            "readout_mode": "normalized" if self.cfg.normalized_readout else "difference",
            "norm_diff_bally_corr": _corr(norm_diff[playing], ball_y[playing])
            if playing.any() else 0.0,
            "early_norm_diff_corr": _corr(norm_diff[early_mask], ball_y[early_mask])
            if early_mask.any() else 0.0,
            "late_norm_diff_corr": _corr(norm_diff[late_mask], ball_y[late_mask])
            if late_mask.any() else 0.0,

            # 两池输出关系
            "exclusive_fraction": float(np.mean(
                ((spikes_up > 0) & (spikes_down == 0))
                | ((spikes_up == 0) & (spikes_down > 0))
            )),
            "both_spike_fraction": float(np.mean((spikes_up > 0) & (spikes_down > 0))),

            # 抑制性网络（关闭时全为 0）
            # 说明：inh_up_total/inh_down_total 在本函数上方按模式计算，
            # none→(0,0)，shared→(I,0)，cross→(I_up,I_down)。
            # trace 列 19=spikes_inh（总），20=inh_rate_used（均值）。
            "inhibition_mode": self.inhibition_mode,
            "inhibitory": int(self.inhibitory),
            "local_credit": int(self.local_credit),
            "hs_mode": (
                "dynamic_band" if self.hs_dynamic
                else ("play_only" if self.hs_play_only
                      else ("point" if self.use_homeostasis else "off"))
            ),
            "stp": int(self.stp_enabled),
            "pd": int(self.pd_enabled),
            "pd_tau_ms": float(self.cfg.pd_tau_ms),
            "lat_mode": int(self.lat_mode),
            "lat_gain": float(self.cfg.lat_gain),
            "lat_delta_corr": lat_corr,
            "lat_delta_p95_abs": lat_p95,
            "lat_zero_frac": lat_zero,
            "net_mode": int(self.net_mode),
            # v0.22.0：递归 E-I（7a Gate 指标；非 rec 条件全为 0）
            "rec_mode": int(self.rec_mode),
            "rec_w_se_nS": float(self.cfg.rec_w_se_nS),
            "rec_w_ee_nS": float(self.cfg.rec_w_ee_nS),
            "rec_w_ei_nS": float(self.cfg.rec_w_ei_nS),
            "rec_g_ie_nS": float(self.cfg.rec_g_ie_nS),
            "rec_w_em_nS": float(self.cfg.rec_w_em_nS),
            "rec_e_mean_rate_hz": rec_e_mean_rate,
            "rec_e_min_rate_hz": rec_e_min_rate,
            "rec_e_max_rate_hz": rec_e_max_rate,
            "rec_i_mean_rate_hz": rec_i_mean_rate,
            "rec_s_mean_rate_hz": rec_s_mean_rate,
            "rec_max_cell_rate_hz": rec_max_cell_rate,
            "rec_e_cv_isi_mean": rec_cv_isi,
            "rec_e_pair_corr_mean": rec_pair_corr,
            "rec_e_rate_drift": rec_drift,
            "net_s_rate_hz": (
                float(np.mean([c.spike_count for c in self.s_cells]) / play_s)
                if self.net_mode else 0.0
            ),
            "net_e1_rate_hz": (
                float(self.e_cells[0].spike_count / play_s)
                if self.net_mode else 0.0
            ),
            "net_e2_rate_hz": (
                float(self.e_cells[1].spike_count / play_s)
                if self.net_mode else 0.0
            ),
            "net_i1_rate_hz": (
                float(self.i_cells[0].spike_count / play_s)
                if self.net_mode else 0.0
            ),
            "net_i2_rate_hz": (
                float(self.i_cells[1].spike_count / play_s)
                if self.net_mode else 0.0
            ),
            "inh_weight_nS": float(self.cfg.inh_weight_nS),
            "cross_rec_weight_nS": float(self.cfg.cross_rec_weight_nS),
            "tuned_inh_gain": float(self.cfg.tuned_inh_gain),
            "inh_total_spikes": inh_up_total + inh_down_total,
            "inh_up_total_spikes": inh_up_total,
            "inh_down_total_spikes": inh_down_total,
            "inh_diff_bally_corr": _corr(
                (up_counts - down_counts)[playing], ball_y[playing]
            ) if playing.any() else 0.0,
            "inh_up_down_count_corr": _corr(
                up_counts[playing], down_counts[playing]
            ) if playing.any() else 0.0,
            "inh_mean_rate_hz": float(np.mean(trace[:, 20])),
            "inh_play_rate_hz": float(np.mean(trace[playing, 20]))
            if playing.any() else 0.0,
            "motor_mean_rate_hz": float(np.mean(
                0.5 * (trace[:, 6].astype(float) + trace[:, 7].astype(float))
            )),
            "bg_noise_hz": float(self.cfg.bg_noise_hz),
            "bg_noise_weight_nS": float(self.cfg.bg_noise_weight_nS),
            "rest_motor_rate_hz": float(np.mean(motor_rate_arr[rest_mask]))
            if rest_mask.any() else 0.0,
            "quiet_rest_rate_hz": float(np.mean(self.quiet_rest_rates))
            if len(self.quiet_rest_rates) else 0.0,
            "play_motor_rate_hz": float(np.mean(motor_rate_arr[playing]))
            if playing.any() else 0.0,
            "inh_motor_rate_corr": _corr(
                trace[playing, 20].astype(float),
                0.5 * (
                    trace[playing, 6].astype(float)
                    + trace[playing, 7].astype(float)
                ),
            ) if playing.any() else 0.0,

            # 权重（net 模式只有通道 0/1 参与）
            "w_up_initial_mean": float(np.mean(wu0)),
            "w_down_initial_mean": float(np.mean(wd0)),
            "w_up_final_mean": float(np.mean(wu)),
            "w_down_final_mean": float(np.mean(wd)),
            "w_up_delta_absmean": float(np.mean(np.abs(wu - wu0))),
            "w_down_delta_absmean": float(np.mean(np.abs(wd - wd0))),
            "w_diff_channel_corr_initial": _corr(wu0 - wd0, wchan),
            "w_diff_channel_corr": _corr(wu - wd, wchan),
            "w_sum_channel_corr": _corr(wu + wd, wchan),
            "w_diff_absmean_final": float(np.mean(np.abs(wu - wd))),
            "w_up_at_max_frac": float(np.mean(wu >= self.cfg.hs_w_max - 1e-9)),
            "w_down_at_max_frac": float(np.mean(wd >= self.cfg.hs_w_max - 1e-9)),
            "w_up_final_std": float(np.std(w_up)),
            "w_down_final_std": float(np.std(w_down)),

            "total_spikes_up": int(up.cell.spike_count),
            "total_spikes_down": int(down.cell.spike_count),
            "n_rewards": int(np.sum(trace[:, 17].astype(float) != 0.0)),
        }
        return metrics, trace, impacts, weights
