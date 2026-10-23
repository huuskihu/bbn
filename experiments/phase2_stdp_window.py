r"""
阶段 2.1：pair-based STDP 学习窗口验证。

协议：
    单个 pre 脉冲与单个 post 脉冲，扫描 Δt = t_post - t_pre ∈ [-50, 50] ms。
    预期：Δt > 0 -> LTP（Δw > 0）；Δt < 0 -> LTD（Δw < 0）；
    |Δt| 越大，|Δw| 越小（指数衰减）。

输出：
    results/phase2/fig_stdp_window.png
    results/phase2/stdp_window.csv
    results/phase2/stdp_report.md
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

from src.plasticity.stdp import STDPConfig, STDPSynapse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase2.yaml")
    parser.add_argument("--outdir", default="results/phase2")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    c = cfg["stdp"]
    stdp_cfg = STDPConfig(
        a_plus=float(c["a_plus"]),
        a_minus=float(c["a_minus"]),
        tau_plus_ms=float(c["tau_plus_ms"]),
        tau_minus_ms=float(c["tau_minus_ms"]),
        w_min=float(c["w_min"]),
        w_max=float(c["w_max"]),
    )
    w0 = float(c["w_init"])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dts = np.arange(-50.0, 50.01, 1.0)
    rows = []
    for dt in dts:
        syn = STDPSynapse(1, stdp_cfg, w_init=w0)
        t_pre = 100.0
        t_post = t_pre + dt
        if dt >= 0:
            syn.pre_spike(0, t_pre)
            syn.post_spike(t_post)
        else:
            syn.post_spike(t_pre)
            syn.pre_spike(0, t_pre + abs(dt))
        rows.append({"dt_ms": float(dt), "dw": float(syn.w[0] - w0)})

    df = pd.DataFrame(rows)
    df.to_csv(outdir / "stdp_window.csv", index=False)

    # 理论曲线
    theory = []
    for dt in dts:
        if dt >= 0:
            theory.append(stdp_cfg.a_plus * np.exp(-dt / stdp_cfg.tau_plus_ms))
        else:
            theory.append(-stdp_cfg.a_minus * np.exp(dt / stdp_cfg.tau_minus_ms))
    theory = np.array(theory)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["dt_ms"], df["dw"], "o-", ms=3, lw=1.2, label="simulated")
    ax.plot(dts, theory, "--", lw=1.0, label="theory")
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set_xlabel("Δt = t_post − t_pre (ms)")
    ax.set_ylabel("Δw")
    ax.set_title("Pair-based STDP window")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_stdp_window.png", bbox_inches="tight")
    plt.close(fig)

    # 判据
    ltp = df[df["dt_ms"] > 0]["dw"].to_numpy()
    ltd = df[df["dt_ms"] < 0]["dw"].to_numpy()
    peak_ltp = float(np.max(ltp))
    peak_ltd = float(np.min(ltd))
    max_err = float(np.max(np.abs(df["dw"].to_numpy() - theory)))
    passes = {
        "ltp_positive": bool(peak_ltp > 0),
        "ltd_negative": bool(peak_ltd < 0),
        "ltp_at_short_dt": bool(peak_ltp > 0.8 * stdp_cfg.a_plus),
        "matches_theory": bool(max_err < 1e-9),
    }

    lines = []
    lines.append("# Phase 2.1 STDP Window")
    lines.append("")
    lines.append(f"- A+ = {stdp_cfg.a_plus}, A− = {stdp_cfg.a_minus}")
    lines.append(f"- τ+ = {stdp_cfg.tau_plus_ms} ms, τ− = {stdp_cfg.tau_minus_ms} ms")
    lines.append(f"- Peak LTP: {peak_ltp:.5f}")
    lines.append(f"- Peak LTD: {peak_ltd:.5f}")
    lines.append(f"- Max deviation from theory: {max_err:.2e}")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in passes.items():
        lines.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append(
        "本测试只验证 pair-based 规则本身；细胞膜动力学与闭环整合在阶段 3 验证。"
    )
    lines.append("")
    (outdir / "stdp_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"peak LTP={peak_ltp:.5f}, peak LTD={peak_ltd:.5f}, max_err={max_err:.2e}")
    print(f"outputs -> {outdir.resolve()}")


if __name__ == "__main__":
    main()
