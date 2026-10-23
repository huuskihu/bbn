r"""
阶段 4：两池差分读出（push-pull）+ 2 细胞。

运行（完整）：
    .\.venv\Scripts\python.exe experiments\phase4_network.py --config config\phase4.yaml --jobs 8

冒烟：
    .\.venv\Scripts\python.exe experiments\phase4_network.py --config config\phase4.yaml `
        --seeds 0 --duration 30 --outdir results\phase4_smoke

输出：
    results/phase4/summary.csv
    results/phase4/summary_by_condition.csv
    results/phase4/phase4_report.md
    results/phase4/fig_rally_by_condition.png
    results/phase4/fig_readout_corr.png
    results/phase4/fig_impact_scatter.png
    results/phase4/fig_weights_pushpull.png
    results/phase4/traces/<condition>_seed<seed>.csv
    results/phase4/impacts/<condition>_seed<seed>.csv
    results/phase4/weights/<condition>_seed<seed>.csv

注意：
    - 串行/并行结果一致；每个 worker 只写自己的文件，主进程汇总。
    - 不调参凑曲线；负结果如实记录。
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
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
from src.loop.phase4_loop import Phase4Config, Phase4Loop

TRACE_COLUMNS = [
    "t_ms",
    "ball_x",
    "ball_y",
    "paddle_y",
    "rate_up_hz",
    "rate_down_hz",
    "rate_up_used",
    "rate_down_used",
    "rate_diff_hz",
    "rate_diff_used",
    "velocity",
    "event",
    "spikes_up",
    "spikes_down",
    "w_up_mean",
    "w_down_mean",
    "w_diff_mean",
    "reward_d",
    "playing",
    "spikes_inh",
    "inh_rate_used",
]

IMPACT_COLUMNS = [
    "t_ms",
    "ball_y",
    "rate_diff_pre",
    "rate_up_pre",
    "rate_down_pre",
    "hit",
]

WEIGHT_COLUMNS = ["t_ms"] + [f"w_up_{i}" for i in range(1, 9)] + [
    f"w_down_{i}" for i in range(1, 9)
]


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

    p = cfg["phase4"]
    pc = Phase4Config(
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
        pushpull_span=float(p["pushpull_span"]),
        random_init_jitter=float(p["random_init_jitter"]),
        snapshot_interval_s=float(p["snapshot_interval_s"]),
        inhibitory_enabled=bool(p.get("inhibitory_enabled", False)),
        inh_input_weight=float(p.get("inh_input_weight", 1.0)),
        inh_weight_nS=float(p.get("inh_weight_nS", 10.0)),
        inh_tau_ms=float(p.get("inh_tau_ms", 10.0)),
        E_inh_mV=float(p.get("E_inh_mV", -80.0)),
        cross_inhibition_enabled=bool(p.get("cross_inhibition_enabled", False)),
        cross_rec_weight_nS=float(p.get("cross_rec_weight_nS", 40.0)),
        cross_rec_tau_ms=float(p.get("cross_rec_tau_ms", 5.0)),
        tuned_inhibition_enabled=bool(p.get("tuned_inhibition_enabled", False)),
        tuned_inh_gain=float(p.get("tuned_inh_gain", 1.0)),
        normalized_readout=bool(p.get("normalized_readout", False)),
        velocity_gain_norm=float(p.get("velocity_gain_norm", 5.0)),
        norm_eps_hz=float(p.get("norm_eps_hz", 1e-3)),
        bg_noise_hz=float(p.get("bg_noise_hz", 3.0)),
        bg_noise_weight_nS=float(p.get("bg_noise_weight_nS", 40.0)),
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


def _perm_test(a, b, rng, n_perm: int = 20000):
    """两组置换检验（打乱条件标签）；返回 mean diff, p, n_a, n_b。

    注意：不能用按 seed 配对。各条件的动作不同 → Poisson 感觉事件数不同 →
    RNG 流在第一个 tick 后就分叉，seed 标签不再共享同一批随机数。
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    obs = float(np.mean(a) - np.mean(b))
    pool = np.concatenate([a, b])
    n_a = len(a)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        d = float(np.mean(pool[:n_a]) - np.mean(pool[n_a:]))
        if abs(d) >= abs(obs):
            count += 1
    p = (count + 1) / (n_perm + 1)
    return obs, p, n_a, len(b)


def _run_one(payload):
    """一个 (condition, seed) run；只写自己的文件，返回 metrics。"""
    (
        condition,
        seed,
        cell,
        pc,
        pong,
        trace_dir,
        impact_dir,
        weight_dir,
        trace_stride,
    ) = payload
    t0 = time.time()

    loop = Phase4Loop(
        condition=condition,
        cfg=pc,
        cell_params=cell,
        pong_cfg=pong,
        seed=seed,
    )
    metrics, trace, impacts, weights = loop.run()
    metrics["wall_s"] = time.time() - t0

    df = pd.DataFrame(trace, columns=TRACE_COLUMNS)
    if trace_stride > 1:
        df = df.iloc[::trace_stride].reset_index(drop=True)
    df.to_csv(Path(trace_dir) / f"{condition}_seed{seed}.csv", index=False)

    if len(impacts):
        pd.DataFrame(impacts, columns=IMPACT_COLUMNS).to_csv(
            Path(impact_dir) / f"{condition}_seed{seed}.csv", index=False
        )
    pd.DataFrame(weights, columns=WEIGHT_COLUMNS).to_csv(
        Path(weight_dir) / f"{condition}_seed{seed}.csv", index=False
    )
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/phase4.yaml")
    parser.add_argument("--outdir", default="results/phase4")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--conditions", default=None)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument(
        "--velocity-gain",
        type=float,
        default=None,
        help="覆盖 Tier 1 velocity_gain（仅用于预注册的增益敏感性实验）",
    )
    parser.add_argument(
        "--rate-min",
        type=float,
        default=None,
        help="覆盖感觉率因子下限（Hz）；与 --rate-max 一起用于恒常率实验",
    )
    parser.add_argument(
        "--rate-max",
        type=float,
        default=None,
        help="覆盖感觉率因子上限（Hz）",
    )
    parser.add_argument(
        "--trace-stride",
        type=int,
        default=1,
        help="trace CSV 的降采样步长（>1 时每 N 个 tick 写一行；metrics 仍用全量数据）",
    )
    parser.add_argument(
        "--inhibitory",
        action="store_true",
        help="启用抑制性中间神经元（3 细胞版）",
    )
    parser.add_argument(
        "--inh-weight",
        type=float,
        default=None,
        help="覆盖抑制性突触权重（nS / I spike），用于校准",
    )
    parser.add_argument(
        "--cross-inhibition",
        action="store_true",
        help="启用交叉抑制（4 细胞：I_up 抑制 down，I_down 抑制 up）",
    )
    parser.add_argument(
        "--cross-rec-weight",
        type=float,
        default=None,
        help="覆盖 motor→I 的递归兴奋权重（nS / motor spike）",
    )
    parser.add_argument(
        "--tuned-inhibition",
        action="store_true",
        help="启用差分调谐抑制（I_up/I_down 接收 8 通道感觉并按 push-pull 调谐）",
    )
    parser.add_argument(
        "--tuned-gain",
        type=float,
        default=None,
        help="覆盖差分调谐抑制的输入增益",
    )
    parser.add_argument(
        "--ball-speed",
        type=float,
        default=None,
        help="覆盖球速（bins/s；0.5 = 2 s 回合，0.25 = 4 s 回合）",
    )
    parser.add_argument(
        "--normalized-readout",
        action="store_true",
        help="启用归一化读出 v = k_norm·(up−down)/(up+down+eps)",
    )
    parser.add_argument(
        "--gain-norm",
        type=float,
        default=None,
        help="覆盖归一化读出的增益（bins/s）",
    )
    parser.add_argument(
        "--bg-noise-hz",
        type=float,
        default=None,
        help="覆盖背景自发活动率（Hz；0 关闭）",
    )
    parser.add_argument(
        "--bg-noise-weight",
        type=float,
        default=None,
        help="覆盖背景事件权重（nS）",
    )
    parser.add_argument(
        "--net-em-weight",
        type=float,
        default=None,
        help="覆盖 E→motor 电导（nS；仅用于 v0.19.0 预注册校准）",
    )
    parser.add_argument(
        "--net-se-weight",
        type=float,
        default=None,
        help="覆盖 S→E/I 电导（nS；默认 10）",
    )
    parser.add_argument(
        "--lat-gain",
        type=float,
        default=None,
        help="覆盖延迟解码增益（bins/s per ms；6a 校准后冻结）",
    )
    parser.add_argument(
        "--rec-ee-weight",
        type=float,
        default=None,
        help="覆盖递归 E→E 电导（nS；仅用于 v0.22.0 7a 预注册校准）",
    )
    args = parser.parse_args()

    cell, pc, pong, conditions, seeds = load_config(args.config)
    if args.velocity_gain is not None:
        pc.velocity_gain = float(args.velocity_gain)
    if args.rate_min is not None:
        pc.rate_min_hz = float(args.rate_min)
    if args.rate_max is not None:
        pc.rate_max_hz = float(args.rate_max)
    if args.inhibitory:
        pc.inhibitory_enabled = True
    if args.inh_weight is not None:
        pc.inh_weight_nS = float(args.inh_weight)
    if args.cross_inhibition:
        pc.cross_inhibition_enabled = True
    if args.cross_rec_weight is not None:
        pc.cross_rec_weight_nS = float(args.cross_rec_weight)
    if args.tuned_inhibition:
        pc.tuned_inhibition_enabled = True
    if args.tuned_gain is not None:
        pc.tuned_inh_gain = float(args.tuned_gain)
    if args.ball_speed is not None:
        pong.ball_speed = float(args.ball_speed)
    if args.normalized_readout:
        pc.normalized_readout = True
    if args.gain_norm is not None:
        pc.velocity_gain_norm = float(args.gain_norm)
    if args.bg_noise_hz is not None:
        pc.bg_noise_hz = float(args.bg_noise_hz)
    if args.bg_noise_weight is not None:
        pc.bg_noise_weight_nS = float(args.bg_noise_weight)
    if args.net_em_weight is not None:
        pc.net_em_weight_nS = float(args.net_em_weight)
    if args.net_se_weight is not None:
        pc.net_se_weight_nS = float(args.net_se_weight)
    if args.lat_gain is not None:
        pc.lat_gain = float(args.lat_gain)
    if args.rec_ee_weight is not None:
        pc.rec_w_ee_nS = float(args.rec_ee_weight)
    if args.duration is not None:
        pc.duration_s = float(args.duration)
    if args.seeds:
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if args.conditions:
        conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    outdir = Path(args.outdir)
    trace_dir = outdir / "traces"
    impact_dir = outdir / "impacts"
    weight_dir = outdir / "weights"
    for d in (trace_dir, impact_dir, weight_dir):
        d.mkdir(parents=True, exist_ok=True)

    payloads = [
        (
            cond,
            seed,
            cell,
            pc,
            pong,
            trace_dir,
            impact_dir,
            weight_dir,
            max(1, int(args.trace_stride)),
        )
        for cond in conditions
        for seed in seeds
    ]

    rows = []
    t_start = time.time()
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = {ex.submit(_run_one, p): (p[0], p[1]) for p in payloads}
            done = 0
            for fut in as_completed(futures):
                cond, seed = futures[fut]
                m = fut.result()
                rows.append(m)
                done += 1
                print(
                    f"[{done}/{len(payloads)}] {cond} seed={seed} "
                    f"rally={m['average_rally_length']:.3f} "
                    f"corr(diff,y)={m['impact_rate_diff_corr']:+.3f} "
                    f"({m['wall_s']:.1f}s)"
                )
    else:
        for i, p in enumerate(payloads, 1):
            m = _run_one(p)
            rows.append(m)
            print(
                f"[{i}/{len(payloads)}] {m['condition']} seed={m['seed']} "
                f"rally={m['average_rally_length']:.3f} "
                f"corr(diff,y)={m['impact_rate_diff_corr']:+.3f} "
                f"({m['wall_s']:.1f}s)"
            )

    summary = pd.DataFrame(rows)
    summary = summary.sort_values(["condition", "seed"]).reset_index(drop=True)
    summary.to_csv(outdir / "summary.csv", index=False)

    agg = (
        summary.groupby("condition", sort=False)
        .agg(
            n_seeds=("seed", "count"),
            avg_rally_mean=("average_rally_length", "mean"),
            avg_rally_sd=("average_rally_length", "std"),
            hits_mean=("hits", "mean"),
            misses_mean=("misses", "mean"),
            aces_mean=("aces", "mean"),
            long_rallies_mean=("long_rallies", "mean"),
            mean_abs_velocity=("mean_abs_velocity", "mean"),
            mean_rate_up=("mean_rate_up_hz", "mean"),
            mean_rate_down=("mean_rate_down_hz", "mean"),
            mean_abs_rate_diff=("mean_abs_rate_diff_hz", "mean"),
            play_fraction=("play_fraction", "mean"),
            play_rate_diff=("play_mean_abs_rate_diff_hz", "mean"),
            play_tick_corr=("play_tick_rate_diff_corr", "mean"),
            norm_diff_corr=("norm_diff_bally_corr", "mean"),
            early_norm_corr=("early_norm_diff_corr", "mean"),
            late_norm_corr=("late_norm_diff_corr", "mean"),
            rest_rate=("rest_motor_rate_hz", "mean"),
            quiet_rest_rate=("quiet_rest_rate_hz", "mean"),
            play_motor_rate=("play_motor_rate_hz", "mean"),
            bg_weight=("bg_noise_weight_nS", "mean"),
            impact_corr_mean=("impact_rate_diff_corr", "mean"),
            impact_corr_sd=("impact_rate_diff_corr", "std"),
            impact_r2_mean=("impact_rate_diff_r2", "mean"),
            impact_up_corr_mean=("impact_rate_up_corr", "mean"),
            impact_down_corr_mean=("impact_rate_down_corr", "mean"),
            tick_corr_mean=("tick_rate_diff_corr", "mean"),
            vel_y_corr_mean=("tick_velocity_bally_corr", "mean"),
            rate_updown_corr=("tick_rate_updown_corr", "mean"),
            exclusive_fraction=("exclusive_fraction", "mean"),
            both_spike_fraction=("both_spike_fraction", "mean"),
            inh_play_rate=("inh_play_rate_hz", "mean"),
            inh_total_spikes=("inh_total_spikes", "mean"),
            inh_up_total=("inh_up_total_spikes", "mean"),
            inh_down_total=("inh_down_total_spikes", "mean"),
            inh_diff_corr=("inh_diff_bally_corr", "mean"),
            inh_up_down_corr=("inh_up_down_count_corr", "mean"),
            inh_motor_corr=("inh_motor_rate_corr", "mean"),
            motor_mean_rate=("motor_mean_rate_hz", "mean"),
            net_s_rate=("net_s_rate_hz", "mean"),
            net_e1_rate=("net_e1_rate_hz", "mean"),
            net_e2_rate=("net_e2_rate_hz", "mean"),
            net_i1_rate=("net_i1_rate_hz", "mean"),
            net_i2_rate=("net_i2_rate_hz", "mean"),
            rec_ee_nS=("rec_w_ee_nS", "mean"),
            rec_e_rate_mean=("rec_e_mean_rate_hz", "mean"),
            rec_e_rate_min=("rec_e_min_rate_hz", "mean"),
            rec_e_rate_max=("rec_e_max_rate_hz", "mean"),
            rec_i_rate_mean=("rec_i_mean_rate_hz", "mean"),
            rec_s_rate_mean=("rec_s_mean_rate_hz", "mean"),
            rec_max_cell_rate=("rec_max_cell_rate_hz", "mean"),
            rec_cv_isi=("rec_e_cv_isi_mean", "mean"),
            rec_pair_corr=("rec_e_pair_corr_mean", "mean"),
            rec_rate_drift=("rec_e_rate_drift", "mean"),
            lat_corr=("lat_delta_corr", "mean"),
            lat_p95=("lat_delta_p95_abs", "mean"),
            lat_zero=("lat_zero_frac", "mean"),
            w_up_init=("w_up_initial_mean", "mean"),
            w_up_final=("w_up_final_mean", "mean"),
            w_down_init=("w_down_initial_mean", "mean"),
            w_down_final=("w_down_final_mean", "mean"),
            dw_up=("w_up_delta_absmean", "mean"),
            dw_down=("w_down_delta_absmean", "mean"),
            w_diff_corr_init=("w_diff_channel_corr_initial", "mean"),
            w_diff_corr_final=("w_diff_channel_corr", "mean"),
            w_sum_corr_final=("w_sum_channel_corr", "mean"),
            w_diff_absmean=("w_diff_absmean_final", "mean"),
            at_max_up=("w_up_at_max_frac", "mean"),
            at_max_down=("w_down_at_max_frac", "mean"),
        )
        .reset_index()
    )
    agg.to_csv(outdir / "summary_by_condition.csv", index=False)

    # ------------------------------------------------------------------
    # 图
    # ------------------------------------------------------------------
    conds = list(agg["condition"])

    # 图 1：行为
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(agg))
    ax.bar(x, agg["avg_rally_mean"], yerr=agg["avg_rally_sd"].fillna(0), capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(conds, rotation=25, ha="right")
    ax.set_ylabel("Average rally length")
    ax.set_title("Phase 4: two-pool readout, behavior by condition")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_rally_by_condition.png", bbox_inches="tight")
    plt.close(fig)

    # 图 2：读出信息量
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x, agg["impact_corr_mean"], yerr=agg["impact_corr_sd"].fillna(0), capsize=3)
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(conds, rotation=25, ha="right")
    ax.set_ylabel("corr(pre-impact rate diff, ball y)")
    ax.set_title("Phase 4: does the differential readout encode ball y?")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "fig_readout_corr.png", bbox_inches="tight")
    plt.close(fig)

    # 图 3：冲击散点（static vs 3b，所有 seed 合并）
    panels = [
        ("phase4_pushpull_static", "push-pull static"),
        ("phase4_pushpull_3b", "push-pull 3-factor"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, (cond, title) in zip(axes, panels):
        frames = []
        for seed in seeds:
            fp = impact_dir / f"{cond}_seed{seed}.csv"
            if fp.exists():
                frames.append(pd.read_csv(fp))
        if frames:
            d = pd.concat(frames, ignore_index=True)
            ax.scatter(d["ball_y"], d["rate_diff_pre"], s=10, alpha=0.35)
            if len(d) > 2 and d["ball_y"].std() > 0:
                b, a = np.polyfit(d["ball_y"], d["rate_diff_pre"], 1)
                xx = np.linspace(d["ball_y"].min(), d["ball_y"].max(), 20)
                ax.plot(xx, a + b * xx, color="tab:red", lw=1.5)
                ax.set_title(f"{title}\nslope={b:+.3f} Hz/bin")
            else:
                ax.set_title(title)
        ax.set_xlabel("ball y at impact")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("mean rate diff, last 300 ms (Hz)")
    fig.suptitle("Phase 4: differential readout vs ball position")
    fig.tight_layout()
    fig.savefig(outdir / "fig_impact_scatter.png", bbox_inches="tight")
    plt.close(fig)

    # 图 4：pushpull_3b seed0 的每通道权重
    key_cond = "phase4_pushpull_3b"
    fp = weight_dir / f"{key_cond}_seed{seeds[0]}.csv"
    if fp.exists():
        d = pd.read_csv(fp)
        w_up_cols = [c for c in d.columns if c.startswith("w_up_")]
        w_down_cols = [c for c in d.columns if c.startswith("w_down_")]
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
        xx = np.arange(1, 9)
        for ax, cols, name in zip(
            axes, (w_up_cols, w_down_cols), ("up pool", "down pool")
        ):
            ax.plot(xx, d[cols].iloc[0], "o-", label="initial")
            ax.plot(xx, d[cols].iloc[-1], "s-", label="final")
            ax.set_xlabel("Sensory channel (ball y bin)")
            ax.set_title(f"{name}")
            ax.grid(alpha=0.3)
            ax.legend(frameon=False)
        axes[0].set_ylabel("Synaptic efficacy")
        fig.suptitle(f"{key_cond} seed {seeds[0]}: weight profile")
        fig.tight_layout()
        fig.savefig(outdir / "fig_weights_pushpull.png", bbox_inches="tight")
        plt.close(fig)

    # ------------------------------------------------------------------
    # 报告
    # ------------------------------------------------------------------
    lines = []
    lines.append("# Phase 4: Two-pool differential readout (2 cells)")
    lines.append("")
    lines.append(f"- Config: `{args.config}`")
    lines.append(f"- Duration: {pc.duration_s:.1f} s; seeds: {seeds}")
    lines.append(
        f"- ball_speed: {pong.ball_speed:.3f} bins/s (approach ≈ "
        f"{1.0 / pong.ball_speed:.1f} s)"
        + ("  ← task-timescale override (main = 0.5)" if args.ball_speed is not None else "  (main Phase 4 value)")
    )
    lines.append(
        f"- velocity_gain: {pc.velocity_gain:.3f} bins/s/Hz"
        + ("  ← Tier 1 sensitivity override (main Phase 4 = 0.15)" if args.velocity_gain is not None else "  (main Phase 4 value)")
    )
    lines.append(
        "- readout: "
        + (
            f"normalized, k_norm={pc.velocity_gain_norm:.2f} bins/s, eps={pc.norm_eps_hz:.1e} Hz"
            if pc.normalized_readout
            else "difference (v = k·(up−down))"
        )
    )
    lines.append(
        f"- background activity: {pc.bg_noise_hz:.2f} Hz, "
        f"weight={pc.bg_noise_weight_nS:.1f} nS/spike (independent per pool)"
    )
    local_conditions = [c for c in conditions if "local" in c]
    lines.append(
        "- credit assignment: "
        + (
            "pool-specific local for conditions tagged `local` ("
            + ", ".join(local_conditions)
            + "); global scalar D(t) otherwise"
            if local_conditions
            else "global scalar D(t)"
        )
    )
    dyn_conditions = [c for c in conditions if "dyn" in c]
    if dyn_conditions:
        hs_desc = (
            f"functional band [{pc.hs_target_low_hz:.0f}, {pc.hs_target_high_hz:.0f}] Hz, "
            f"play-only, α={pc.hs_alpha:.2f} for: " + ", ".join(dyn_conditions)
        )
    elif any("play_hs" in c for c in conditions):
        hs_desc = f"point target {pc.target_rate_hz:.0f} Hz, play-only"
    elif any("no_hs" in c for c in conditions):
        hs_desc = f"point target {pc.target_rate_hz:.0f} Hz, off for `no_hs` arms"
    else:
        hs_desc = f"point target {pc.target_rate_hz:.0f} Hz, all periods"
    lines.append(f"- homeostasis: {hs_desc}")
    stp_conditions = [c for c in conditions if "stp" in c]
    if stp_conditions:
        lines.append(
            "- short-term plasticity: Tsodyks–Markram on sensory afferents "
            f"(U={pc.stp_u:.2f}, τ_rec={pc.stp_tau_rec_ms:.0f} ms, "
            f"τ_fac={pc.stp_tau_fac_ms:.0f} ms, gain normalized by U) for: "
            + ", ".join(stp_conditions)
        )
    else:
        lines.append("- short-term plasticity: off")
    pd_conditions = [c for c in conditions if "pd" in c]
    if pd_conditions:
        lines.append(
            "- control: PD readout, v = Kp·Δr + Kp·τ_pred·dΔr/dt with "
            f"Kp={pc.velocity_gain:.3f} bins/s/Hz, τ_pred={pc.pd_tau_ms:.0f} ms "
            "for: " + ", ".join(pd_conditions)
        )
    else:
        lines.append("- control: proportional, v = Kp·Δr")
    lat_conditions = [c for c in conditions if "lat" in c]
    if lat_conditions:
        lines.append(
            "- encoding: frame latency code (frame=100 ms, delay 0–100 ms by ball_y, "
            f"10 Hz volley); readout = frame first-spike latency difference, "
            f"v = K_lat·Δt (K_lat={pc.lat_gain:.3f} bins/s per ms) for: "
            + ", ".join(lat_conditions)
        )
    lines.append(
        f"- sensory rate factor: {pc.rate_min_hz:.1f}–{pc.rate_max_hz:.1f} Hz"
        + ("  ← rate-range override" if (args.rate_min is not None or args.rate_max is not None) else "  (distance-gated, main Phase 4)")
    )
    if any("net" in c for c in conditions):
        inh_desc = (
            f"10-cell E/I feedforward network (4 sensory → 2 E + 2 I → 2 motor); "
            f"g_S→E={pc.net_se_weight_nS:.0f} nS, g_E→M={pc.net_em_weight_nS:.0f} nS, "
            f"g_I→M={pc.inh_weight_nS:.0f} nS, E_inh={pc.E_inh_mV:.0f} mV"
        )
    elif pc.tuned_inhibition_enabled:
        inh_desc = (
            f"tuned (4-cell: I_up/I_down receive 8-channel sensory with "
            f"push-pull weights ×{pc.tuned_inh_gain:.2f}; "
            f"g_inh={pc.inh_weight_nS:.1f} nS/spike, E_inh={pc.E_inh_mV:.1f} mV)"
        )
    elif pc.cross_inhibition_enabled:
        inh_desc = (
            f"cross (4-cell: g_inh={pc.inh_weight_nS:.1f} nS/spike, "
            f"g_rec={pc.cross_rec_weight_nS:.1f} nS/spike, 10 ms loop delay, "
            f"E_inh={pc.E_inh_mV:.1f} mV)"
        )
    elif pc.inhibitory_enabled:
        inh_desc = (
            f"shared (3-cell: g_inh={pc.inh_weight_nS:.1f} nS/spike, "
            f"tau={pc.inh_tau_ms:.1f} ms, E_inh={pc.E_inh_mV:.1f} mV)"
        )
    else:
        inh_desc = "off (2-cell network)"
    lines.append(f"- inhibitory network: {inh_desc}")
    lines.append(f"- Conditions: {conditions}")
    lines.append(f"- Parallel jobs: {args.jobs}; total wall: {time.time() - t_start:.0f} s")
    lines.append("")
    lines.append("## Structure")
    lines.append("")
    lines.append(
        "Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory "
        "event times and the same feedback stimulation, each with its own plastic "
        "weights. Paddle velocity = k * (rate_up - rate_down), so common drive "
        "from ball distance and feedback cancels."
    )
    lines.append("")
    lines.append(
        "`phase4_pushpull_static` already contains a hand-set anti-symmetric "
        "weight profile, so plasticity must be judged against it, not only "
        "against random paddle."
    )
    if any("net" in c for c in conditions):
        lines.append("")
        lines.append(
            "Network conditions use 10 cells: 4 sensory relays (S1–S4, 8-channel "
            "gaussian tuning) drive 2 excitatory and 2 inhibitory interneurons; "
            "E spikes reach the motor pools through the plastic 2×2 weights, "
            "while I_up/I_down inhibit the opposite pool. Motor pools no longer "
            "receive sensory events directly, but keep the same feedback protocol."
        )
    lines.append("")
    lines.append("## Behavior")
    lines.append("")
    lines.append(
        "| condition | avg rally | hits | misses | aces | long rallies | mean |v| |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.avg_rally_mean:.3f} ± "
            f"{0 if pd.isna(row.avg_rally_sd) else row.avg_rally_sd:.3f} | "
            f"{row.hits_mean:.1f} | {row.misses_mean:.1f} | {row.aces_mean:.2f} | "
            f"{row.long_rallies_mean:.2f} | {row.mean_abs_velocity:.2f} |"
        )
    lines.append("")
    lines.append("## Readout information")
    lines.append("")
    lines.append(
        "`impact corr` = Pearson correlation over rallies between the mean "
        "rate difference in the last 300 ms before impact and the ball y at "
        "impact (pooled per seed, then averaged). `play corr` is the tick-level "
        "correlation restricted to ticks where the game is running (rest "
        "timeouts excluded)."
    )
    lines.append("")
    lines.append(
        "| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | "
        "play fraction | play |diff| | play corr | norm corr | early norm | late norm | "
        "impact corr | impact R² | up corr | down corr |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        corr_sd = 0.0 if pd.isna(row.impact_corr_sd) else row.impact_corr_sd
        lines.append(
            f"| {row.condition} | {row.mean_rate_up:.1f} | {row.mean_rate_down:.1f} | "
            f"{row.mean_abs_rate_diff:.2f} | {row.play_fraction:.2f} | "
            f"{row.play_rate_diff:.2f} | {row.play_tick_corr:+.3f} | "
            f"{row.norm_diff_corr:+.3f} | {row.early_norm_corr:+.3f} | "
            f"{row.late_norm_corr:+.3f} | "
            f"{row.impact_corr_mean:+.3f} ± {corr_sd:.3f} | "
            f"{row.impact_r2_mean:.3f} | {row.impact_up_corr_mean:+.3f} | "
            f"{row.impact_down_corr_mean:+.3f} |"
        )
    lines.append("")
    lines.append("## Background activity")
    lines.append("")
    lines.append(
        "Mean motor rate during quiet rest (timeout after the unpredictable "
        "feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest "
        "rate is 0; with spontaneous activity it should be in the 1–5 Hz target range."
    )
    lines.append("")
    lines.append("| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.quiet_rest_rate:.2f} | {row.rest_rate:.2f} | "
            f"{row.play_motor_rate:.1f} | {row.bg_weight:.0f} |"
        )
    lines.append("")
    lines.append("## Motor differentiation")
    lines.append("")
    lines.append(
        "Fraction of ticks in which exactly one pool spikes, and the tick-level "
        "correlation between the two pools' rates. Shared input and shared "
        "feedback drive both pools together; true motor differentiation would "
        "show up as higher exclusivity and lower co-activity."
    )
    lines.append("")
    lines.append("| condition | exclusive spiking | rate up/down corr |")
    lines.append("|---|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.exclusive_fraction:.3f} | "
            f"{row.rate_updown_corr:+.3f} |"
        )
    lines.append("")
    lines.append("## Network activity (10-cell)")
    lines.append("")
    lines.append(
        "Mean firing rate over the whole session for the sensory relays (S1–S4), "
        "the two excitatory interneurons (E_up/E_down) and the two inhibitory "
        "interneurons (I_up/I_down). Zero for 2-cell conditions."
    )
    lines.append("")
    lines.append("| condition | S (mean of 4) | E_up | E_down | I_up | I_down |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.net_s_rate:.1f} | {row.net_e1_rate:.1f} | "
            f"{row.net_e2_rate:.1f} | {row.net_i1_rate:.1f} | {row.net_i2_rate:.1f} |"
        )
    lines.append("")
    lines.append("## Latency readout (v0.21.0)")
    lines.append("")
    lines.append(
        "`lat corr` is the tick-level correlation between the frame first-spike "
        "latency difference (down − up) and ball_y during play; `Δt P95` is the "
        "95th percentile of |Δt| in ms; `zero` is the fraction of playing ticks "
        "with no spike in either pool during the frame."
    )
    lines.append("")
    lines.append("| condition | lat corr | Δt P95 (ms) | zero frac |")
    lines.append("|---|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.lat_corr:+.3f} | {row.lat_p95:.1f} | {row.lat_zero:.2f} |"
        )
    lines.append("")
    lines.append("## Inhibition (3/4-cell version)")
    lines.append("")
    lines.append(
        "Only meaningful when inhibition is on. `I rate` is the 300 ms "
        "windowed total inhibitory rate during play; `corr(I, motor)` is the "
        "tick-level correlation between I rate and the mean motor rate."
    )
    lines.append("")
    lines.append(
        "| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.inh_play_rate:.1f} | "
            f"{row.inh_up_total:.0f} | {row.inh_down_total:.0f} | "
            f"{row.motor_mean_rate:.1f} | {row.exclusive_fraction:.3f} | "
            f"{row.both_spike_fraction:.3f} | {row.inh_diff_corr:+.3f} | "
            f"{row.inh_up_down_corr:+.3f} |"
        )
    lines.append("")
    lines.append("## Weights and plasticity")
    lines.append("")
    lines.append(
        "| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | "
        "corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | "
        "frac at w_max (up/down) | corr(w_up+w_down, channel) |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in agg.itertuples(index=False):
        lines.append(
            f"| {row.condition} | {row.w_up_init:.3f}→{row.w_up_final:.3f} | "
            f"{row.w_down_init:.3f}→{row.w_down_final:.3f} | {row.dw_up:.4f} | "
            f"{row.dw_down:.4f} | {row.w_diff_corr_init:+.3f}→{row.w_diff_corr_final:+.3f} | "
            f"{row.w_diff_absmean:.3f} | {row.at_max_up:.2f}/{row.at_max_down:.2f} | "
            f"{row.w_sum_corr_final:+.3f} |"
        )
    lines.append("")
    lines.append("## Two-sample permutation tests (rally length)")
    lines.append("")
    lines.append(
        "Conditions do **not** share RNG streams: different actions change the "
        "Poisson sensory event counts, so seed labels are not paired. Tests are "
        "two-sided label-shuffling permutations (20,000), descriptive only — no "
        "multiple-comparison correction."
    )
    lines.append("")
    lines.append("| contrast | mean diff | p | n_a / n_b |")
    lines.append("|---|---:|---:|---:|")
    contrasts = [
        ("phase4_pushpull_static", "phase4_random_paddle"),
        ("phase4_pushpull_static", "phase4_symmetric_static"),
        ("phase4_pushpull_3b_no_hs", "phase4_pushpull_static"),
        ("phase4_pushpull_3b_play_hs", "phase4_pushpull_static"),
        ("phase4_pushpull_3b", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_no_hs", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_play_hs", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_no_hs", "phase4_pushpull_3b"),
        ("phase4_pushpull_local_3b_play_hs", "phase4_pushpull_3b"),
        ("phase4_pushpull_local_3b_dyn", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_dyn", "phase4_pushpull_local_3b_no_hs"),
        ("phase4_pushpull_local_3b_dyn", "phase4_pushpull_local_3b"),
        ("phase4_pushpull_dyn_3b", "phase4_pushpull_static"),
        ("phase4_pushpull_dyn_3b", "phase4_pushpull_3b"),
        ("phase4_pushpull_local_3b_no_hs_stp", "phase4_pushpull_local_3b_no_hs"),
        ("phase4_pushpull_local_3b_no_hs_stp", "phase4_pushpull_static_stp"),
        ("phase4_pushpull_local_3b_no_hs_stp", "phase4_pushpull_static"),
        ("phase4_pushpull_3b_no_hs_stp", "phase4_pushpull_local_3b_no_hs_stp"),
        ("phase4_pushpull_static_stp", "phase4_pushpull_static"),
        ("phase5_net_local_no_hs_3b", "phase5_net_static"),
        ("phase5_net_global_no_hs_3b", "phase5_net_static"),
        ("phase5_net_static", "phase4_pushpull_static"),
        ("phase5_net_local_no_hs_3b", "phase4_pushpull_local_3b_no_hs"),
        ("phase4_pushpull_local_3b_no_hs_pd", "phase4_pushpull_local_3b_no_hs"),
        ("phase4_pushpull_static_pd", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_no_hs_pd", "phase4_pushpull_static"),
        ("phase4_pushpull_static_lat", "phase4_pushpull_static"),
        ("phase4_pushpull_local_3b_no_hs_lat", "phase4_pushpull_static_lat"),
        ("phase4_pushpull_local_3b_no_hs_lat", "phase4_pushpull_static"),
        ("phase4_random_3b", "phase4_random_paddle"),
    ]
    stats_rng = np.random.default_rng(12345)
    for a, b in contrasts:
        ga = summary.loc[summary["condition"] == a, "average_rally_length"].to_numpy()
        gb = summary.loc[summary["condition"] == b, "average_rally_length"].to_numpy()
        if len(ga) == 0 or len(gb) == 0:
            continue
        m, p, na, nb = _perm_test(ga, gb, stats_rng)
        lines.append(f"| {a} − {b} | {m:+.3f} | {p:.4f} | {na}/{nb} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- 见下方人工结论（基于本表，不调参）。")
    lines.append("")
    (outdir / "phase4_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\nSummary by condition:")
    print(agg.to_string(index=False))
    print(f"\nOutputs written to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
