# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 346 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.151 ± 0.063 | 8.8 | 58.6 | 51.13 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.178 ± 0.045 | 10.4 | 58.4 | 49.53 | 0.00 | 0.11 |
| phase4_pushpull_3b_play_hs | 0.165 ± 0.061 | 9.6 | 58.5 | 50.07 | 0.00 | 0.02 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |
| phase4_random_3b | 0.168 ± 0.048 | 9.8 | 58.6 | 50.07 | 0.00 | 0.00 |
| phase4_random_paddle | 0.125 ± 0.055 | 7.3 | 58.8 | 52.40 | 0.00 | 0.09 |
| phase4_symmetric_static | 0.162 ± 0.045 | 9.5 | 58.5 | 50.13 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.5 | 21.5 | 0.05 | 0.22 | 0.21 | +0.145 | +0.179 ± 0.046 | 0.034 | -0.012 | -0.039 |
| phase4_pushpull_3b_no_hs | 15.1 | 15.1 | 0.95 | 0.23 | 3.16 | +0.638 | +0.834 ± 0.043 | 0.697 | +0.289 | -0.184 |
| phase4_pushpull_3b_play_hs | 21.2 | 21.3 | 0.18 | 0.23 | 0.66 | +0.234 | +0.264 ± 0.074 | 0.075 | +0.018 | -0.051 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |
| phase4_random_3b | 21.6 | 21.6 | 0.03 | 0.23 | 0.08 | -0.006 | +0.003 ± 0.114 | 0.012 | +0.020 | +0.020 |
| phase4_random_paddle | 17.7 | 17.8 | 0.81 | 0.22 | 2.70 | -0.166 | -0.261 ± 0.390 | 0.210 | -0.039 | +0.110 |
| phase4_symmetric_static | 17.7 | 17.7 | 0.00 | 0.23 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.006 | -0.006 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.014 | +0.987 |
| phase4_pushpull_3b_play_hs | 0.002 | +0.998 |
| phase4_pushpull_static | 0.022 | +0.975 |
| phase4_random_3b | 0.001 | +1.000 |
| phase4_random_paddle | 0.015 | +0.992 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.370 | 1.000→1.370 | 0.3743 | 0.3718 | +1.000→+0.000 | 0.000 | 0.34/0.34 | -0.088 |
| phase4_pushpull_3b_no_hs | 1.000→0.356 | 1.000→0.355 | 0.6439 | 0.6446 | +1.000→+0.838 | 0.068 | 0.00/0.00 | +0.136 |
| phase4_pushpull_3b_play_hs | 1.000→1.440 | 1.000→1.440 | 0.4398 | 0.4398 | +1.000→+0.000 | 0.000 | 0.33/0.33 | +0.114 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.338 | 1.007→1.338 | 0.3360 | 0.3319 | -0.128→+0.000 | 0.000 | 0.07/0.07 | -0.249 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.079 | 0.0002 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.042 | 0.0158 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.026 | 0.1246 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.040 | 0.0517 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.053 | 0.0133 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.043 | 0.0346 | 15/15 |

## Interpretation

- 本目录是 600 s 主协议臂（距离门控 4–40 Hz）的自动表格。
- 完整分析、H1–H4 判定与跨臂比较见 `results/phase4_long_session.md`。
- 关键结果：static 0.204 vs symmetric 0.162（+0.042，p=0.016）、vs random 0.125（+0.079，p=0.0002）；
  3b −0.053（p=0.012）；no_hs T1→T2 hit 0.190→0.109（p=0.0001）。
