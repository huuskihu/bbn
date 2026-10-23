# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 120.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.600 bins/s/Hz  ← Tier 1 sensitivity override (main Phase 4 = 0.15)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 73 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.094 ± 0.076 | 1.1 | 12.0 | 10.93 | 0.00 | 0.08 |
| phase4_pushpull_3b_no_hs | 0.237 ± 0.187 | 2.7 | 11.8 | 9.73 | 0.00 | 0.52 |
| phase4_pushpull_3b_play_hs | 0.175 ± 0.136 | 2.1 | 11.9 | 10.27 | 0.07 | 0.29 |
| phase4_pushpull_static | 0.246 ± 0.203 | 2.9 | 11.9 | 9.47 | 0.00 | 0.60 |
| phase4_random_3b | 0.144 ± 0.120 | 1.7 | 11.9 | 10.47 | 0.00 | 0.05 |
| phase4_random_paddle | 0.094 ± 0.094 | 1.1 | 12.0 | 10.93 | 0.00 | 0.28 |
| phase4_symmetric_static | 0.106 ± 0.097 | 1.3 | 12.0 | 11.07 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.2 | 21.2 | 0.21 | 0.22 | 0.76 | +0.279 | +0.336 ± 0.166 | 0.139 | -0.079 | -0.163 |
| phase4_pushpull_3b_no_hs | 17.2 | 17.3 | 1.42 | 0.24 | 4.70 | +0.710 | +0.920 ± 0.036 | 0.848 | +0.543 | -0.409 |
| phase4_pushpull_3b_play_hs | 20.9 | 21.0 | 0.85 | 0.23 | 2.95 | +0.545 | +0.634 ± 0.139 | 0.420 | +0.037 | -0.242 |
| phase4_pushpull_static | 18.1 | 18.2 | 1.66 | 0.25 | 5.51 | +0.754 | +0.936 ± 0.018 | 0.876 | +0.479 | -0.491 |
| phase4_random_3b | 21.3 | 21.3 | 0.13 | 0.23 | 0.37 | -0.024 | -0.030 ± 0.298 | 0.084 | -0.040 | -0.034 |
| phase4_random_paddle | 17.9 | 18.0 | 0.73 | 0.22 | 2.36 | -0.135 | -0.147 ± 0.456 | 0.216 | -0.130 | -0.052 |
| phase4_symmetric_static | 17.8 | 17.8 | 0.00 | 0.22 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.056 | -0.056 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.003 | +0.998 |
| phase4_pushpull_3b_no_hs | 0.022 | +0.977 |
| phase4_pushpull_3b_play_hs | 0.012 | +0.989 |
| phase4_pushpull_static | 0.023 | +0.973 |
| phase4_random_3b | 0.002 | +0.999 |
| phase4_random_paddle | 0.014 | +0.993 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.432 | 1.000→1.432 | 0.4324 | 0.4323 | +1.000→+0.000 | 0.000 | 0.33/0.33 | -0.033 |
| phase4_pushpull_3b_no_hs | 1.000→0.782 | 1.000→0.772 | 0.2300 | 0.2396 | +1.000→+0.978 | 0.189 | 0.00/0.00 | +0.342 |
| phase4_pushpull_3b_play_hs | 1.000→1.402 | 1.000→1.402 | 0.4020 | 0.4020 | +1.000→-0.077 | 0.001 | 0.07/0.07 | +0.036 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.412 | 1.007→1.412 | 0.4093 | 0.4073 | -0.128→+0.000 | 0.000 | 0.27/0.27 | +0.340 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.152 | 0.0090 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.141 | 0.0154 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.010 | 0.8969 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.071 | 0.2672 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.152 | 0.0096 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.050 | 0.2463 | 15/15 |

## Interpretation

- 本目录只提供 gain=0.60 的自动表格；机制结论与假设判定见 `results/phase4_gain_sensitivity.md`。
- 主结果（gain=0.15）见 `results/phase4/phase4_report.md`。
