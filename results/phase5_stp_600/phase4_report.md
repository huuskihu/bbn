# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: pool-specific local for conditions tagged `local` (phase4_pushpull_local_3b_no_hs_stp, phase4_pushpull_local_3b_no_hs); global scalar D(t) otherwise
- homeostasis: point target 20 Hz, off for `no_hs` arms
- short-term plasticity: Tsodyks–Markram on sensory afferents (U=0.40, τ_rec=200 ms, τ_fac=1000 ms, gain normalized by U) for: phase4_pushpull_local_3b_no_hs_stp, phase4_pushpull_3b_no_hs_stp, phase4_pushpull_static_stp
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_local_3b_no_hs_stp', 'phase4_pushpull_3b_no_hs_stp', 'phase4_pushpull_static_stp', 'phase4_pushpull_static', 'phase4_pushpull_local_3b_no_hs']
- Parallel jobs: 10; total wall: 301 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 0.200 ± 0.065 | 11.6 | 58.1 | 47.93 | 0.00 | 0.09 |
| phase4_pushpull_local_3b_no_hs | 0.220 ± 0.079 | 12.7 | 57.9 | 47.27 | 0.07 | 0.28 |
| phase4_pushpull_local_3b_no_hs_stp | 0.187 ± 0.066 | 10.9 | 58.2 | 48.73 | 0.07 | 0.17 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |
| phase4_pushpull_static_stp | 0.177 ± 0.060 | 10.3 | 58.3 | 49.53 | 0.00 | 0.12 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 14.6 | 14.6 | 0.81 | 0.23 | 2.68 | +0.682 | +0.675 | +0.645 | +0.728 | +0.759 ± 0.040 | 0.578 | +0.363 | -0.317 |
| phase4_pushpull_local_3b_no_hs | 18.7 | 18.9 | 2.25 | 0.24 | 8.09 | +0.636 | +0.592 | +0.569 | +0.740 | +0.735 ± 0.107 | 0.551 | +0.429 | -0.446 |
| phase4_pushpull_local_3b_no_hs_stp | 15.5 | 15.6 | 1.36 | 0.23 | 4.90 | +0.744 | +0.728 | +0.699 | +0.817 | +0.809 ± 0.035 | 0.656 | +0.463 | -0.534 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.681 | +0.656 | +0.886 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |
| phase4_pushpull_static_stp | 15.3 | 15.3 | 1.03 | 0.23 | 3.62 | +0.749 | +0.714 | +0.704 | +0.784 | +0.802 ± 0.032 | 0.645 | +0.399 | -0.438 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 1.59 | 16.84 | 7.3 | 40 |
| phase4_pushpull_local_3b_no_hs | 1.57 | 17.53 | 22.8 | 40 |
| phase4_pushpull_local_3b_no_hs_stp | 1.57 | 16.94 | 10.9 | 40 |
| phase4_pushpull_static | 1.58 | 17.45 | 19.0 | 40 |
| phase4_pushpull_static_stp | 1.59 | 16.91 | 9.7 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 0.013 | +0.992 |
| phase4_pushpull_local_3b_no_hs | 0.031 | +0.950 |
| phase4_pushpull_local_3b_no_hs_stp | 0.022 | +0.979 |
| phase4_pushpull_static | 0.022 | +0.975 |
| phase4_pushpull_static_stp | 0.016 | +0.988 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 0.0 | 0 | 0 | 14.6 | 0.013 | 0.129 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_no_hs | 0.0 | 0 | 0 | 18.8 | 0.031 | 0.155 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_no_hs_stp | 0.0 | 0 | 0 | 15.5 | 0.022 | 0.133 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |
| phase4_pushpull_static_stp | 0.0 | 0 | 0 | 15.3 | 0.016 | 0.133 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b_no_hs_stp | 1.000→0.740 | 1.000→0.749 | 0.2613 | 0.2519 | +1.000→+0.946 | 0.147 | 0.00/0.00 | -0.103 |
| phase4_pushpull_local_3b_no_hs | 1.000→1.204 | 1.000→1.141 | 0.2336 | 0.1915 | +1.000→+0.780 | 0.327 | 0.07/0.04 | -0.201 |
| phase4_pushpull_local_3b_no_hs_stp | 1.000→1.087 | 1.000→1.092 | 0.1369 | 0.1372 | +1.000→+0.880 | 0.391 | 0.03/0.01 | +0.030 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_pushpull_static_stp | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_static | +0.015 | 0.5127 | 15/15 |
| phase4_pushpull_local_3b_no_hs_stp − phase4_pushpull_local_3b_no_hs | -0.032 | 0.2431 | 15/15 |
| phase4_pushpull_local_3b_no_hs_stp − phase4_pushpull_static_stp | +0.011 | 0.6381 | 15/15 |
| phase4_pushpull_local_3b_no_hs_stp − phase4_pushpull_static | -0.017 | 0.4285 | 15/15 |
| phase4_pushpull_3b_no_hs_stp − phase4_pushpull_local_3b_no_hs_stp | +0.013 | 0.6002 | 15/15 |
| phase4_pushpull_static_stp − phase4_pushpull_static | -0.028 | 0.1576 | 15/15 |

## Interpretation

- 本目录是 P3 STP 的自动表格；完整分析见 `results/phase5_stp_report.md`。
- 时间形状：`static_stp` early 0.656→0.704、gap 0.230→0.080；`local_stp` early 0.569→0.699、gap 0.171→0.118（H1 early 路径成立）。
- 信息：`local_stp` impact corr 0.735→0.809、`w_diff corr` 0.780→0.880；但 mean |diff| 2.25→1.36 Hz，命令减弱（mean |v| 0.28→0.17）。
- 行为：`local_stp` 0.187 < `local_no_hs` 0.220（p=0.243），与 `static_stp` 0.177 无差异（p=0.638）；H2 不支持。
- H4 触发：时间形状不是行为瓶颈，STP 线停止；不调 U/τ、不叠加 PD。
