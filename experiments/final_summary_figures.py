"""最终报告汇总图：跨阶段机制筛查、信息-行为关系与递归网络 Gate。

读取各阶段 summary_by_condition.csv 与 results/phase7_7a/*/summary.csv，
输出到 results/figures/：
    fig_final_protocol.png       闭环协议示意
    fig_final_rally.png          关键条件的行为（rally）对比
    fig_final_info.png           impact corr vs rally（信息质量未必预测行为）
    fig_final_conditions.png     所有机制条件的行为分布（点图 + static 参照）
    fig_final_timing.png         early → late 信息相关的变化（信息到达时刻）
    fig_final_saturation.png     权重饱和、信用梯度与行为/信息的关系
    fig_phase7a_rec_ei.png       递归 E-I 的 w_ee 校准与 Gate 统计
只读结果文件，不重跑仿真，不改任何参数。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "P4": ROOT / "results/phase4_600/summary_by_condition.csv",
    "P0": ROOT / "results/phase5_bg_noise_600/summary_by_condition.csv",
    "P1": ROOT / "results/phase5_local_credit_600/summary_by_condition.csv",
    "P2": ROOT / "results/phase5_dynamic_homeostasis_600/summary_by_condition.csv",
    "P3": ROOT / "results/phase5_stp_600/summary_by_condition.csv",
    "P4net": ROOT / "results/phase5_ten_cell_600/summary_by_condition.csv",
    "P5": ROOT / "results/phase5_pd_readout_600/summary_by_condition.csv",
}

PHASE_COLOR = {
    "P4": "#6b7280",
    "P0": "#0f766e",
    "P1": "#2563eb",
    "P2": "#ea580c",
    "P3": "#16a34a",
    "P4net": "#7c3aed",
    "P5": "#db2777",
}

# 行为对比图的关键条件
KEY = [
    ("phase4_pushpull_static", "2-cell static", "P4", "#6b7280"),
    ("phase4_symmetric_static", "2-cell symmetric", "P4", "#9ca3af"),
    ("phase4_pushpull_3b_no_hs", "2-cell 3b no HS", "P4", "#4b5563"),
    ("phase4_pushpull_local_3b_no_hs", "P1 local (no HS)", "P1", "#2563eb"),
    ("phase4_pushpull_local_3b_dyn", "P2 local + dyn", "P2", "#ea580c"),
    ("phase4_pushpull_local_3b_no_hs_stp", "P3 local + STP", "P3", "#16a34a"),
    ("phase5_net_static", "P4 net static", "P4net", "#7c3aed"),
    ("phase5_net_local_no_hs_3b", "P4 net local", "P4net", "#a855f7"),
    ("phase4_pushpull_local_3b_no_hs_pd", "P5 local + PD", "P5", "#db2777"),
]

# 条件分布图：每个阶段选一个代表条件（避免同名条件重复）
DIST = [
    ("P4", "phase4_pushpull_static", "2-cell static"),
    ("P4", "phase4_symmetric_static", "2-cell symmetric"),
    ("P4", "phase4_pushpull_3b", "2-cell 3b (global D)"),
    ("P4", "phase4_pushpull_3b_no_hs", "2-cell 3b no HS"),
    ("P0", "phase4_pushpull_3b", "P0 3b + noise"),
    ("P1", "phase4_pushpull_local_3b_no_hs", "P1 local no HS"),
    ("P2", "phase4_pushpull_local_3b_dyn", "P2 local + dyn"),
    ("P2", "phase4_pushpull_dyn_3b", "P2 dyn (global D)"),
    ("P3", "phase4_pushpull_local_3b_no_hs_stp", "P3 local + STP"),
    ("P3", "phase4_pushpull_static_stp", "P3 static + STP"),
    ("P4net", "phase5_net_static", "P4 10-cell static"),
    ("P4net", "phase5_net_local_no_hs_3b", "P4 10-cell local"),
    ("P4net", "phase5_net_global_no_hs_3b", "P4 10-cell global"),
    ("P5", "phase4_pushpull_static_pd", "P5 static + PD"),
    ("P5", "phase4_pushpull_local_3b_no_hs_pd", "P5 local + PD"),
]

TIMING = [
    ("P1", "phase4_pushpull_static", "2-cell static"),
    ("P1", "phase4_pushpull_local_3b_no_hs", "P1 local no HS"),
    ("P2", "phase4_pushpull_local_3b_dyn", "P2 local + dyn"),
    ("P3", "phase4_pushpull_local_3b_no_hs_stp", "P3 local + STP"),
    ("P4net", "phase5_net_static", "P4 10-cell static"),
]


# 信息图只标注互不重叠的代表点
LABEL_KEY = [
    ("phase4_pushpull_static", "2-cell static", "P4"),
    ("phase4_pushpull_3b_no_hs", "2-cell 3b no HS", "P4"),
    ("phase4_pushpull_local_3b_no_hs", "P1 local no HS", "P1"),
    ("phase4_pushpull_local_3b_dyn", "P2 local + dyn", "P2"),
    ("phase4_pushpull_local_3b_no_hs_stp", "P3 local + STP", "P3"),
    ("phase5_net_static", "P4 10-cell static", "P4net"),
    ("phase5_net_local_no_hs_3b", "P4 10-cell local", "P4net"),
]


def load_all() -> pd.DataFrame:
    frames = []
    for phase, path in SOURCES.items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["phase"] = phase
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def pick(df: pd.DataFrame, phase: str, cond: str):
    hit = df[(df["phase"] == phase) & (df["condition"] == cond)]
    return None if hit.empty else hit.iloc[0]


def draw_protocol() -> None:
    """闭环协议示意（不含数据，仅结构）。"""
    fig, ax = plt.subplots(figsize=(10.2, 3.4))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 3.4)
    ax.axis("off")

    boxes = [
        (0.10, 1.15, 1.45, 1.15, "8-channel\nplace code", "#e0f2fe"),
        (1.85, 1.15, 1.45, 1.15, "Sensory relay\nS1–S4", "#dbeafe"),
        (3.60, 1.05, 1.75, 1.35, "Network\n2 / 10 / 22 cells", "#ede9fe"),
        (5.65, 1.15, 1.45, 1.15, "Motor pools\nUp / Down", "#fce7f3"),
        (7.40, 1.15, 1.35, 1.15, "Paddle\nv = k·Δr", "#fde68a"),
        (9.05, 1.15, 1.05, 1.15, "Pong\nenv", "#f3f4f6"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.03,rounding_size=0.08",
                linewidth=1.0, edgecolor="#374151", facecolor=color,
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5)

    for i in range(len(boxes) - 1):
        x0 = boxes[i][0] + boxes[i][2]
        x1 = boxes[i + 1][0]
        y = boxes[i][1] + boxes[i][3] / 2
        ax.add_patch(
            FancyArrowPatch(
                (x0 + 0.02, y), (x1 - 0.02, y),
                arrowstyle="-|>", mutation_scale=10, color="#374151", lw=1.1,
            )
        )

    # 反馈回路：从 Pong 底部向下、向左、再向上进入网络
    ax.plot([9.58, 9.58], [1.15, 0.42], color="#b91c1c", lw=1.2)
    ax.plot([9.58, 3.62], [0.42, 0.42], color="#b91c1c", lw=1.2)
    ax.add_patch(
        FancyArrowPatch(
            (3.62, 0.42), (3.62, 1.03),
            arrowstyle="-|>", mutation_scale=11, color="#b91c1c", lw=1.2,
        )
    )
    ax.text(
        6.6, 0.22,
        "hit: +100 Hz / 100 ms   ·   miss: +5 Hz / 4 s + rest",
        fontsize=8, color="#b91c1c", ha="center",
    )
    ax.text(
        5.2, 3.05,
        "Closed loop: 10 ms tick, all plasticity local (STDP + eligibility + homeostasis)",
        fontsize=9, ha="center", color="#111827",
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_final_protocol.png", dpi=200)
    plt.close(fig)


def fig_rally(df: pd.DataFrame) -> None:
    rows = []
    for cond, label, phase, color in KEY:
        r = pick(df, phase, cond)
        if r is None:
            continue
        sd = float(r["avg_rally_sd"]) if not pd.isna(r["avg_rally_sd"]) else 0.0
        rows.append((label, float(r["avg_rally_mean"]), sd, color))
    labels = [r[0] for r in rows]
    means = np.array([r[1] for r in rows])
    sds = np.array([r[2] for r in rows])
    colors = [r[3] for r in rows]

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    y = np.arange(len(rows))
    ax.barh(y, means, xerr=sds, color=colors, alpha=0.9, capsize=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("average rally length (600 s, 15 seeds)")
    ax.set_xlim(0, max(0.32, float(means.max()) + float(sds.max()) + 0.04))
    for i, (m, sd) in enumerate(zip(means, sds)):
        ax.text(m + sd + 0.006, i, f"{m:.3f}", va="center", fontsize=8)
    ax.axvline(
        float(pick(df, "P4", "phase4_pushpull_static")["avg_rally_mean"]),
        color="#6b7280", ls="--", lw=1,
    )
    ax.set_title("Behavior across mechanism lines: nothing beats hand-wired push-pull")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_final_rally.png", dpi=200)
    plt.close(fig)


def fig_info(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for phase, group in df.groupby("phase"):
        ax.scatter(
            group["impact_corr_mean"],
            group["avg_rally_mean"],
            s=44, alpha=0.85,
            color=PHASE_COLOR.get(phase, "#111827"),
            label=phase,
        )
    for cond, label, phase in LABEL_KEY:
        r = pick(df, phase, cond)
        if r is None:
            continue
        ax.annotate(
            label,
            (float(r["impact_corr_mean"]), float(r["avg_rally_mean"])),
            textcoords="offset points", xytext=(6, 4), fontsize=7.2,
        )
    ax.axhline(1 / 7, color="#9ca3af", ls="--", lw=1)
    ax.text(-0.62, 1 / 7 + 0.004, "frozen paddle ≈ 1/7", fontsize=7.5, color="#6b7280")
    ax.set_xlabel("impact-rate correlation with ball y")
    ax.set_ylabel("average rally length")
    ax.set_title("Information quality does not predict behavior")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_final_info.png", dpi=200)
    plt.close(fig)


def fig_conditions(df: pd.DataFrame) -> None:
    rows = []
    for phase, cond, label in DIST:
        r = pick(df, phase, cond)
        if r is None:
            continue
        rows.append(
            (
                phase, label,
                float(r["avg_rally_mean"]),
                float(r["avg_rally_sd"]) if not pd.isna(r["avg_rally_sd"]) else 0.0,
            )
        )
    labels = [r[1] for r in rows]
    means = np.array([r[2] for r in rows])
    sds = np.array([r[3] for r in rows])
    colors = [PHASE_COLOR[r[0]] for r in rows]

    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    y = np.arange(len(rows))
    ax.errorbar(
        means, y, xerr=sds, fmt="o", ecolor="#9ca3af", elinewidth=0.8,
        capsize=2, ms=0,
    )
    for i, (m, c) in enumerate(zip(means, colors)):
        ax.plot(m, i, "o", color=c, ms=8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    static_mean = float(pick(df, "P4", "phase4_pushpull_static")["avg_rally_mean"])
    ax.axvline(static_mean, color="#6b7280", ls="--", lw=1)
    ax.set_xlabel("average rally length (mean ± SD over seeds)")
    ax.set_title("Every mechanism line lands around the static reference")
    handles = [
        plt.Line2D([], [], marker="o", ls="", color=c, label=p, ms=7)
        for p, c in PHASE_COLOR.items()
        if any(r[0] == p for r in rows)
    ]
    ax.legend(handles=handles, fontsize=7.5, frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_final_conditions.png", dpi=200)
    plt.close(fig)


def fig_timing(df: pd.DataFrame) -> None:
    rows = []
    for phase, cond, label in TIMING:
        r = pick(df, phase, cond)
        if r is None:
            continue
        rows.append(
            (
                label,
                float(r["early_norm_corr"]),
                float(r["late_norm_corr"]),
                PHASE_COLOR[phase],
            )
        )
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    y = np.arange(len(rows))
    for i, (label, early, late, color) in enumerate(rows):
        ax.plot([early, late], [i, i], color="#d1d5db", lw=2, zorder=1)
        ax.plot(early, i, "o", color=color, ms=8, zorder=2)
        ax.plot(late, i, "s", color=color, ms=7, zorder=2)
        ax.text(
            max(early, late) + 0.02, i,
            f"{early:.2f} → {late:.2f}", va="center", fontsize=7.5,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("correlation between normalized rate difference and ball_y")
    ax.set_title("Early (ball far) vs late (ball near) information")
    ax.legend(
        handles=[
            plt.Line2D([], [], marker="o", ls="", color="#374151", label="early", ms=7),
            plt.Line2D([], [], marker="s", ls="", color="#374151", label="late", ms=6),
        ],
        fontsize=7.5, frameon=False, loc="lower right",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_final_timing.png", dpi=200)
    plt.close(fig)


def fig_saturation(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.7))
    ax = axes[0]
    for phase, group in df.groupby("phase"):
        ax.scatter(
            group["at_max_up"], group["avg_rally_mean"],
            s=40, alpha=0.85, color=PHASE_COLOR.get(phase, "#111827"),
        )
    ax.set_xlabel("fraction of Up weights at w_max")
    ax.set_ylabel("average rally length")
    ax.set_title("Weight saturation vs behavior")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    for phase, group in df.groupby("phase"):
        ax.scatter(
            group["w_diff_corr_final"], group["impact_corr_mean"],
            s=40, alpha=0.85, color=PHASE_COLOR.get(phase, "#111827"),
        )
    ax.axhline(0.0, color="#9ca3af", lw=0.8, ls=":")
    ax.axvline(0.0, color="#9ca3af", lw=0.8, ls=":")
    ax.set_xlabel("w_diff channel correlation (credit gradient)")
    ax.set_ylabel("impact-rate correlation (information)")
    ax.set_title("Correct gradient ≠ usable information")
    ax.spines[["top", "right"]].set_visible(False)

    handles = [
        plt.Line2D([], [], marker="o", ls="", color=c, label=p, ms=6)
        for p, c in PHASE_COLOR.items()
        if (df["phase"] == p).any()
    ]
    fig.legend(
        handles=handles, fontsize=7.5, frameon=False, loc="lower center", ncol=6,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "fig_final_saturation.png", dpi=200)
    plt.close(fig)


def fig_rec_ei() -> None:
    groups = ["w0", "w5", "w10", "w20"]
    frames = []
    for g in groups:
        p = ROOT / "results" / "phase7_7a" / g / "summary.csv"
        if p.exists():
            frames.append(pd.read_csv(p))
    if not frames:
        return
    d = pd.concat(frames, ignore_index=True)
    agg = d.groupby("rec_w_ee_nS").agg(
        e=("rec_e_mean_rate_hz", "mean"),
        i=("rec_i_mean_rate_hz", "mean"),
        mx=("rec_max_cell_rate_hz", "mean"),
        cv=("rec_e_cv_isi_mean", "mean"),
        pc=("rec_e_pair_corr_mean", "mean"),
        dr=("rec_e_rate_drift", "mean"),
    ).reset_index()

    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.7))
    ax[0].axhspan(5, 25, color="#d1fae5", alpha=0.9, label="Gate band 5–25 Hz")
    ax[0].plot(agg["rec_w_ee_nS"], agg["e"], "o-", color="#7c3aed", label="E rate")
    ax[0].plot(agg["rec_w_ee_nS"], agg["i"], "s--", color="#2563eb", label="I rate")
    ax[0].plot(agg["rec_w_ee_nS"], agg["mx"], "^:", color="#dc2626", label="max cell")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("w_ee (nS)")
    ax[0].set_ylabel("play rate (Hz, log)")
    ax[0].set_xticks(agg["rec_w_ee_nS"])
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_title("No operating point inside the band")
    ax[0].spines[["top", "right"]].set_visible(False)

    ax[1].plot(agg["rec_w_ee_nS"], agg["cv"], "o-", color="#16a34a", label="CV(ISI)")
    ax[1].plot(agg["rec_w_ee_nS"], agg["pc"], "s--", color="#ea580c", label="pair corr")
    ax[1].plot(agg["rec_w_ee_nS"], agg["dr"], "^:", color="#6b7280", label="rate drift")
    ax[1].axhline(0.5, color="#16a34a", lw=0.8, ls=":")
    ax[1].axhline(0.8, color="#ea580c", lw=0.8, ls=":")
    ax[1].axhline(0.3, color="#6b7280", lw=0.8, ls=":")
    ax[1].set_xlabel("w_ee (nS)")
    ax[1].set_ylabel("Gate statistic")
    ax[1].set_xticks(agg["rec_w_ee_nS"])
    ax[1].legend(fontsize=7, frameon=False)
    ax[1].set_title("At w_ee=10 nS the network ignites and synchronizes")
    ax[1].spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_phase7a_rec_ei.png", dpi=200)
    plt.close(fig)


def main() -> None:
    df = load_all()
    if df.empty:
        raise SystemExit("no summary_by_condition.csv found")
    draw_protocol()
    fig_rally(df)
    fig_info(df)
    fig_conditions(df)
    fig_timing(df)
    fig_saturation(df)
    fig_rec_ei()
    for name in (
        "fig_final_protocol.png",
        "fig_final_rally.png",
        "fig_final_info.png",
        "fig_final_conditions.png",
        "fig_final_timing.png",
        "fig_final_saturation.png",
        "fig_phase7a_rec_ei.png",
    ):
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
