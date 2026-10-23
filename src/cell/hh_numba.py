"""
Numba 加速的 Pospischil RS 单房室 HH 细胞。

目的：
    Brian 2 的 numpy target 约 25× 慢于实时，阶段 1/3 的闭环会长到不可接受。
    这里用 Numba JIT 实现**同一组方程**，作为生产引擎；Brian 2 版本保留为
    参考实现（Phase 0 已用 Brian 2 验证过基线）。

单位：
    v: mV, m/h/n/p: 1, g: nS, C: pF, I: pA, t: ms

数值：
    RK4，dt 默认 0.01 ms。比 Brian 2 的 exponential_euler(dt=0.025 ms) 更稳，
    用于 spike 这种快变量。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from numba import njit


# ---------------------------------------------------------------------------
# 参数
# ---------------------------------------------------------------------------


@dataclass
class HHParams:
    """Pospischil RS 的 Tier 0 参数（与 config/cell_pospischil_rs.yaml 对齐）。"""

    C_m: float = 290.0       # pF
    g_L: float = 29.0        # nS
    E_L: float = -70.0       # mV
    g_Na: float = 14500.0    # nS
    E_Na: float = 50.0       # mV
    g_K: float = 1450.0      # nS
    E_K: float = -100.0      # mV
    g_M: float = 20.3        # nS
    V_T: float = -55.0       # mV
    tau_max: float = 1000.0  # ms


# ---------------------------------------------------------------------------
# Numba 核心
# ---------------------------------------------------------------------------


@njit(cache=False)
def vtrap(x: float, y: float) -> float:
    """NEURON vtrap 的稳定实现。"""
    z = x / y
    if abs(z) < 1e-6:
        return y * (1.0 - z / 2.0)
    if z > 50.0:
        return 0.0
    if z < -50.0:
        return -x
    return x / (math.exp(z) - 1.0)


@njit(cache=False)
def rates(v: float, V_T: float, tau_max: float):
    """返回 m_inf, tau_m, h_inf, tau_h, n_inf, tau_n, p_inf, tau_p（时间单位 ms）。"""
    v2 = v - V_T

    a_m = 0.32 * vtrap(13.0 - v2, 4.0)
    b_m = 0.28 * vtrap(v2 - 40.0, 5.0)
    tau_m = 1.0 / (a_m + b_m)
    m_inf = a_m / (a_m + b_m)

    a_h = 0.128 * math.exp((17.0 - v2) / 18.0)
    b_h = 4.0 / (1.0 + math.exp((40.0 - v2) / 5.0))
    tau_h = 1.0 / (a_h + b_h)
    h_inf = a_h / (a_h + b_h)

    a_n = 0.032 * vtrap(15.0 - v2, 5.0)
    b_n = 0.5 * math.exp((10.0 - v2) / 40.0)
    tau_n = 1.0 / (a_n + b_n)
    n_inf = a_n / (a_n + b_n)

    p_inf = 1.0 / (1.0 + math.exp(-(v + 35.0) / 10.0))
    tau_p = tau_max / (
        3.3 * math.exp((v + 35.0) / 20.0) + math.exp(-(v + 35.0) / 20.0)
    )

    return m_inf, tau_m, h_inf, tau_h, n_inf, tau_n, p_inf, tau_p


@njit(cache=False)
def _deriv(
    v,
    m,
    h,
    n,
    p,
    I_syn,
    I_inj,
    C_m,
    g_L,
    E_L,
    g_Na,
    E_Na,
    g_K,
    E_K,
    g_M,
    V_T,
    tau_max,
):
    m_inf, tau_m, h_inf, tau_h, n_inf, tau_n, p_inf, tau_p = rates(v, V_T, tau_max)

    I_Na = g_Na * m * m * m * h * (v - E_Na)
    I_K = g_K * n * n * n * n * (v - E_K)
    I_M = g_M * p * (v - E_K)
    I_L = g_L * (v - E_L)

    dv = (I_inj - I_Na - I_K - I_M - I_L - I_syn) / C_m
    dm = (m_inf - m) / tau_m
    dh = (h_inf - h) / tau_h
    dn = (n_inf - n) / tau_n
    dp = (p_inf - p) / tau_p

    return dv, dm, dh, dn, dp


@njit(cache=False)
def _rk4_step(
    v,
    m,
    h,
    n,
    p,
    I_syn,
    I_inj,
    dt,
    C_m,
    g_L,
    E_L,
    g_Na,
    E_Na,
    g_K,
    E_K,
    g_M,
    V_T,
    tau_max,
):
    k1v, k1m, k1h, k1n, k1p = _deriv(
        v, m, h, n, p, I_syn, I_inj,
        C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
    )
    k2v, k2m, k2h, k2n, k2p = _deriv(
        v + 0.5 * dt * k1v,
        m + 0.5 * dt * k1m,
        h + 0.5 * dt * k1h,
        n + 0.5 * dt * k1n,
        p + 0.5 * dt * k1p,
        I_syn, I_inj,
        C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
    )
    k3v, k3m, k3h, k3n, k3p = _deriv(
        v + 0.5 * dt * k2v,
        m + 0.5 * dt * k2m,
        h + 0.5 * dt * k2h,
        n + 0.5 * dt * k2n,
        p + 0.5 * dt * k2p,
        I_syn, I_inj,
        C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
    )
    k4v, k4m, k4h, k4n, k4p = _deriv(
        v + dt * k3v,
        m + dt * k3m,
        h + dt * k3h,
        n + dt * k3n,
        p + dt * k3p,
        I_syn, I_inj,
        C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
    )

    v = v + dt / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
    m = m + dt / 6.0 * (k1m + 2.0 * k2m + 2.0 * k3m + k4m)
    h = h + dt / 6.0 * (k1h + 2.0 * k2h + 2.0 * k3h + k4h)
    n = n + dt / 6.0 * (k1n + 2.0 * k2n + 2.0 * k3n + k4n)
    p = p + dt / 6.0 * (k1p + 2.0 * k2p + 2.0 * k3p + k4p)

    return v, m, h, n, p


@njit(cache=False)
def run_spikes(
    v,
    m,
    h,
    n,
    p,
    g_syn,
    t0,
    n_steps,
    dt,
    I_inj,
    C_m,
    g_L,
    E_L,
    g_Na,
    E_Na,
    g_K,
    E_K,
    g_M,
    V_T,
    tau_max,
    tau_syn,
    E_syn,
    spike_times,
    spike_count,
    refractory_steps,
    g_inh,
    tau_inh,
    E_inh,
):
    """带 spike 检测/重置的 block 仿真；返回更新后的状态和 spike 计数。"""
    ref = 0
    decay = math.exp(-dt / tau_syn)
    decay_inh = math.exp(-dt / tau_inh)

    for step in range(n_steps):
        g_total = 0.0
        for i in range(g_syn.shape[0]):
            g_total += g_syn[i]
        I_syn = g_total * (v - E_syn) + g_inh * (v - E_inh)

        v_old = v
        v, m, h, n, p = _rk4_step(
            v, m, h, n, p, I_syn, I_inj, dt,
            C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
        )

        for i in range(g_syn.shape[0]):
            g_syn[i] *= decay
        g_inh *= decay_inh

        if ref > 0:
            ref -= 1
        elif v_old < 0.0 and v >= 0.0:
            if spike_count < spike_times.shape[0]:
                spike_times[spike_count] = t0 + (step + 1) * dt
            spike_count += 1
            v = -70.0
            ref = refractory_steps

    return v, m, h, n, p, g_syn, spike_count, g_inh


@njit(cache=False)
def run_events(
    v,
    m,
    h,
    n,
    p,
    g_syn,
    t0,
    n_steps,
    dt,
    I_inj,
    C_m,
    g_L,
    E_L,
    g_Na,
    E_Na,
    g_K,
    E_K,
    g_M,
    V_T,
    tau_max,
    tau_syn,
    E_syn,
    event_steps,
    event_channels,
    event_weights,
    spike_times,
    spike_count,
    refractory_steps,
    g_inh,
    tau_inh,
    E_inh,
    inh_event_steps,
    inh_event_weights,
):
    """带块内精确突触事件的仿真；event_steps 必须按升序排列。

    g_syn 为兴奋性电导（E_syn），g_inh 为抑制性电导（E_inh）。
    inh_event_steps/weights 为抑制性事件的块内步数与权重（nS）。
    """
    ref = 0
    decay = math.exp(-dt / tau_syn)
    decay_inh = math.exp(-dt / tau_inh)
    ev_idx = 0
    n_events = event_steps.shape[0]
    inh_idx = 0
    n_inh = inh_event_steps.shape[0]

    for step in range(n_steps):
        # 在 RK4 之前施加本步的突触事件（阶跃电导）
        while ev_idx < n_events and event_steps[ev_idx] == step:
            g_syn[event_channels[ev_idx]] += event_weights[ev_idx]
            ev_idx += 1
        while inh_idx < n_inh and inh_event_steps[inh_idx] == step:
            g_inh += inh_event_weights[inh_idx]
            inh_idx += 1

        g_total = 0.0
        for i in range(g_syn.shape[0]):
            g_total += g_syn[i]
        I_syn = g_total * (v - E_syn) + g_inh * (v - E_inh)

        v_old = v
        v, m, h, n, p = _rk4_step(
            v, m, h, n, p, I_syn, I_inj, dt,
            C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
        )

        for i in range(g_syn.shape[0]):
            g_syn[i] *= decay
        g_inh *= decay_inh

        if ref > 0:
            ref -= 1
        elif v_old < 0.0 and v >= 0.0:
            if spike_count < spike_times.shape[0]:
                spike_times[spike_count] = t0 + (step + 1) * dt
            spike_count += 1
            v = -70.0
            ref = refractory_steps

    return v, m, h, n, p, g_syn, spike_count, g_inh


@njit(cache=False)
def run_record(
    v,
    m,
    h,
    n,
    p,
    g_syn,
    n_steps,
    dt,
    I_inj,
    C_m,
    g_L,
    E_L,
    g_Na,
    E_Na,
    g_K,
    E_K,
    g_M,
    V_T,
    tau_max,
    tau_syn,
    E_syn,
    v_trace,
    record_stride,
    g_inh,
    tau_inh,
    E_inh,
):
    """无 spike 重置，记录 v；用于波形验证。"""
    decay = math.exp(-dt / tau_syn)
    decay_inh = math.exp(-dt / tau_inh)
    idx = 0
    for step in range(n_steps):
        g_total = 0.0
        for i in range(g_syn.shape[0]):
            g_total += g_syn[i]
        I_syn = g_total * (v - E_syn) + g_inh * (v - E_inh)

        v, m, h, n, p = _rk4_step(
            v, m, h, n, p, I_syn, I_inj, dt,
            C_m, g_L, E_L, g_Na, E_Na, g_K, E_K, g_M, V_T, tau_max,
        )

        for i in range(g_syn.shape[0]):
            g_syn[i] *= decay
        g_inh *= decay_inh

        if step % record_stride == 0:
            if idx < v_trace.shape[0]:
                v_trace[idx] = v
            idx += 1

    return v, m, h, n, p, g_syn, g_inh


# ---------------------------------------------------------------------------
# Python 包装
# ---------------------------------------------------------------------------


class FastHH:
    """单细胞快速引擎；状态显式保存，便于 checkpoint。"""

    def __init__(self, params: HHParams | None = None, dt_ms: float = 0.01, n_channels: int = 8):
        self.p = params or HHParams()
        self.dt = float(dt_ms)
        self.n_channels = int(n_channels)
        self.spike_capacity = 500_000
        self.reset()

    def reset(self):
        m0, _, h0, _, n0, _, p0, _ = rates(-70.0, self.p.V_T, self.p.tau_max)
        self.v = -70.0
        self.m = m0
        self.h = h0
        self.n = n0
        self.p_var = p0
        self.g_syn = np.zeros(self.n_channels, dtype=np.float64)
        self.g_inh = 0.0
        self.tau_inh_ms = 10.0
        self.E_inh_mV = -80.0
        self.t_ms = 0.0
        self.spike_times = np.zeros(self.spike_capacity, dtype=np.float64)
        self.spike_count = 0

    def add_syn(self, increments):
        self.g_syn += np.asarray(increments, dtype=np.float64)

    def run(self, duration_ms: float, I_inj_nA: float = 0.0, tau_syn_ms: float = 5.0, E_syn_mV: float = 0.0):
        n_steps = int(round(duration_ms / self.dt))
        refractory_steps = int(round(2.0 / self.dt))
        before = self.spike_count
        self.v, self.m, self.h, self.n, self.p_var, self.g_syn, self.spike_count, self.g_inh = run_spikes(
            self.v,
            self.m,
            self.h,
            self.n,
            self.p_var,
            self.g_syn,
            self.t_ms,
            n_steps,
            self.dt,
            I_inj_nA * 1000.0,
            self.p.C_m,
            self.p.g_L,
            self.p.E_L,
            self.p.g_Na,
            self.p.E_Na,
            self.p.g_K,
            self.p.E_K,
            self.p.g_M,
            self.p.V_T,
            self.p.tau_max,
            tau_syn_ms,
            E_syn_mV,
            self.spike_times,
            self.spike_count,
            refractory_steps,
            self.g_inh,
            self.tau_inh_ms,
            self.E_inh_mV,
        )
        self.t_ms += duration_ms
        return self.spike_times[before : self.spike_count].copy()

    def run_events(
        self,
        duration_ms: float,
        event_times_rel_ms=None,
        event_channels=None,
        event_weights=None,
        I_inj_nA: float = 0.0,
        tau_syn_ms: float = 5.0,
        E_syn_mV: float = 0.0,
        inh_event_times_rel_ms=None,
        inh_event_weights=None,
        tau_inh_ms: float | None = None,
        E_inh_mV: float | None = None,
    ):
        """块内精确突触事件；时间相对于本 block 起点（ms）。

        inh_event_* 为抑制性事件（标量电导，加到 g_inh）；默认无。
        """
        n_steps = int(round(duration_ms / self.dt))

        if event_times_rel_ms is None or len(event_times_rel_ms) == 0:
            steps = np.zeros(0, dtype=np.int64)
            chans = np.zeros(0, dtype=np.int64)
            weights = np.zeros(0, dtype=np.float64)
        else:
            times = np.asarray(event_times_rel_ms, dtype=np.float64)
            steps = np.clip((times / self.dt).astype(np.int64), 0, n_steps - 1)
            chans = np.asarray(event_channels, dtype=np.int64)
            weights = np.asarray(event_weights, dtype=np.float64)
            order = np.argsort(steps)
            steps = steps[order]
            chans = chans[order]
            weights = weights[order]

        if inh_event_times_rel_ms is None or len(inh_event_times_rel_ms) == 0:
            inh_steps = np.zeros(0, dtype=np.int64)
            inh_weights = np.zeros(0, dtype=np.float64)
        else:
            inh_times = np.asarray(inh_event_times_rel_ms, dtype=np.float64)
            inh_steps = np.clip((inh_times / self.dt).astype(np.int64), 0, n_steps - 1)
            inh_weights = np.asarray(inh_event_weights, dtype=np.float64)
            order = np.argsort(inh_steps)
            inh_steps = inh_steps[order]
            inh_weights = inh_weights[order]

        tau_inh = self.tau_inh_ms if tau_inh_ms is None else float(tau_inh_ms)
        E_inh = self.E_inh_mV if E_inh_mV is None else float(E_inh_mV)

        before = self.spike_count
        refractory_steps = int(round(2.0 / self.dt))
        (
            self.v,
            self.m,
            self.h,
            self.n,
            self.p_var,
            self.g_syn,
            self.spike_count,
            self.g_inh,
        ) = run_events(
            self.v,
            self.m,
            self.h,
            self.n,
            self.p_var,
            self.g_syn,
            self.t_ms,
            n_steps,
            self.dt,
            I_inj_nA * 1000.0,
            self.p.C_m,
            self.p.g_L,
            self.p.E_L,
            self.p.g_Na,
            self.p.E_Na,
            self.p.g_K,
            self.p.E_K,
            self.p.g_M,
            self.p.V_T,
            self.p.tau_max,
            tau_syn_ms,
            E_syn_mV,
            steps,
            chans,
            weights,
            self.spike_times,
            self.spike_count,
            refractory_steps,
            self.g_inh,
            tau_inh,
            E_inh,
            inh_steps,
            inh_weights,
        )
        self.t_ms += duration_ms
        return self.spike_times[before : self.spike_count].copy()

    def run_record(self, duration_ms: float, I_inj_nA: float = 0.0, record_stride: int = 1):
        n_steps = int(round(duration_ms / self.dt))
        n_rec = n_steps // record_stride + 2
        v_trace = np.zeros(n_rec, dtype=np.float64)
        self.v, self.m, self.h, self.n, self.p_var, self.g_syn, self.g_inh = run_record(
            self.v,
            self.m,
            self.h,
            self.n,
            self.p_var,
            self.g_syn,
            n_steps,
            self.dt,
            I_inj_nA * 1000.0,
            self.p.C_m,
            self.p.g_L,
            self.p.E_L,
            self.p.g_Na,
            self.p.E_Na,
            self.p.g_K,
            self.p.E_K,
            self.p.g_M,
            self.p.V_T,
            self.p.tau_max,
            5.0,
            0.0,
            v_trace,
            record_stride,
            self.g_inh,
            self.tau_inh_ms,
            self.E_inh_mV,
        )
        self.t_ms += duration_ms
        return v_trace[: min(n_rec, n_steps // record_stride + 1)]
