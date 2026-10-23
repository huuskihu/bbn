# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: pool-specific local for conditions tagged `local` (phase5_net_local_no_hs_3b, phase4_pushpull_local_3b_no_hs); global scalar D(t) otherwise
- homeostasis: point target 20 Hz, off for `no_hs` arms
- short-term plasticity: off
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: 10-cell E/I feedforward network (4 sensory → 2 E + 2 I → 2 motor); g_S→E=40 nS, g_E→M=40 nS, g_I→M=10 nS, E_inh=-80 mV
- Conditions: ['phase5_net_static', 'phase5_net_local_no_hs_3b', 'phase5_net_global_no_hs_3b', 'phase4_pushpull_static', 'phase4_pushpull_local_3b_no_hs']
- Parallel jobs: 10; total wall: 977 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.220 ± 0.079 | 12.7 | 57.9 | 47.27 | 0.07 | 0.28 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |
| phase5_net_global_no_hs_3b | 0.148 ± 0.047 | 8.7 | 58.6 | 51.07 | 0.00 | 0.01 |
| phase5_net_local_no_hs_3b | 0.127 ± 0.053 | 7.5 | 58.9 | 52.67 | 0.00 | 0.10 |
| phase5_net_static | 0.203 ± 0.098 | 11.7 | 58.1 | 49.07 | 0.20 | 0.03 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 18.7 | 18.9 | 2.25 | 0.24 | 8.09 | +0.636 | +0.592 | +0.569 | +0.740 | +0.735 ± 0.107 | 0.551 | +0.429 | -0.446 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.681 | +0.656 | +0.886 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |
| phase5_net_global_no_hs_3b | 13.4 | 13.4 | 0.18 | 0.22 | 0.24 | +0.072 | +0.054 | +0.028 | +0.075 | +0.116 ± 0.109 | 0.025 | -0.029 | -0.051 |
| phase5_net_local_no_hs_3b | 16.4 | 16.4 | 0.94 | 0.22 | 3.07 | -0.025 | -0.027 | -0.018 | -0.044 | -0.017 ± 0.129 | 0.016 | +0.045 | +0.046 |
| phase5_net_static | 16.2 | 16.2 | 0.34 | 0.23 | 0.80 | +0.266 | +0.252 | +0.158 | +0.356 | +0.479 ± 0.068 | 0.234 | +0.086 | -0.046 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 1.57 | 17.53 | 22.8 | 40 |
| phase4_pushpull_static | 1.58 | 17.45 | 19.0 | 40 |
| phase5_net_global_no_hs_3b | 1.59 | 16.78 | 1.9 | 40 |
| phase5_net_local_no_hs_3b | 1.58 | 17.31 | 13.4 | 40 |
| phase5_net_static | 1.58 | 17.27 | 12.5 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.031 | +0.950 |
| phase4_pushpull_static | 0.022 | +0.975 |
| phase5_net_global_no_hs_3b | 0.002 | +0.999 |
| phase5_net_local_no_hs_3b | 0.010 | +0.985 |
| phase5_net_static | 0.004 | +0.998 |

## Network activity (10-cell)

Mean firing rate over the whole session for the sensory relays (S1–S4), the two excitatory interneurons (E_up/E_down) and the two inhibitory interneurons (I_up/I_down). Zero for 2-cell conditions.

| condition | S (mean of 4) | E_up | E_down | I_up | I_down |
|---|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase4_pushpull_static | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase5_net_global_no_hs_3b | 7.6 | 14.6 | 14.4 | 14.4 | 14.6 |
| phase5_net_local_no_hs_3b | 7.7 | 14.5 | 14.6 | 14.6 | 14.5 |
| phase5_net_static | 7.6 | 14.4 | 14.4 | 14.4 | 14.4 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.0 | 0 | 0 | 18.8 | 0.031 | 0.155 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |
| phase5_net_global_no_hs_3b | 12.1 | 1945 | 1965 | 13.4 | 0.002 | 0.122 | -0.142 | +0.817 |
| phase5_net_local_no_hs_3b | 12.1 | 1934 | 1928 | 16.4 | 0.010 | 0.142 | -0.142 | +0.824 |
| phase5_net_static | 12.2 | 2021 | 2016 | 16.2 | 0.004 | 0.144 | -0.145 | +0.821 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 1.000→1.204 | 1.000→1.141 | 0.2336 | 0.1915 | +1.000→+0.780 | 0.327 | 0.07/0.04 | -0.201 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase5_net_global_no_hs_3b | 1.000→0.274 | 1.000→0.271 | 0.7259 | 0.7290 | +0.000→+0.000 | 0.337 | 0.00/0.00 | +0.000 |
| phase5_net_local_no_hs_3b | 1.000→1.105 | 1.000→1.091 | 0.2460 | 0.2398 | +0.000→+0.000 | 0.266 | 0.07/0.03 | +0.000 |
| phase5_net_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.400 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_static | +0.015 | 0.5127 | 15/15 |
| phase5_net_local_no_hs_3b − phase5_net_static | -0.076 | 0.0048 | 15/15 |
| phase5_net_global_no_hs_3b − phase5_net_static | -0.055 | 0.0389 | 15/15 |
| phase5_net_static − phase4_pushpull_static | -0.001 | 0.9899 | 15/15 |
| phase5_net_local_no_hs_3b − phase4_pushpull_local_3b_no_hs | -0.092 | 0.0009 | 15/15 |

## Interpretation

- 本目录是 P4 10 细胞 E/I 网络；完整分析见 `results/phase5_ten_cell_report.md`。
- 存活：S 7.6 Hz、E 14.4/14.4 Hz、I 14.4/14.4 Hz、play motor 12.5 Hz；H1 支持。
- 结构：`net_static` 0.203 ≈ 2 细胞 static 0.204（p=0.990）；但 impact corr 0.920→0.479（信息瓶颈）。
- 学习：`net_local` 0.127 < `net_static` 0.203（−0.076，p=0.005）；`net_global` 0.148（权重崩到 0.27）。
- H3 不支持、H4 触发：扩网络线停止；`w_diff corr` 在 2 通道下不适用（报告已说明）。
