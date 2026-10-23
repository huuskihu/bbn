# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 20.0–20.0 Hz  ← rate-range override
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 350 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.153 ± 0.054 | 8.9 | 58.7 | 50.47 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.179 ± 0.049 | 10.4 | 58.3 | 49.53 | 0.00 | 0.12 |
| phase4_pushpull_3b_play_hs | 0.176 ± 0.068 | 10.3 | 58.5 | 49.67 | 0.00 | 0.02 |
| phase4_pushpull_static | 0.236 ± 0.079 | 13.5 | 57.7 | 46.80 | 0.00 | 0.18 |
| phase4_random_3b | 0.150 ± 0.061 | 8.8 | 58.7 | 51.13 | 0.00 | 0.00 |
| phase4_random_paddle | 0.125 ± 0.050 | 7.3 | 59.0 | 52.47 | 0.07 | 0.09 |
| phase4_symmetric_static | 0.180 ± 0.035 | 10.5 | 58.3 | 49.73 | 0.07 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 20.7 | 20.7 | 0.06 | 0.23 | 0.23 | +0.167 | +0.185 ± 0.098 | 0.043 | -0.064 | -0.103 |
| phase4_pushpull_3b_no_hs | 15.2 | 15.2 | 1.01 | 0.23 | 3.53 | +0.732 | +0.802 ± 0.036 | 0.645 | +0.295 | -0.269 |
| phase4_pushpull_3b_play_hs | 20.8 | 20.8 | 0.19 | 0.23 | 0.67 | +0.260 | +0.270 ± 0.085 | 0.080 | +0.037 | -0.042 |
| phase4_pushpull_static | 17.2 | 17.3 | 1.42 | 0.24 | 5.07 | +0.802 | +0.872 ± 0.024 | 0.760 | +0.419 | -0.389 |
| phase4_random_3b | 20.7 | 20.7 | 0.03 | 0.23 | 0.09 | -0.030 | -0.044 ± 0.146 | 0.022 | -0.021 | -0.018 |
| phase4_random_paddle | 17.2 | 17.2 | 0.76 | 0.22 | 2.60 | -0.125 | -0.140 ± 0.391 | 0.162 | +0.001 | +0.068 |
| phase4_symmetric_static | 17.2 | 17.2 | 0.00 | 0.23 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | +0.006 | +0.006 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.015 | +0.987 |
| phase4_pushpull_3b_play_hs | 0.003 | +0.997 |
| phase4_pushpull_static | 0.021 | +0.977 |
| phase4_random_3b | 0.001 | +1.000 |
| phase4_random_paddle | 0.014 | +0.993 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.380 | 1.000→1.380 | 0.3806 | 0.3808 | +1.000→+0.000 | 0.000 | 0.33/0.33 | -0.016 |
| phase4_pushpull_3b_no_hs | 1.000→0.465 | 1.000→0.468 | 0.5348 | 0.5324 | +1.000→+0.906 | 0.085 | 0.00/0.00 | +0.075 |
| phase4_pushpull_3b_play_hs | 1.000→1.442 | 1.000→1.442 | 0.4415 | 0.4415 | +1.000→+0.000 | 0.000 | 0.20/0.20 | -0.005 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.396 | 1.007→1.396 | 0.3938 | 0.3892 | -0.128→+0.000 | 0.000 | 0.28/0.28 | +0.065 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.111 | 0.0001 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.056 | 0.0179 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.057 | 0.0269 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.059 | 0.0373 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.083 | 0.0023 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.026 | 0.2141 | 15/15 |

## Interpretation

- 本目录是 600 s 恒常率臂（20/20 Hz）的自动表格。
- 完整分析、H1–H4 判定与跨臂比较见 `results/phase4_long_session.md`。
- 关键结果：static 0.236 vs symmetric 0.180（+0.056，p=0.019）、vs random 0.125（+0.111，p=0.0002）；
  3b −0.083（p=0.002）；no_hs T1→T2 hit 0.186→0.114（p=0.0009）；
  const static 比 dist static 仅 +0.031（p=0.183）。
