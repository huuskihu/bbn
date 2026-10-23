r"""
阶段 1：静态闭环基线。

运行：
    .\.venv\Scripts\python.exe experiments\phase1_static_loop.py --config config\phase1.yaml

输出：
    results/phase1/summary.csv
    results/phase1/phase1_report.md
    results/phase1/fig_rally_length.png
    results/phase1/fig_trace_full.png
    results/phase1/fig_rate_by_condition.png
    results/phase1/traces/<condition>_seed<seed>.csv

注意：
    - 本阶段没有可塑性；权重固定，细胞不会学习。
    - full_feedback / no_feedback / silent / random_paddle / always_up / always_down 是对照。
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
    cell_params = HHParams(
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
    phase1_cfg = Phase1Config(
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

    pc = cfg["pong"]
    pong_cfg = PongConfig(
        ball_speed=float(pc["ball_speed"]),
        paddle_bins=float(pc["paddle_bins"]),
        hit_tolerance=float(pc["hit_tolerance"]),
        y_min=float(pc["y_min"]),
        y_max=float(pc["y_max"]),
        initial_paddle_y=float(pc["initial_paddle_y"]),
    )

    conditions = list(cfg["experiment"]["conditions"])
    seeds = [int(s) for s in cfg["experiment"]["seeds"]]
    return cell_params, phase1_cfg, pong_cfg, conditions, seeds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase1.yaml")
    parser.add_argument("--outdir", default="results/phase1")
    parser.add_argument("--duration", type=float, default=None, help="覆盖 duration_s")
    parser.add_argument("--seeds", default=None, help="逗号分隔，如 0,1")
    parser.add_argument("--conditions", default=None, help="逗号分隔")
    args = parser.parse_args()

    cell_params, phase1_cfg, pong_cfg, conditions, seeds = load_config(args.config)
    if args.duration is not None:
        phase1_cfg.duration_s = float(args.duration)
    if args.seeds:
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if args.conditions:
        conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    outdir = Path(args.outdir)
    trace_dir = outdir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    traces: dict[tuple[str, int], pd.DataFrame] = {}

    for condition in conditions:
        for seed in seeds:
            print(f"[run] {condition} seed={seed} duration={phase1_cfg.duration_s:.0f}s")
            loop = Phase1Loop(
                condition=condition,
                cfg=phase1_cfg,
                cell_params=cell_params,
                pong_cfg=pong_cfg,
                seed=seed,
            )
            metrics, trace = loop.run()
            metrics["seed"] = seed
            rows.append(metrics)

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
            df.to_csv(trace_dir / f"{condition}_seed{seed}.csv", index=False)
            traces[(condition, seed)] = df

            print(
                f"  hits={metrics['hits']} misses={metrics['misses']} "
                f"avg_rally={metrics['average_rally_length']:.2f} "
                f"mean_rate={metrics['mean_rate_hz']:.1f}Hz"
            )

    summary = pd.DataFrame(rows)
    summary.to_csv(outdir / "summary.csv", index=False)

    # 汇总表
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
            paddle_range_mean=("paddle_range", "mean"),
        )
        .reset_index()
    )
    agg.to_csv(outdir / "summary_by_condition.csv", index=False)

    # 图 1：平均 rally length
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(agg))
    ax.bar(x, agg["avg_rally_mean"], yerr=agg["avg_rally_sd"].fillna(0), capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(agg["condition"], rotation=20, ha="right")
    ax.set_ylabel("Average rally length")
    ax.set_title("Phase 1 static baseline: rally length by condition")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_rally_length.png", bbox_inches="tight")
    plt.close(fig)

    # 图 2：full_feedback seed 0 的轨迹
    key = ("full_feedback", seeds[0])
    if key in traces:
        df = traces[key]
        fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
        axes[0].plot(df["t_ms"] / 1000.0, df["ball_y"], label="ball y", lw=1.0)
        axes[0].plot(df["t_ms"] / 1000.0, df["paddle_y"], label="paddle y", lw=1.0)
        axes[0].set_ylabel("Position (bins)")
        axes[0].legend(frameon=False)
        axes[0].grid(alpha=0.3)

        axes[1].plot(
            df["t_ms"] / 1000.0, df["rate_hz"], lw=0.5, alpha=0.35, label="instantaneous"
        )
        axes[1].plot(df["t_ms"] / 1000.0, df["rate_used"], lw=1.0, label="smoothed")
        axes[1].axhline(phase1_cfg.reference_rate_hz, color="tab:red", ls="--", lw=0.8)
        axes[1].set_xlabel("Time (s)")
        axes[1].set_ylabel("Cell rate (Hz)")
        axes[1].legend(frameon=False, fontsize=8)
        axes[1].grid(alpha=0.3)
        fig.suptitle(f"Full feedback, seed {seeds[0]}")
        fig.tight_layout()
        fig.savefig(outdir / "fig_trace_full.png", bbox_inches="tight")
        plt.close(fig)

    # 图 3：各条件的放电率分布
    fig, ax = plt.subplots(figsize=(8, 4))
    rate_data = []
    labels = []
    for condition in conditions:
        for seed in seeds:
            key = (condition, seed)
            if key in traces:
                rate_data.append(traces[key]["rate_used"].to_numpy(dtype=float))
                labels.append(condition)
    if rate_data:
        # 按条件合并
        merged = {}
        for label, arr in zip(labels, rate_data):
            merged.setdefault(label, []).append(arr)
        positions = []
        data = []
        for i, label in enumerate(merged):
            data.append(np.concatenate(merged[label]))
            positions.append(i)
        ax.boxplot(data, positions=positions, widths=0.6, showfliers=False)
        ax.set_xticks(positions)
        ax.set_xticklabels(list(merged.keys()), rotation=20, ha="right")
        ax.set_ylabel("Cell firing rate (Hz)")
        ax.set_title("Rate distribution by condition")
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_rate_by_condition.png", bbox_inches="tight")
    plt.close(fig)

    # 报告
    lines = []
    lines.append("# Phase 1 Static Baseline Report")
    lines.append("")
    lines.append(f"- Config: `{args.config}`")
    lines.append(f"- Duration per run: {phase1_cfg.duration_s:.1f} s")
    lines.append(f"- Seeds: {seeds}")
    lines.append(f"- Conditions: {conditions}")
    lines.append("")
    lines.append("## Summary by condition")
    lines.append("")
    lines.append(
        "| condition | hits | misses | avg rally | aces | long rallies | mean rate (Hz) | paddle range |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.hits_mean:.1f} | {row.misses_mean:.1f} | "
            f"{row.avg_rally_mean:.2f} ± {0 if pd.isna(row.avg_rally_sd) else row.avg_rally_sd:.2f} | "
            f"{row.aces_mean:.1f} | {row.long_rallies_mean:.1f} | "
            f"{row.mean_rate_mean:.1f} | {row.paddle_range_mean:.2f} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- 本阶段没有可塑性；所有条件共用固定突触权重。")
    lines.append("- `full_feedback` 命中给 100 Hz/100 ms 全通道可预测刺激；未命中给 5 Hz/4 s 随机不可预测刺激 + 4 s rest。")
    lines.append("- `no_feedback` 不给任何反馈；`silent` 未命中只给 4 s rest；`random_paddle`/`always_up`/`always_down` 忽略细胞输出。")
    lines.append("- 静态基线不应显示学习；它用来验证闭环、编码、读出和对照是否工作。")
    lines.append("")
    (outdir / "phase1_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\nSummary by condition:")
    print(agg.to_string(index=False))
    print(f"\nOutputs written to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
