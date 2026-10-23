# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 120.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.300 bins/s/Hz  ← Tier 1 sensitivity override (main Phase 4 = 0.15)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 76 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.154 ± 0.160 | 1.8 | 11.9 | 10.47 | 0.00 | 0.06 |
| phase4_pushpull_3b_no_hs | 0.204 ± 0.157 | 2.4 | 11.9 | 9.67 | 0.00 | 0.33 |
| phase4_pushpull_3b_play_hs | 0.194 ± 0.121 | 2.3 | 11.9 | 10.07 | 0.00 | 0.21 |
| phase4_pushpull_static | 0.201 ± 0.190 | 2.3 | 11.9 | 9.87 | 0.00 | 0.35 |
| phase4_random_3b | 0.139 ± 0.098 | 1.7 | 12.0 | 10.47 | 0.00 | 0.02 |
| phase4_random_paddle | 0.106 ± 0.092 | 1.3 | 12.0 | 10.87 | 0.00 | 0.16 |
| phase4_symmetric_static | 0.106 ± 0.097 | 1.3 | 12.0 | 11.07 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.3 | 21.3 | 0.24 | 0.23 | 0.85 | +0.291 | +0.361 ± 0.154 | 0.152 | +0.049 | -0.031 |
| phase4_pushpull_3b_no_hs | 17.3 | 17.3 | 1.42 | 0.24 | 4.72 | +0.719 | +0.928 ± 0.040 | 0.862 | +0.452 | -0.455 |
| phase4_pushpull_3b_play_hs | 20.8 | 20.8 | 0.88 | 0.24 | 3.02 | +0.542 | +0.643 ± 0.081 | 0.420 | +0.061 | -0.239 |
| phase4_pushpull_static | 18.0 | 17.9 | 1.51 | 0.24 | 5.09 | +0.747 | +0.916 ± 0.056 | 0.842 | +0.400 | -0.486 |
| phase4_random_3b | 21.5 | 21.5 | 0.13 | 0.23 | 0.37 | -0.028 | -0.012 ± 0.269 | 0.068 | +0.063 | +0.069 |
| phase4_random_paddle | 18.0 | 18.0 | 0.74 | 0.22 | 2.41 | -0.120 | -0.135 ± 0.432 | 0.192 | +0.014 | +0.073 |
| phase4_symmetric_static | 17.8 | 17.8 | 0.00 | 0.22 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.056 | -0.056 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.004 | +0.997 |
| phase4_pushpull_3b_no_hs | 0.021 | +0.976 |
| phase4_pushpull_3b_play_hs | 0.012 | +0.989 |
| phase4_pushpull_static | 0.021 | +0.976 |
| phase4_random_3b | 0.002 | +0.999 |
| phase4_random_paddle | 0.015 | +0.993 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.409 | 1.000→1.409 | 0.4089 | 0.4087 | +1.000→+0.000 | 0.000 | 0.28/0.28 | +0.130 |
| phase4_pushpull_3b_no_hs | 1.000→0.774 | 1.000→0.774 | 0.2379 | 0.2387 | +1.000→+0.981 | 0.188 | 0.00/0.00 | -0.022 |
| phase4_pushpull_3b_play_hs | 1.000→1.428 | 1.000→1.428 | 0.4277 | 0.4277 | +1.000→-0.056 | 0.000 | 0.10/0.10 | +0.002 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.377 | 1.007→1.377 | 0.3751 | 0.3704 | -0.128→+0.000 | 0.000 | 0.21/0.21 | -0.017 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.095 | 0.0857 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.095 | 0.0953 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | +0.003 | 0.9742 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.007 | 0.9215 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.047 | 0.4753 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.033 | 0.4067 | 15/15 |

## Interpretation

- 本目录只提供 gain=0.30 的自动表格；机制结论与假设判定见 `results/phase4_gain_sensitivity.md`。
- 主结果（gain=0.15）见 `results/phase4/phase4_report.md`。
