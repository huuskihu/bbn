r"""
阶段 2.3：稳态突触缩放验证。

协议：
    给 FastHH 一个恒定的兴奋性电导 drive；
    每 1 s 测一次放电率，按 Turrigiano 乘性缩放规则调整 drive；
    预期：从高驱动和低驱动出发，放电率都收敛到目标 20 Hz，权重不越界。

输出：
    results/phase2/fig_homeostasis.png
    results/phase2/homeostasis.csv
    results/phase2/homeostasis_report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cell.hh_numba import FastHH, HHParams
from src.plasticity.homeostasis import HomeostasisConfig, HomeostaticScaler


def load_cell(cfg) -> HHParams:
    c = cfg["cell"]
    return HHParams(
        C_m=float(c["C_m_pF"]),
        g_L=float(c["g_L_nS"]),
        E_L=float(c["E_L_mV"]),
        g_Na=float(c["g_Na_nS"]),
        E_Na=float(c["E_Na_mV"]),
        g_K=float(c["g_K_nS"]),
        E_K=float(c["E_K_mV"]),
        g_M=float(c["g_M_nS"]),
        V_T=float(c["V_T_mV"]),
        tau_max=float(c["tau_max_ms"]),
    )


def run_case(cell_params, hs_cfg, initial_drive, duration_s, window_s=1.0, tick_ms=10.0):
    cell = FastHH(params=cell_params, dt_ms=0.01, n_channels=8)
    scaler = HomeostaticScaler(np.array([initial_drive], dtype=float), hs_cfg)

    rates = []
    drives = []
    spikes_in_window = 0
    t_window = 0.0

    n_ticks = int(round(duration_s * 1000.0 / tick_ms))
    ticks_per_window = int(round(window_s * 1000.0 / tick_ms))

    for k in range(n_ticks):
        # 恒定电导：每个 tick 重新设定，抵消指数衰减
        cell.g_syn[:] = 0.0
        cell.g_syn[0] = scaler.weights[0]
        new = cell.run(tick_ms)
        spikes_in_window += len(new)
        t_window += tick_ms

        if (k + 1) % ticks_per_window == 0:
            rate = spikes_in_window / window_s
            rates.append(rate)
            drives.append(float(scaler.weights[0]))
            scaler.scale(rate)
            spikes_in_window = 0
            t_window = 0.0

    t = np.arange(1, len(rates) + 1) * window_s
    return np.array(t), np.array(rates), np.array(drives)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase2.yaml")
    parser.add_argument("--outdir", default="results/phase2")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    cell_params = load_cell(cfg)
    h = cfg["homeostasis"]
    hs_cfg = HomeostasisConfig(
        target_rate_hz=float(h["target_rate_hz"]),
        alpha=float(h["alpha"]),
        w_min=float(h["w_min_nS"]),
        w_max=float(h["w_max_nS"]),
        rate_floor_hz=float(h["rate_floor_hz"]),
    )
    duration = float(h["duration_s"])
    window = float(h["measure_window_s"])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cases = {
        "high": float(h["initial_drive_high_nS"]),
        "low": float(h["initial_drive_low_nS"]),
    }

    rows = []
    fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    for name, drive0 in cases.items():
        t, rates, drives = run_case(cell_params, hs_cfg, drive0, duration, window)
        for ti, r, d in zip(t, rates, drives):
            rows.append(
                {"case": name, "t_s": float(ti), "rate_hz": float(r), "drive_nS": float(d)}
            )
        axes[0].plot(t, rates, lw=1.2, label=f"{name} start ({drive0:.1f} nS)")
        axes[1].plot(t, drives, lw=1.2, label=name)

    axes[0].axhline(hs_cfg.target_rate_hz, color="tab:red", ls="--", lw=0.8, label="target")
    axes[0].set_ylabel("Firing rate (Hz)")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[1].axhline(hs_cfg.w_min, color="gray", ls=":", lw=0.8)
    axes[1].axhline(hs_cfg.w_max, color="gray", ls=":", lw=0.8)
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Drive conductance (nS)")
    axes[1].legend(frameon=False, fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.suptitle("Homeostatic synaptic scaling")
    fig.tight_layout()
    fig.savefig(outdir / "fig_homeostasis.png", bbox_inches="tight")
    plt.close(fig)

    df = pd.DataFrame(rows)
    df.to_csv(outdir / "homeostasis.csv", index=False)

    # 判据：最后 10 s 的平均率接近目标
    summary = []
    for name in cases:
        sub = df[(df["case"] == name) & (df["t_s"] >= duration - 10.0)]
        final_rate = float(sub["rate_hz"].mean())
        final_drive = float(sub["drive_nS"].mean())
        summary.append(
            {
                "case": name,
                "final_rate_hz": final_rate,
                "final_drive_nS": final_drive,
                "abs_error_hz": abs(final_rate - hs_cfg.target_rate_hz),
                "within_bounds": bool(
                    hs_cfg.w_min <= final_drive <= hs_cfg.w_max
                ),
            }
        )
    sdf = pd.DataFrame(summary)

    lines = []
    lines.append("# Phase 2.3 Homeostatic Scaling")
    lines.append("")
    lines.append(f"- target = {hs_cfg.target_rate_hz} Hz; α = {hs_cfg.alpha}")
    lines.append(f"- bounds = [{hs_cfg.w_min}, {hs_cfg.w_max}] nS")
    lines.append("")
    lines.append("| start | final rate (Hz) | final drive (nS) | |error| (Hz) | within bounds |")
    lines.append("|---|---:|---:|---:|---|")
    for row in sdf.itertuples(index=False):
        lines.append(
            f"| {row.case} | {row.final_rate_hz:.1f} | {row.final_drive_nS:.2f} | "
            f"{row.abs_error_hz:.1f} | {'PASS' if row.within_bounds else 'FAIL'} |"
        )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for row in sdf.itertuples(index=False):
        ok = row.abs_error_hz <= 5.0
        lines.append(f"- {row.case} converges within 5 Hz: {'PASS' if ok else 'FAIL'}")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append(
        "本测试把 8 个感觉通道等效成一个总驱动电导；Phase 3 会对 8 个权重做同样的乘性缩放。"
    )
    lines.append("")
    (outdir / "homeostasis_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(sdf.to_string(index=False))
    print(f"outputs -> {outdir.resolve()}")


if __name__ == "__main__":
    main()
