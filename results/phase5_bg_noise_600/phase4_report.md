# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 3.00 Hz, weight=80.0 nS/spike (independent per pool)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_static', 'phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_symmetric_static']
- Parallel jobs: 10; total wall: 237 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.155 ± 0.066 | 9.1 | 58.6 | 51.07 | 0.00 | 0.13 |
| phase4_pushpull_3b_no_hs | 0.162 ± 0.047 | 9.5 | 58.4 | 50.20 | 0.00 | 0.18 |
| phase4_pushpull_static | 0.189 ± 0.050 | 10.9 | 58.1 | 49.13 | 0.00 | 0.23 |
| phase4_symmetric_static | 0.146 ± 0.057 | 8.5 | 58.7 | 50.93 | 0.00 | 0.14 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 24.2 | 24.1 | 3.55 | 0.23 | 3.96 | +0.058 | +0.025 | +0.006 | +0.106 | +0.083 ± 0.133 | 0.023 | +0.005 | -0.035 |
| phase4_pushpull_3b_no_hs | 17.9 | 17.9 | 3.90 | 0.23 | 5.37 | +0.447 | +0.271 | +0.168 | +0.455 | +0.724 ± 0.051 | 0.526 | +0.216 | -0.293 |
| phase4_pushpull_static | 20.6 | 20.6 | 4.24 | 0.23 | 6.60 | +0.604 | +0.418 | +0.330 | +0.757 | +0.853 ± 0.028 | 0.729 | +0.438 | -0.473 |
| phase4_symmetric_static | 20.6 | 20.5 | 3.56 | 0.22 | 4.03 | -0.001 | -0.009 | -0.015 | +0.007 | +0.051 ± 0.098 | 0.011 | +0.021 | -0.006 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_3b | 4.63 | 20.59 | 36.3 | 80 |
| phase4_pushpull_3b_no_hs | 4.60 | 19.74 | 11.6 | 80 |
| phase4_pushpull_static | 4.61 | 20.18 | 22.1 | 80 |
| phase4_symmetric_static | 4.60 | 20.19 | 21.8 | 80 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.074 | +0.970 |
| phase4_pushpull_3b_no_hs | 0.082 | +0.946 |
| phase4_pushpull_static | 0.087 | +0.940 |
| phase4_symmetric_static | 0.075 | +0.960 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.0 | 0 | 0 | 24.2 | 0.074 | 0.176 | +0.000 | +0.000 |
| phase4_pushpull_3b_no_hs | 0.0 | 0 | 0 | 17.9 | 0.082 | 0.122 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 20.6 | 0.087 | 0.143 | +0.000 | +0.000 |
| phase4_symmetric_static | 0.0 | 0 | 0 | 20.5 | 0.075 | 0.148 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.394 | 1.000→1.398 | 0.3940 | 0.3982 | +1.000→-0.027 | 0.009 | 0.40/0.40 | -0.111 |
| phase4_pushpull_3b_no_hs | 1.000→0.392 | 1.000→0.389 | 0.6118 | 0.6137 | +1.000→+0.809 | 0.090 | 0.00/0.00 | -0.120 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_symmetric_static | +0.043 | 0.0387 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.026 | 0.1559 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.033 | 0.1370 | 15/15 |

## Interpretation

- 本目录是 P0 背景自发活动（3 Hz, 80 nS）的自动表格；完整分析见 `results/phase5_bg_noise_report.md`。
- 关键结果：quiet-rest 4.6 Hz（目标 1–5）；3b 仍饱和（at w_max 0.40，w_diff corr −0.027）；
  static 0.189 / hit 0.158（无噪声 0.204 / 0.169）；no_hs 梯度 0.809 但行为 0.162。
- 按预注册 H4，背景噪声线停止。
