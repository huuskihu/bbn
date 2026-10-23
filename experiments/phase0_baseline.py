r"""
阶段 0：Pospischil (2008) RS 单房室 HH 细胞的基线电生理。

运行：
    .\.venv\Scripts\python.exe experiments\phase0_baseline.py --config config\cell_pospischil_rs.yaml

输出（默认写到 results/phase0/）：
    - phase0_report.md
    - phase0_summary.json
    - fi_curve.csv
    - fig_fi_curve.png
    - fig_spike_waveform.png
    - fig_adaptation.png
    - fig_rest_rin.png

说明：
    - 模型参数来自 Pospischil et al. 2008 Fig.1 caption 与 ModelDB 123623 sPY_template。
    - 本脚本只做基线验证；不包含任何可塑性规则，也不训练。
    - 采用 Brian 2 的 threshold/reset 作为“spike 检测”；waveform 用无 threshold 的单独组记录完整波形。
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from brian2 import (
    NeuronGroup,
    SpikeMonitor,
    StateMonitor,
    Network,
    Function,
    defaultclock,
    seed,
    prefs,
    mV,
    nA,
    pA,
    pF,
    nS,
    ms,
    second,
    Hz,
)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def vtrap_py(x, y):
    """NEURON 的 vtrap，向量化版本：在 x/y 接近 0 时用 Taylor 展开。

    注意：这里直接处理 numpy 数组，配合 auto_vectorise=False 使用，
    比逐元素 np.vectorize 快很多。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = x / y
    exact = x / (np.exp(np.clip(z, -50.0, 50.0)) - 1.0)
    taylor = y * (1.0 - z / 2.0)
    return np.where(np.abs(z) < 1e-6, taylor, exact)


def steady_state(v_mV: float, V_T: float, tau_max_ms: float):
    """在给定膜电位下计算 m/h/n/p 的稳态值。"""
    v2 = v_mV - V_T

    a_m = 0.32 * vtrap_py(13.0 - v2, 4.0)
    b_m = 0.28 * vtrap_py(v2 - 40.0, 5.0)
    m_inf = a_m / (a_m + b_m)

    a_h = 0.128 * np.exp((17.0 - v2) / 18.0)
    b_h = 4.0 / (1.0 + np.exp((40.0 - v2) / 5.0))
    h_inf = a_h / (a_h + b_h)

    a_n = 0.032 * vtrap_py(15.0 - v2, 5.0)
    b_n = 0.5 * np.exp((10.0 - v2) / 40.0)
    n_inf = a_n / (a_n + b_n)

    p_inf = 1.0 / (1.0 + np.exp(-(v_mV + 35.0) / 10.0))

    return float(m_inf), float(h_inf), float(n_inf), float(p_inf)


def build_equations() -> str:
    """Pospischil RS 单房室 HH 方程（单位：mV, pA, pF, nS, ms）。"""
    return r"""
    I_inj : amp

    dv/dt = (I_inj - I_Na - I_K - I_M - I_L) / C_m : volt
    dm/dt = (m_inf - m) / tau_m : 1
    dh/dt = (h_inf - h) / tau_h : 1
    dn/dt = (n_inf - n) / tau_n : 1
    dp/dt = (p_inf - p) / tau_p : 1

    I_Na = g_Na * m**3 * h * (v - E_Na) : amp
    I_K  = g_K  * n**4     * (v - E_K)  : amp
    I_M  = g_M  * p        * (v - E_K)  : amp
    I_L  = g_L             * (v - E_L)  : amp

    v_mV = v / mV : 1
    v2 = v_mV - V_T : 1

    a_m = 0.32 * vtrap(13 - v2, 4) / ms : Hz
    b_m = 0.28 * vtrap(v2 - 40, 5) / ms : Hz
    tau_m = 1 / (a_m + b_m) : second
    m_inf = a_m / (a_m + b_m) : 1

    a_h = 0.128 * exp((17 - v2) / 18) / ms : Hz
    b_h = 4 / (1 + exp((40 - v2) / 5)) / ms : Hz
    tau_h = 1 / (a_h + b_h) : second
    h_inf = a_h / (a_h + b_h) : 1

    a_n = 0.032 * vtrap(15 - v2, 5) / ms : Hz
    b_n = 0.5 * exp((10 - v2) / 40) / ms : Hz
    tau_n = 1 / (a_n + b_n) : second
    n_inf = a_n / (a_n + b_n) : 1

    p_inf = 1 / (1 + exp(-(v_mV + 35) / 10)) : 1
    tau_p = tau_max / (3.3 * exp((v_mV + 35) / 20) + exp(-(v_mV + 35) / 20)) : second
    """


def make_vtrap() -> Function:
    """Brian 2 用户函数：与 vtrap_py 等价，供方程使用。"""
    return Function(
        vtrap_py,
        arg_units=[1, 1],
        return_unit=1,
        auto_vectorise=False,
    )


def make_namespace(cfg: dict, vtrap: Function) -> dict:
    """把 YAML 的绝对参数转成 Brian 2 常量。"""
    a = cfg["absolute"]
    return {
        "C_m": float(a["capacitance_pF"]) * pF,
        "g_L": float(a["leak_conductance_nS"]) * nS,
        "E_L": float(a["leak_reversal_mV"]) * mV,
        "g_Na": float(a["na_conductance_nS"]) * nS,
        "E_Na": float(a["na_reversal_mV"]) * mV,
        "g_K": float(a["k_conductance_nS"]) * nS,
        "E_K": float(a["k_reversal_mV"]) * mV,
        "g_M": float(a["m_conductance_nS"]) * nS,
        "V_T": float(a["vtraub_mV"]),
        "tau_max": float(a["m_tau_max_ms"]) * ms,
        "vtrap": vtrap,
    }


def make_group(cfg: dict, ns: dict, with_threshold: bool):
    """创建一个单细胞组；with_threshold=True 时用于 spike 计数。"""
    eqs = build_equations()
    method = cfg["numerics"]["method"]
    m0, h0, n0, p0 = steady_state(-70.0, ns["V_T"], cfg["absolute"]["m_tau_max_ms"])

    if with_threshold:
        G = NeuronGroup(
            1,
            eqs,
            threshold="v > 0*mV",
            reset="v = -70*mV",
            refractory=2 * ms,
            method=method,
            namespace=ns,
        )
    else:
        G = NeuronGroup(1, eqs, method=method, namespace=ns)

    G.v = -70 * mV
    G.m = m0
    G.h = h0
    G.n = n0
    G.p = p0
    G.I_inj = 0 * pA
    return G


def run_case(
    cfg: dict,
    ns: dict,
    amp_nA: float,
    duration_ms: float,
    with_threshold: bool = True,
    record_v: bool = True,
):
    """跑一个恒定电流 case，返回电压、spike 时间与墙钟耗时。"""
    G = make_group(cfg, ns, with_threshold)
    G.I_inj = amp_nA * nA

    objs = [G]
    mon = StateMonitor(G, "v", record=0) if record_v else None
    smon = SpikeMonitor(G) if with_threshold else None
    if mon is not None:
        objs.append(mon)
    if smon is not None:
        objs.append(smon)

    net = Network(objs)
    t0 = time.perf_counter()
    net.run(duration_ms * ms)
    wall = time.perf_counter() - t0

    t_ms = np.asarray(mon.t / ms) if mon is not None else None
    v_mV = np.asarray(mon.v[0] / mV) if mon is not None else None
    spike_times_s = (
        np.asarray(smon.t / second) if smon is not None else np.array([])
    )

    return {
        "v_mV": v_mV,
        "t_ms": t_ms,
        "spike_times_s": spike_times_s,
        "wall_s": wall,
    }


def count_spikes(spike_times_s: np.ndarray, t_start_s: float, t_end_s: float) -> int:
    return int(np.sum((spike_times_s >= t_start_s) & (spike_times_s < t_end_s)))


# ---------------------------------------------------------------------------
# 各项测试
# ---------------------------------------------------------------------------


def test_rest_and_rin(cfg: dict, ns: dict):
    p = cfg["phase0"]
    rest = run_case(cfg, ns, 0.0, p["rest_duration_ms"], with_threshold=True)
    rin = run_case(
        cfg, ns, p["rin_current_nA"], p["rin_duration_ms"], with_threshold=False
    )

    # 取最后 100 ms 的均值
    n_rest = max(1, int(100.0 / cfg["numerics"]["dt_ms"]))
    v_rest = float(np.mean(rest["v_mV"][-n_rest:]))
    v_hyper = float(np.mean(rin["v_mV"][-n_rest:]))
    rin_mohm = (v_rest - v_hyper) / abs(p["rin_current_nA"])

    return {
        "v_rest_mV": v_rest,
        "v_hyper_mV": v_hyper,
        "rin_mohm": rin_mohm,
        "rest_trace": rest,
        "rin_trace": rin,
    }


def test_fi(cfg: dict, ns: dict):
    p = cfg["phase0"]
    amps = np.arange(
        p["fi_current_min_nA"],
        p["fi_current_max_nA"] + p["fi_current_step_nA"] / 2,
        p["fi_current_step_nA"],
    )
    rows = []
    for amp in amps:
        res = run_case(
            cfg, ns, float(amp), p["fi_duration_ms"], with_threshold=True, record_v=False
        )
        t0 = p["fi_warmup_ms"] / 1000.0
        t1 = p["fi_duration_ms"] / 1000.0
        n = count_spikes(res["spike_times_s"], t0, t1)
        rate = n / (t1 - t0)
        rows.append({"current_nA": float(amp), "spikes": n, "rate_hz": rate})

    df = pd.DataFrame(rows)
    return df


def refine_rheobase(cfg: dict, ns: dict, fi_df: pd.DataFrame):
    p = cfg["phase0"]
    firing = fi_df[fi_df["spikes"] > 0]
    if firing.empty:
        return None

    first_amp = float(firing.iloc[0]["current_nA"])
    prev_amp = first_amp - p["fi_current_step_nA"]
    prev_amp = max(prev_amp, 0.0)

    step = p["rheobase_scan_step_nA"]
    amps = np.arange(prev_amp, first_amp + step / 2, step)
    smallest = None
    for amp in amps:
        res = run_case(
            cfg, ns, float(amp), p["fi_duration_ms"], with_threshold=True, record_v=False
        )
        n = count_spikes(
            res["spike_times_s"], p["fi_warmup_ms"] / 1000.0, p["fi_duration_ms"] / 1000.0
        )
        if n > 0:
            smallest = float(amp)
            break
    return smallest


def test_spike_waveform(cfg: dict, ns: dict):
    """短脉冲诱发单个 spike，记录完整波形（无 threshold/reset）。"""
    p = cfg["phase0"]
    G = make_group(cfg, ns, with_threshold=False)
    mon = StateMonitor(G, "v", record=0)
    net = Network(G, mon)

    # 先稳定 20 ms，再给 5 ms 脉冲，再恢复 60 ms
    net.run(20 * ms)
    G.I_inj = p["spike_current_nA"] * nA
    net.run(p["spike_pulse_ms"] * ms)
    G.I_inj = 0 * nA
    net.run(p["spike_tail_ms"] * ms)

    t = np.asarray(mon.t / ms)
    v = np.asarray(mon.v[0] / mV)

    # 找第一个超过 0 mV 的 spike
    above = np.where(v > 0.0)[0]
    if len(above) == 0:
        return {"detected": False}

    i_peak = above[0]
    # 找局部峰值（在第一个 above 之后 2 ms 内）
    i_end = min(len(v), i_peak + int(2.0 / cfg["numerics"]["dt_ms"]))
    i_peak = i_peak + int(np.argmax(v[i_peak:i_end]))
    v_peak = float(v[i_peak])

    # baseline：脉冲前 5 ms
    i_base_end = max(1, i_peak - int(10.0 / cfg["numerics"]["dt_ms"]))
    v_base = float(np.mean(v[max(0, i_base_end - 200) : i_base_end]))

    # 阈值：上升沿中 dv/dt 首次超过 10 mV/ms 的点
    dv = np.gradient(v, t)
    i_up = max(0, i_peak - int(5.0 / cfg["numerics"]["dt_ms"]))
    crossing = np.where(dv[i_up:i_peak] > 10.0)[0]
    if len(crossing) > 0:
        i_thr = i_up + crossing[0]
        v_thr = float(v[i_thr])
    else:
        v_thr = float("nan")

    amplitude = v_peak - v_base

    # 半宽：峰值后电压降到 v_base + amplitude/2 的时间
    half_level = v_base + amplitude / 2.0
    after = np.where(v[i_peak:] < half_level)[0]
    if len(after) > 0:
        i_half = i_peak + after[0]
        half_width_ms = float(t[i_half] - t[i_peak])
    else:
        half_width_ms = float("nan")

    # AHP：峰值后 20 ms 内最低电压
    i_ahp_end = min(len(v), i_peak + int(20.0 / cfg["numerics"]["dt_ms"]))
    v_ahp = float(np.min(v[i_peak:i_ahp_end]))

    # 画图窗口：峰值前 5 ms 到后 20 ms
    i_lo = max(0, i_peak - int(5.0 / cfg["numerics"]["dt_ms"]))
    i_hi = min(len(v), i_peak + int(20.0 / cfg["numerics"]["dt_ms"]))

    return {
        "detected": True,
        "v_peak_mV": v_peak,
        "v_base_mV": v_base,
        "v_threshold_mV": v_thr,
        "amplitude_mV": amplitude,
        "half_width_ms": half_width_ms,
        "v_ahp_mV": v_ahp,
        "t_plot_ms": t[i_lo:i_hi],
        "v_plot_mV": v[i_lo:i_hi],
    }


def test_adaptation(cfg: dict, ns: dict):
    p = cfg["phase0"]
    res = run_case(
        cfg, ns, p["adaptation_current_nA"], p["adaptation_duration_ms"], with_threshold=True
    )
    times = res["spike_times_s"]
    if len(times) < 3:
        return {"enough_spikes": False, "n_spikes": int(len(times))}

    isi = np.diff(times) * 1000.0  # ms
    first_isi = float(isi[0])
    last_isi = float(isi[-1])
    ratio = last_isi / first_isi if first_isi > 0 else float("nan")

    t_end = p["adaptation_duration_ms"] / 1000.0
    first_window = count_spikes(times, 0.0, 0.3) / 0.3
    last_window = count_spikes(times, t_end - 0.3, t_end) / 0.3

    inst_rate = 1000.0 / isi  # Hz
    inst_times = times[1:]  # ISI 对应后一个 spike

    return {
        "enough_spikes": True,
        "n_spikes": int(len(times)),
        "first_isi_ms": first_isi,
        "last_isi_ms": last_isi,
        "isi_ratio": ratio,
        "rate_first_300ms_hz": first_window,
        "rate_last_300ms_hz": last_window,
        "v_trace": res,
        "inst_rate_hz": inst_rate,
        "inst_times_s": inst_times,
    }


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config/cell_pospischil_rs.yaml",
        help="Pospischil RS 参数 YAML",
    )
    parser.add_argument(
        "--outdir", default="results/phase0", help="输出目录"
    )
    args = parser.parse_args()

    cfg_path = Path(args.config)
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 数值设置
    defaultclock.dt = cfg["numerics"]["dt_ms"] * ms
    prefs.codegen.target = cfg["numerics"]["codegen_target"]
    seed(int(cfg["phase0"]["seed"]))

    vtrap = make_vtrap()
    ns = make_namespace(cfg, vtrap)

    print("=" * 70)
    print("Phase 0: Pospischil 2008 RS baseline")
    print(f"dt = {cfg['numerics']['dt_ms']} ms, method = {cfg['numerics']['method']}")
    print(f"codegen target = {prefs.codegen.target}")
    print("=" * 70)

    # 1. rest + Rin
    print("\n[1/5] Resting potential and input resistance ...")
    rr = test_rest_and_rin(cfg, ns)
    print(f"  V_rest = {rr['v_rest_mV']:.2f} mV")
    print(f"  Rin    = {rr['rin_mohm']:.2f} MOhm")

    # 2. f-I
    print("\n[2/5] f-I curve ...")
    fi_df = test_fi(cfg, ns)
    fi_df.to_csv(outdir / "fi_curve.csv", index=False)
    print(fi_df.to_string(index=False))

    # 3. rheobase
    print("\n[3/5] Rheobase ...")
    rheobase = refine_rheobase(cfg, ns, fi_df)
    print(f"  rheobase = {rheobase} nA" if rheobase is not None else "  rheobase not found")

    # 4. spike waveform
    print("\n[4/5] Spike waveform ...")
    wave = test_spike_waveform(cfg, ns)
    if wave["detected"]:
        print(
            f"  peak = {wave['v_peak_mV']:.2f} mV, amplitude = {wave['amplitude_mV']:.2f} mV, "
            f"half-width = {wave['half_width_ms']:.2f} ms"
        )
    else:
        print("  no spike detected in waveform test")

    # 5. adaptation + benchmark
    print("\n[5/5] Adaptation and speed benchmark ...")
    adapt = test_adaptation(cfg, ns)
    if adapt["enough_spikes"]:
        print(
            f"  spikes = {adapt['n_spikes']}, ISI ratio = {adapt['isi_ratio']:.2f}, "
            f"rate first/last 300 ms = {adapt['rate_first_300ms_hz']:.1f}/"
            f"{adapt['rate_last_300ms_hz']:.1f} Hz"
        )
    else:
        print(f"  not enough spikes: {adapt.get('n_spikes')}")

    bench = run_case(
        cfg,
        ns,
        cfg["phase0"]["benchmark_current_nA"],
        cfg["phase0"]["benchmark_duration_ms"],
        with_threshold=True,
        record_v=False,
    )
    sim_s = cfg["phase0"]["benchmark_duration_ms"] / 1000.0
    print(f"  benchmark: {sim_s:.1f} s simulated in {bench['wall_s']:.2f} s wall")

    # ------------------------------------------------------------------
    # 图
    # ------------------------------------------------------------------
    plt.rcParams.update({"figure.dpi": 130, "font.size": 10})

    # f-I
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(fi_df["current_nA"], fi_df["rate_hz"], "o-", ms=3, lw=1.2)
    if rheobase is not None:
        ax.axvline(rheobase, color="tab:red", ls="--", lw=1, label=f"rheobase {rheobase:.3f} nA")
        ax.legend(frameon=False)
    ax.set_xlabel("Injected current (nA)")
    ax.set_ylabel("Firing rate (Hz)")
    ax.set_title("Pospischil RS: f-I curve")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_fi_curve.png", bbox_inches="tight")
    plt.close(fig)

    # spike waveform
    if wave["detected"]:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(wave["t_plot_ms"], wave["v_plot_mV"], lw=1.4)
        ax.axhline(wave["v_threshold_mV"], color="tab:red", ls=":", lw=1, label="threshold (dv/dt>10)")
        ax.axhline(wave["v_ahp_mV"], color="tab:green", ls=":", lw=1, label="AHP")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Membrane potential (mV)")
        ax.set_title("Single action potential")
        ax.legend(frameon=False, fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(outdir / "fig_spike_waveform.png", bbox_inches="tight")
        plt.close(fig)

    # adaptation
    if adapt["enough_spikes"]:
        fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=False)
        axes[0].plot(adapt["v_trace"]["t_ms"], adapt["v_trace"]["v_mV"], lw=1.0)
        axes[0].set_ylabel("V (mV)")
        axes[0].set_title("Spike-frequency adaptation")
        axes[0].grid(alpha=0.3)

        axes[1].plot(adapt["inst_times_s"], adapt["inst_rate_hz"], "o-", ms=2, lw=1.0)
        axes[1].set_xlabel("Time (s)")
        axes[1].set_ylabel("Instantaneous rate (Hz)")
        axes[1].grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(outdir / "fig_adaptation.png", bbox_inches="tight")
        plt.close(fig)

    # rest + Rin
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(rr["rest_trace"]["t_ms"], rr["rest_trace"]["v_mV"], label="I = 0 nA", lw=1.2)
    ax.plot(
        rr["rin_trace"]["t_ms"],
        rr["rin_trace"]["v_mV"],
        label=f"I = {cfg['phase0']['rin_current_nA']} nA",
        lw=1.2,
    )
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("V (mV)")
    ax.set_title("Rest and input resistance")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_rest_rin.png", bbox_inches="tight")
    plt.close(fig)

    # ------------------------------------------------------------------
    # 指标与报告
    # ------------------------------------------------------------------
    v_rest = rr["v_rest_mV"]
    rin = rr["rin_mohm"]

    metrics = {
        "v_rest_mV": {
            "value": v_rest,
            "unit": "mV",
            "criterion": "-75 to -65",
            "pass": bool(-75 <= v_rest <= -65),
        },
        "rin_mohm": {
            "value": rin,
            "unit": "MOhm",
            "criterion": "25 to 45 (paper: 34.5)",
            "pass": bool(25 <= rin <= 45),
        },
        "rheobase_nA": {
            "value": rheobase,
            "unit": "nA",
            "criterion": "0.1 to 0.8",
            "pass": bool(rheobase is not None and 0.1 <= rheobase <= 0.8),
        },
        "spike_amplitude_mV": {
            "value": wave.get("amplitude_mV"),
            "unit": "mV",
            "criterion": "> 50",
            "pass": bool(wave.get("detected") and wave.get("amplitude_mV", 0) > 50),
        },
        "spike_half_width_ms": {
            "value": wave.get("half_width_ms"),
            "unit": "ms",
            "criterion": "0.3 to 3.0",
            "pass": bool(
                wave.get("detected")
                and 0.3 <= wave.get("half_width_ms", float("nan")) <= 3.0
            ),
        },
        "isi_ratio": {
            "value": adapt.get("isi_ratio"),
            "unit": "last/first",
            "criterion": "> 1.0 (adaptation: ISI lengthens)",
            "pass": bool(adapt.get("enough_spikes") and adapt.get("isi_ratio", 0) > 1.0),
        },
        "rate_at_0p8nA_hz": {
            "value": float(
                fi_df.loc[(fi_df["current_nA"] - 0.8).abs().idxmin(), "rate_hz"]
            ),
            "unit": "Hz",
            "criterion": "1 to 100",
            "pass": bool(
                1
                <= float(fi_df.loc[(fi_df["current_nA"] - 0.8).abs().idxmin(), "rate_hz"])
                <= 100
            ),
        },
        "benchmark_wall_s_per_sim_s": {
            "value": bench["wall_s"] / sim_s,
            "unit": "s wall / s sim",
            "criterion": "report only",
            "pass": True,
        },
    }

    summary = {
        "model": cfg["model"],
        "config": str(cfg_path),
        "dt_ms": cfg["numerics"]["dt_ms"],
        "codegen_target": prefs.codegen.target,
        "metrics": metrics,
        "fi_curve": fi_df.to_dict(orient="records"),
        "rheobase_nA": rheobase,
        "adaptation": {
            k: v
            for k, v in adapt.items()
            if k not in ("v_trace", "inst_rate_hz", "inst_times_s")
        },
        "waveform": {
            k: v
            for k, v in wave.items()
            if k not in ("t_plot_ms", "v_plot_mV")
        },
        "benchmark": {
            "sim_s": sim_s,
            "wall_s": bench["wall_s"],
            "ratio": bench["wall_s"] / sim_s,
        },
    }

    with (outdir / "phase0_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    # Markdown 报告
    def fmt(x, nd=2):
        if x is None:
            return "n/a"
        try:
            if np.isnan(x):
                return "n/a"
        except TypeError:
            pass
        return f"{x:.{nd}f}"

    lines = []
    lines.append("# Phase 0 Baseline Report")
    lines.append("")
    lines.append(f"- Model: `{cfg['model']}`")
    lines.append(f"- Config: `{cfg_path}`")
    lines.append(f"- dt: {cfg['numerics']['dt_ms']} ms")
    lines.append(f"- codegen target: `{prefs.codegen.target}`")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value | Unit | Criterion | Pass |")
    lines.append("|---|---:|---|---|---|")
    for name, m in metrics.items():
        val = fmt(m["value"], 3) if isinstance(m["value"], (int, float)) else m["value"]
        lines.append(
            f"| {name} | {val} | {m['unit']} | {m['criterion']} | {'PASS' if m['pass'] else 'FAIL'} |"
        )
    lines.append("")
    lines.append("## f-I curve")
    lines.append("")
    lines.append("| current_nA | spikes | rate_hz |")
    lines.append("|---:|---:|---:|")
    for row in fi_df.itertuples(index=False):
        lines.append(f"| {row.current_nA:.3f} | {row.spikes} | {row.rate_hz:.2f} |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- 参数来源：Pospischil et al. 2008, Fig. 1 caption; ModelDB 123623 `sPY_template`.")
    lines.append("- 有效膜面积按论文的 0.29 nF / 34.5 MΩ 换算（2.9e-4 cm²），而非 ModelDB 注释里的 29000 µm²。")
    lines.append("- E_K 采用 ModelDB 的 -100 mV；论文正文写 -90 mV。若 f-I 偏离，可在阶段 0 报告里对比。")
    lines.append("- spike 计数使用 threshold=0 mV、reset v=-70 mV、refractory=2 ms；waveform 用无 threshold 的单独组。")
    lines.append("- 本阶段不包含任何可塑性规则，不训练，不涉及 Pong。")
    lines.append("")

    (outdir / "phase0_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"Done. Outputs written to: {outdir.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
