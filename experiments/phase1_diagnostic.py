"""
阶段 1 诊断：单细胞读出是否真的携带“球的位置”信息？

背景：
    Phase 1 静态基线显示球拍长期饱和，full_feedback 与 random_paddle 接近。
    需要确认：细胞的放电率是否依赖于 ball_y（位置），还是主要被 ball_x（距离）
    和反馈刺激驱动。这个诊断决定阶段 3 的单细胞学习是否有意义。

做法：
    - 跑 3 个种子的 full_feedback 60 s；
    - 按 rally 切分（ball_x 从 ~0 跳回 1）；
    - 每个 rally 取 ball_x ∈ [0.4, 0.8] 的中间接近段，计算平均放电率；
    - 对“平均放电率 ~ rally 的 ball_y”做线性回归，报告 R² / Pearson r；
    - 画 rate vs ball_y、感觉通道权重。

输出：
    results/phase1/diagnostic.md
    results/phase1/fig_diag_rate_vs_y.png
    results/phase1/fig_diag_weights.png
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

from src.cell.hh_numba import HHParams
from src.env.pong import PongConfig
from src.loop.phase1_loop import Phase1Config, Phase1Loop


def load_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    c = cfg["cell"]
    cell = HHParams(
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

    p = cfg["phase1"]
    pc = Phase1Config(
        tick_ms=float(p["tick_ms"]),
        duration_s=float(p["duration_s"]),
        readout_window_ms=float(p["readout_window_ms"]),
        rate_smoothing=float(p["rate_smoothing"]),
        reference_rate_hz=float(p["reference_rate_hz"]),
        velocity_gain=float(p["velocity_gain"]),
        max_velocity=float(p["max_velocity"]),
        rate_min_hz=float(p["rate_min_hz"]),
        rate_max_hz=float(p["rate_max_hz"]),
        place_sigma_bins=float(p["place_sigma_bins"]),
        syn_weight_nS=float(p["syn_weight_nS"]),
        syn_weight_jitter=float(p["syn_weight_jitter"]),
        syn_tau_ms=float(p["syn_tau_ms"]),
        E_syn_mV=float(p["E_syn_mV"]),
        predictable_rate_hz=float(p["predictable_rate_hz"]),
        predictable_duration_ms=float(p["predictable_duration_ms"]),
        predictable_weight_nS=float(p["predictable_weight_nS"]),
        unpredictable_rate_hz=float(p["unpredictable_rate_hz"]),
        unpredictable_duration_s=float(p["unpredictable_duration_s"]),
        unpredictable_weight_nS=float(p["unpredictable_weight_nS"]),
        rest_after_miss_s=float(p["rest_after_miss_s"]),
    )

    g = cfg["pong"]
    pong = PongConfig(
        ball_speed=float(g["ball_speed"]),
        paddle_bins=float(g["paddle_bins"]),
        hit_tolerance=float(g["hit_tolerance"]),
        y_min=float(g["y_min"]),
        y_max=float(g["y_max"]),
        initial_paddle_y=float(g["initial_paddle_y"]),
    )
    return cell, pc, pong


def split_rallies(df: pd.DataFrame):
    """按 ball_x 从 ~0 跳回 1 切分 rally。"""
    rallies = []
    current = None
    prev_x = None
    for row in df.itertuples(index=False):
        if current is None or (prev_x is not None and row.ball_x > prev_x + 0.5):
            if current is not None:
                rallies.append(current)
            current = {"ball_y": float(row.ball_y), "rows": []}
        current["rows"].append(row)
        prev_x = float(row.ball_x)
    if current is not None:
        rallies.append(current)
    return rallies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase1.yaml")
    parser.add_argument("--outdir", default="results/phase1")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--seeds", default="0,1,2")
    args = parser.parse_args()

    cell, phase1_cfg, pong_cfg = load_config(args.config)
    phase1_cfg.duration_s = args.duration
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    all_points = []
    all_weights = []

    for seed in seeds:
        print(f"[diagnostic] full_feedback seed={seed}")
        loop = Phase1Loop(
            condition="full_feedback",
            cfg=phase1_cfg,
            cell_params=cell,
            pong_cfg=pong_cfg,
            seed=seed,
        )
        _, trace = loop.run()
        df = pd.DataFrame(
            trace,
            columns=[
                "t_ms",
                "ball_x",
                "ball_y",
                "paddle_y",
                "rate_hz",
                "rate_used",
                "velocity",
                "event",
                "new_spikes",
            ],
        )
        all_weights.append(loop.w_syn.copy())

        rallies = split_rallies(df)
        for r in rallies:
            rows = [row for row in r["rows"] if 0.4 <= float(row.ball_x) <= 0.8]
            if len(rows) < 5:
                continue
            rates = np.array([float(row.rate_hz) for row in rows])
            xs = np.array([float(row.ball_x) for row in rows])
            all_points.append(
                {
                    "seed": seed,
                    "ball_y": r["ball_y"],
                    "mean_rate": float(np.mean(rates)),
                    "mean_x": float(np.mean(xs)),
                    "n_ticks": len(rows),
                }
            )

    pts = pd.DataFrame(all_points)
    if pts.empty:
        raise RuntimeError("no rallies collected; increase duration")

    # 线性回归 mean_rate ~ ball_y
    x = pts["ball_y"].to_numpy()
    y = pts["mean_rate"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    # rate ~ ball_x 的对照：中段窗口里 ball_x 方差很小，不做回归；
    # Phase 1 基线已经显示率随球接近而升高（距离驱动）。
    r = float(np.corrcoef(x, y)[0, 1]) if len(x) > 2 else float("nan")

    # 图 1：rate vs ball_y
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(pts["ball_y"], pts["mean_rate"], s=18, alpha=0.7)
    xx = np.linspace(pts["ball_y"].min(), pts["ball_y"].max(), 50)
    ax.plot(xx, slope * xx + intercept, color="tab:red", lw=1.2)
    ax.set_xlabel("Ball y at rally start (bins)")
    ax.set_ylabel("Mean firing rate in mid-approach (Hz)")
    ax.set_title(f"Rate vs ball y (R²={r2:.2f}, r={r:.2f}, n={len(pts)})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_diag_rate_vs_y.png", bbox_inches="tight")
    plt.close(fig)

    # 图 2：感觉通道权重
    w = np.mean(np.vstack(all_weights), axis=0)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(np.arange(1, 9), w)
    ax.set_xlabel("Sensory channel (ball y bin)")
    ax.set_ylabel("Synaptic weight (nS)")
    ax.set_title("Fixed sensory weights (untrained, mean over seeds)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_diag_weights.png", bbox_inches="tight")
    plt.close(fig)

    # 报告
    lines = []
    lines.append("# Phase 1 Diagnostic: does the single-cell rate carry ball-y information?")
    lines.append("")
    lines.append(f"- Duration per seed: {args.duration:.1f} s")
    lines.append(f"- Seeds: {seeds}")
    lines.append(f"- Rallies with valid mid-approach: {len(pts)}")
    lines.append(f"- Mean rate: {y.mean():.1f} ± {y.std():.1f} Hz")
    lines.append("")
    lines.append("## Regression")
    lines.append("")
    lines.append("| Predictor | slope | R² | Pearson r |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| ball_y | {slope:.2f} Hz/bin | {r2:.3f} | {r:.3f} |")
    lines.append("")
    lines.append(
        "> ball_x 在中段窗口内方差很小，未做回归；Phase 1 基线已经显示率随球接近而升高（距离驱动）。"
    )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if r2 > 0.2:
        lines.append(
            "细胞放电率对 ball_y 有可观测的依赖（R² > 0.2）。单细胞读出携带位置信息，"
            "阶段 3 的学习有可塑的空间。"
        )
    else:
        lines.append(
            "细胞放电率对 ball_y 的依赖很弱（R² ≤ 0.2）。当前固定权重下，率读出主要被 "
            "ball_x（距离）和反馈刺激驱动，单细胞难以把“球在哪”转成“往哪动”。"
            "这不是 bug，而是单细胞率读出的结构性限制；阶段 3 应把它作为负结果的一部分，"
            "并在阶段 4 用两池差分读出（up/down）来消除共同驱动。"
        )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `fig_diag_rate_vs_y.png`")
    lines.append("- `fig_diag_weights.png`")
    lines.append("")
    (outdir / "diagnostic.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"n_rallies={len(pts)} mean_rate={y.mean():.1f} Hz")
    print(f"ball_y: slope={slope:.2f} R2={r2:.3f} r={r:.3f}")
    print(f"Outputs written to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
