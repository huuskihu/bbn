r"""
阶段 2.2：资格迹 + 三因子调制的延迟奖励验证。

协议：
    在 t=100/110 ms 给一对 pre-post（通道 0），产生资格迹；
    在延迟 d 后给全局调制信号 D = ±1；
    预期：Δw 随延迟指数衰减；D=+1 为正，D=-1 为负；未配对通道 Δw≈0。

输出：
    results/phase2/fig_eligibility.png
    results/phase2/eligibility.csv
    results/phase2/eligibility_report.md
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

from src.plasticity.stdp import EligibilitySynapse, STDPConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase2.yaml")
    parser.add_argument("--outdir", default="results/phase2")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    c = cfg["stdp"]
    e = cfg["eligibility"]
    stdp_cfg = STDPConfig(
        a_plus=float(c["a_plus"]),
        a_minus=float(c["a_minus"]),
        tau_plus_ms=float(c["tau_plus_ms"]),
        tau_minus_ms=float(c["tau_minus_ms"]),
        w_min=float(c["w_min"]),
        w_max=float(c["w_max"]),
        tau_e_ms=float(e["tau_e_ms"]),
        eta=float(e["eta"]),
    )
    w0 = float(c["w_init"])
    delays = [float(x) for x in e["delays_s"]]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    for d in delays:
        for reward_sign in (+1.0, -1.0):
            syn = EligibilitySynapse(2, stdp_cfg, w_init=w0)
            syn.pre_spike(0, 100.0)
            syn.post_spike(110.0)
            t_reward = 110.0 + d * 1000.0
            dw = syn.reward(t_reward, reward_sign)
            rows.append(
                {
                    "delay_s": d,
                    "D": reward_sign,
                    "dw_paired": float(dw[0]),
                    "dw_unpaired": float(dw[1]),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(outdir / "eligibility.csv", index=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    for sign, label in [(1.0, "D = +1"), (-1.0, "D = -1")]:
        sub = df[df["D"] == sign]
        ax.plot(sub["delay_s"], sub["dw_paired"], "o-", ms=3, lw=1.2, label=label)
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("Reward delay (s)")
    ax.set_ylabel("Δw (paired channel)")
    ax.set_title("Eligibility trace: delayed reward")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_eligibility.png", bbox_inches="tight")
    plt.close(fig)

    # 判据
    plus = df[df["D"] == 1.0].sort_values("delay_s")
    minus = df[df["D"] == -1.0].sort_values("delay_s")
    passes = {
        "plus_positive": bool((plus["dw_paired"] > 0).all()),
        "minus_negative": bool((minus["dw_paired"] < 0).all()),
        "decays_with_delay": bool(
            plus["dw_paired"].iloc[0] > plus["dw_paired"].iloc[-1]
        ),
        "unpaired_zero": bool(np.allclose(df["dw_unpaired"], 0.0, atol=1e-12)),
    }

    lines = []
    lines.append("# Phase 2.2 Eligibility + Three-Factor")
    lines.append("")
    lines.append(f"- τ_e = {stdp_cfg.tau_e_ms} ms; η = {stdp_cfg.eta}")
    lines.append(f"- Pair: pre 100 ms, post 110 ms (Δt = +10 ms)")
    lines.append("")
    lines.append("| delay (s) | D | Δw paired | Δw unpaired |")
    lines.append("|---:|---:|---:|---:|")
    for row in df.itertuples(index=False):
        lines.append(
            f"| {row.delay_s:.1f} | {row.D:+.0f} | {row.dw_paired:.5f} | {row.dw_unpaired:.5f} |"
        )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in passes.items():
        lines.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append(
        "η=1.0 只是为了让验证曲线可见；Phase 3 会重新设定生物合理的学习率。"
        "延迟奖励能作用到正确通道，是 distal reward problem 的最小验证（Izhikevich 2007）。"
    )
    lines.append("")
    (outdir / "eligibility_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(df.to_string(index=False))
    print(f"outputs -> {outdir.resolve()}")


if __name__ == "__main__":
    main()
