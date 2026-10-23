r"""
阶段 3：单细胞闭环学习。

运行：
    .\.venv\Scripts\python.exe experiments\phase3_single_cell.py --config config\phase3.yaml

输出：
    results/phase3/summary.csv
    results/phase3/summary_by_condition.csv
    results/phase3/phase3_report.md
    results/phase3/fig_rally_by_condition.png
    results/phase3/fig_weight_change.png
    results/phase3/fig_weights_3b.png
    results/phase3/fig_trace_3b.png
    results/phase3/traces/<condition>_seed<seed>.csv

注意：
    - 3a 是字面 DishBrain：STDP + 稳态，反馈只作刺激。
    - 3b 是三因子：资格迹 + 可预测/不可预测调制。
    - 本阶段不调参凑曲线；负结果如实记录。
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
from src.loop.phase3_loop import Phase3Config, Phase3Loop


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

    p = cfg["phase3"]
    pc = Phase3Config(
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
        syn_tau_ms=float(p["syn_tau_ms"]),
        E_syn_mV=float(p["E_syn_mV"]),
        predictable_rate_hz=float(p["predictable_rate_hz"]),
        predictable_duration_ms=float(p["predictable_duration_ms"]),
        predictable_weight_nS=float(p["predictable_weight_nS"]),
        unpredictable_rate_hz=float(p["unpredictable_rate_hz"]),
        unpredictable_duration_s=float(p["unpredictable_duration_s"]),
        unpredictable_weight_nS=float(p["unpredictable_weight_nS"]),
        rest_after_miss_s=float(p["rest_after_miss_s"]),
        a_plus=float(p["a_plus"]),
        a_minus=float(p["a_minus"]),
        tau_plus_ms=float(p["tau_plus_ms"]),
        tau_minus_ms=float(p["tau_minus_ms"]),
        w_min=float(p["w_min"]),
        w_max=float(p["w_max"]),
        w_init=float(p["w_init"]),
        w_jitter=float(p["w_jitter"]),
        tau_e_ms=float(p["tau_e_ms"]),
        eta=float(p["eta"]),
        reward_plus=float(p["reward_plus"]),
        reward_minus=float(p["reward_minus"]),
        homeostasis_enabled=bool(p["homeostasis_enabled"]),
        target_rate_hz=float(p["target_rate_hz"]),
        hs_alpha=float(p["hs_alpha"]),
        hs_interval_s=float(p["hs_interval_s"]),
        hs_w_min=float(p["hs_w_min"]),
        hs_w_max=float(p["hs_w_max"]),
        shuffle_rate_hz=float(p["shuffle_rate_hz"]),
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

    conditions = list(cfg["experiment"]["conditions"])
    seeds = [int(s) for s in cfg["experiment"]["seeds"]]
    return cell, pc, pong, conditions, seeds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase3.yaml")
    parser.add_argument("--outdir", default="results/phase3")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--conditions", default=None)
    args = parser.parse_args()

    cell, pc, pong, conditions, seeds = load_config(args.config)
    if args.duration is not None:
        pc.duration_s = float(args.duration)
    if args.seeds:
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if args.conditions:
        conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    outdir = Path(args.outdir)
    trace_dir = outdir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    traces = {}
    weights = {}

    for condition in conditions:
        for seed in seeds:
            print(f"[run] {condition} seed={seed} duration={pc.duration_s:.0f}s")
            loop = Phase3Loop(
                condition=condition,
                cfg=pc,
                cell_params=cell,
                pong_cfg=pong,
                seed=seed,
            )
            metrics, trace = loop.run()
            metrics["seed"] = seed
            rows.append(metrics)
            weights[(condition, seed)] = (loop.w_initial.copy(), loop.syn.w.copy())

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
                    "w_mean",
                    "w_min",
                    "w_max",
                    "reward_d",
                ],
            )
            df.to_csv(trace_dir / f"{condition}_seed{seed}.csv", index=False)
            traces[(condition, seed)] = df

            print(
                f"  hits={metrics['hits']} misses={metrics['misses']} "
                f"avg_rally={metrics['average_rally_length']:.2f} "
                f"w_mean {metrics['w_initial_mean']:.2f}->{metrics['w_final_mean']:.2f} "
                f"|dw|={metrics['w_delta_absmean']:.4f}"
            )

    summary = pd.DataFrame(rows)
    summary.to_csv(outdir / "summary.csv", index=False)

    agg = (
        summary.groupby("condition")
        .agg(
            hits_mean=("hits", "mean"),
            misses_mean=("misses", "mean"),
            avg_rally_mean=("average_rally_length", "mean"),
            avg_rally_sd=("average_rally_length", "std"),
            aces_mean=("aces", "mean"),
            long_rallies_mean=("long_rallies", "mean"),
            mean_rate_mean=("mean_rate_hz", "mean"),
            w_initial_mean=("w_initial_mean", "mean"),
            w_final_mean=("w_final_mean", "mean"),
            w_final_sd=("w_final_std", "mean"),
            w_delta_absmean=("w_delta_absmean", "mean"),
            w_initial_corr=("w_initial_channel_corr", "mean"),
            w_channel_corr=("w_channel_corr", "mean"),
        )
        .reset_index()
    )
    agg.to_csv(outdir / "summary_by_condition.csv", index=False)

    # 图 1：rally length
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(agg))
    ax.bar(x, agg["avg_rally_mean"], yerr=agg["avg_rally_sd"].fillna(0), capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(agg["condition"], rotation=25, ha="right")
    ax.set_ylabel("Average rally length")
    ax.set_title("Phase 3: behavior by condition")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_rally_by_condition.png", bbox_inches="tight")
    plt.close(fig)

    # 图 2：权重变化幅度
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x, agg["w_delta_absmean"])
    ax.set_xticks(x)
    ax.set_xticklabels(agg["condition"], rotation=25, ha="right")
    ax.set_ylabel("Mean |Δw| (efficacy)")
    ax.set_title("Phase 3: weight change by condition")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_weight_change.png", bbox_inches="tight")
    plt.close(fig)

    # 图 3：phase3b_full seed 0 的初始/最终权重
    key = ("phase3b_full", seeds[0])
    if key in weights:
        w0, w1 = weights[key]
        fig, ax = plt.subplots(figsize=(7, 3.5))
        xx = np.arange(1, 9)
        ax.bar(xx - 0.18, w0, width=0.36, label="initial")
        ax.bar(xx + 0.18, w1, width=0.36, label="final")
        ax.set_xlabel("Sensory channel (ball y bin)")
        ax.set_ylabel("Synaptic efficacy")
        ax.set_title(f"phase3b_full seed {seeds[0]}: weights")
        ax.legend(frameon=False)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(outdir / "fig_weights_3b.png", bbox_inches="tight")
        plt.close(fig)

        # 图 4：轨迹
        df = traces[key]
        fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
        axes[0].plot(df["t_ms"] / 1000.0, df["ball_y"], lw=0.8, label="ball y")
        axes[0].plot(df["t_ms"] / 1000.0, df["paddle_y"], lw=0.8, label="paddle y")
        axes[0].set_ylabel("Position")
        axes[0].legend(frameon=False)
        axes[0].grid(alpha=0.3)

        axes[1].plot(df["t_ms"] / 1000.0, df["rate_used"], lw=0.8)
        axes[1].axhline(pc.reference_rate_hz, color="tab:red", ls="--", lw=0.8)
        axes[1].set_ylabel("Rate (Hz)")
        axes[1].grid(alpha=0.3)

        axes[2].plot(df["t_ms"] / 1000.0, df["w_mean"], lw=1.0)
        axes[2].set_ylabel("Mean efficacy")
        axes[2].set_xlabel("Time (s)")
        axes[2].grid(alpha=0.3)
        fig.suptitle(f"phase3b_full seed {seeds[0]}")
        fig.tight_layout()
        fig.savefig(outdir / "fig_trace_3b.png", bbox_inches="tight")
        plt.close(fig)

    # 报告
    lines = []
    lines.append("# Phase 3: Single-cell closed-loop learning")
    lines.append("")
    lines.append(f"- Config: `{args.config}`")
    lines.append(f"- Duration: {pc.duration_s:.1f} s; seeds: {seeds}")
    lines.append(f"- Conditions: {conditions}")
    lines.append("")
    lines.append("## Behavior + weights")
    lines.append("")
    lines.append(
        "| condition | avg rally | hits | misses | mean rate | w init | w final | |Δw| | y corr init→final |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.avg_rally_mean:.3f} ± {0 if pd.isna(row.avg_rally_sd) else row.avg_rally_sd:.3f} | "
            f"{row.hits_mean:.1f} | {row.misses_mean:.1f} | {row.mean_rate_mean:.1f} | "
            f"{row.w_initial_mean:.3f} | {row.w_final_mean:.3f} | "
            f"{row.w_delta_absmean:.4f} | {row.w_initial_corr:+.3f} → {row.w_channel_corr:+.3f} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- 3a = 字面 DishBrain（STDP + 稳态，反馈只作刺激）；3b = 资格迹 + 三因子。")
    lines.append("- 对照：no_feedback / silent / shuffled / static / random_paddle。")
    lines.append("- 本报告只呈现结果，不调参凑曲线；负结果按预注册记录。")
    lines.append("- Phase 1 诊断显示单细胞率几乎不携带 ball_y；因此 3b 的行为改善预期很弱。")
    lines.append("")
    (outdir / "phase3_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\nSummary by condition:")
    print(agg.to_string(index=False))
    print(f"\nOutputs written to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
