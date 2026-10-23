# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.250 bins/s (approach ≈ 4.0 s)  ← task-timescale override (main = 0.5)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 350 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.132 ± 0.073 | 6.3 | 48.0 | 42.53 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.181 ± 0.055 | 8.5 | 47.1 | 39.73 | 0.00 | 0.19 |
| phase4_pushpull_3b_play_hs | 0.204 ± 0.068 | 9.5 | 46.8 | 38.87 | 0.00 | 0.15 |
| phase4_pushpull_static | 0.178 ± 0.057 | 8.3 | 47.1 | 40.07 | 0.07 | 0.31 |
| phase4_random_3b | 0.143 ± 0.081 | 6.7 | 47.7 | 41.80 | 0.00 | 0.01 |
| phase4_random_paddle | 0.118 ± 0.068 | 5.6 | 48.2 | 43.20 | 0.07 | 0.15 |
| phase4_symmetric_static | 0.148 ± 0.062 | 7.0 | 47.7 | 41.87 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 23.9 | 23.9 | 0.09 | 0.36 | 0.22 | +0.176 | +0.180 ± 0.089 | 0.040 | -0.017 | -0.048 |
| phase4_pushpull_3b_no_hs | 13.6 | 13.6 | 1.43 | 0.37 | 3.30 | +0.672 | +0.852 ± 0.041 | 0.728 | +0.247 | -0.255 |
| phase4_pushpull_3b_play_hs | 22.2 | 22.1 | 1.12 | 0.38 | 2.57 | +0.413 | +0.458 ± 0.097 | 0.218 | +0.110 | -0.077 |
| phase4_pushpull_static | 18.4 | 18.4 | 2.30 | 0.37 | 5.50 | +0.774 | +0.929 ± 0.014 | 0.864 | +0.530 | -0.454 |
| phase4_random_3b | 23.9 | 23.9 | 0.05 | 0.37 | 0.12 | -0.016 | -0.028 ± 0.121 | 0.014 | -0.063 | -0.059 |
| phase4_random_paddle | 18.4 | 18.5 | 1.18 | 0.36 | 2.78 | -0.150 | -0.209 ± 0.447 | 0.230 | -0.014 | +0.078 |
| phase4_symmetric_static | 18.3 | 18.3 | 0.00 | 0.37 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | +0.036 | +0.036 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.021 | +0.977 |
| phase4_pushpull_3b_play_hs | 0.018 | +0.989 |
| phase4_pushpull_static | 0.032 | +0.959 |
| phase4_random_3b | 0.001 | +1.000 |
| phase4_random_paddle | 0.022 | +0.988 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.0 | 0 | 0 | 23.9 | 0.001 | 0.212 | +0.000 | +0.000 |
| phase4_pushpull_3b_no_hs | 0.0 | 0 | 0 | 13.6 | 0.021 | 0.115 | +0.000 | +0.000 |
| phase4_pushpull_3b_play_hs | 0.0 | 0 | 0 | 22.2 | 0.018 | 0.189 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 18.4 | 0.032 | 0.152 | +0.000 | +0.000 |
| phase4_random_3b | 0.0 | 0 | 0 | 23.9 | 0.001 | 0.211 | +0.000 | +0.000 |
| phase4_random_paddle | 0.0 | 0 | 0 | 18.4 | 0.022 | 0.157 | +0.000 | +0.000 |
| phase4_symmetric_static | 0.0 | 0 | 0 | 18.3 | 0.000 | 0.168 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.313 | 1.000→1.313 | 0.3183 | 0.3158 | +1.000→+0.000 | 0.000 | 0.20/0.20 | -0.126 |
| phase4_pushpull_3b_no_hs | 1.000→0.345 | 1.000→0.346 | 0.6550 | 0.6539 | +1.000→+0.874 | 0.080 | 0.00/0.00 | -0.055 |
| phase4_pushpull_3b_play_hs | 1.000→1.227 | 1.000→1.226 | 0.2467 | 0.2500 | +1.000→-0.013 | 0.026 | 0.00/0.00 | -0.084 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.374 | 1.007→1.374 | 0.3730 | 0.3694 | -0.128→+0.000 | 0.000 | 0.40/0.40 | -0.039 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.060 | 0.0154 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.030 | 0.1705 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | +0.003 | 0.8813 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | +0.026 | 0.2516 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.046 | 0.0676 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.025 | 0.3616 | 15/15 |

## Interpretation

- 本目录是 4 s 回合（ball_speed=0.25）的自动表格；完整分析见 `results/phase4_slow_ball_report.md`。
- 关键结果：static 0.178 / hit 0.150（2 s 版本为 0.204 / 0.169）；K_eff 0.141→0.094；
  static−symmetric 不显著（+0.030，p=0.171）；no_hs 持平，3b 更差（p=0.068）。
