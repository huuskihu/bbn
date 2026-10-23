# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: cross (4-cell: g_inh=10.0 nS/spike, g_rec=40.0 nS/spike, 10 ms loop delay, E_inh=-80.0 mV)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 689 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.170 ± 0.074 | 9.9 | 58.3 | 49.60 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.146 ± 0.037 | 8.5 | 58.7 | 50.67 | 0.00 | 0.10 |
| phase4_pushpull_3b_play_hs | 0.163 ± 0.077 | 9.5 | 58.5 | 50.33 | 0.00 | 0.02 |
| phase4_pushpull_static | 0.194 ± 0.070 | 11.2 | 58.1 | 48.27 | 0.00 | 0.19 |
| phase4_random_3b | 0.188 ± 0.063 | 10.9 | 58.2 | 49.00 | 0.07 | 0.00 |
| phase4_random_paddle | 0.123 ± 0.077 | 7.2 | 58.9 | 53.27 | 0.13 | 0.09 |
| phase4_symmetric_static | 0.162 ± 0.045 | 9.5 | 58.5 | 50.13 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 20.6 | 20.6 | 0.06 | 0.23 | 0.21 | +0.132 | +0.170 ± 0.056 | 0.032 | -0.016 | -0.042 |
| phase4_pushpull_3b_no_hs | 14.4 | 14.4 | 0.95 | 0.22 | 3.07 | +0.627 | +0.819 ± 0.053 | 0.673 | +0.222 | -0.241 |
| phase4_pushpull_3b_play_hs | 20.4 | 20.4 | 0.18 | 0.23 | 0.63 | +0.246 | +0.276 ± 0.058 | 0.079 | +0.034 | -0.041 |
| phase4_pushpull_static | 17.1 | 17.1 | 1.57 | 0.23 | 5.34 | +0.753 | +0.917 ± 0.022 | 0.841 | +0.503 | -0.522 |
| phase4_random_3b | 20.7 | 20.7 | 0.03 | 0.23 | 0.07 | -0.009 | -0.041 ± 0.108 | 0.013 | -0.039 | -0.035 |
| phase4_random_paddle | 17.1 | 17.1 | 0.86 | 0.22 | 2.75 | -0.146 | -0.248 ± 0.405 | 0.215 | -0.121 | +0.029 |
| phase4_symmetric_static | 17.0 | 17.0 | 0.00 | 0.23 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.013 | -0.013 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.014 | +0.985 |
| phase4_pushpull_3b_play_hs | 0.003 | +0.998 |
| phase4_pushpull_static | 0.022 | +0.971 |
| phase4_random_3b | 0.000 | +1.000 |
| phase4_random_paddle | 0.015 | +0.991 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Inhibition (3-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I, motor) |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 13.2 | 4717 | 4716 | 20.6 | 0.001 | 0.184 | +0.946 |
| phase4_pushpull_3b_no_hs | 2.2 | 3030 | 3035 | 14.4 | 0.014 | 0.125 | +0.922 |
| phase4_pushpull_3b_play_hs | 12.9 | 4681 | 4684 | 20.4 | 0.003 | 0.181 | +0.948 |
| phase4_pushpull_static | 6.6 | 3721 | 3712 | 17.1 | 0.022 | 0.146 | +0.940 |
| phase4_random_3b | 13.3 | 4738 | 4738 | 20.7 | 0.000 | 0.185 | +0.946 |
| phase4_random_paddle | 6.6 | 3704 | 3720 | 17.1 | 0.015 | 0.148 | +0.938 |
| phase4_symmetric_static | 6.5 | 3688 | 3688 | 17.0 | 0.000 | 0.156 | +0.925 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.394 | 1.000→1.394 | 0.3963 | 0.3949 | +1.000→+0.000 | 0.000 | 0.47/0.47 | +0.022 |
| phase4_pushpull_3b_no_hs | 1.000→0.359 | 1.000→0.359 | 0.6424 | 0.6412 | +1.000→+0.777 | 0.073 | 0.00/0.00 | -0.105 |
| phase4_pushpull_3b_play_hs | 1.000→1.434 | 1.000→1.434 | 0.4338 | 0.4338 | +1.000→+0.000 | 0.000 | 0.24/0.24 | +0.213 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.403 | 1.007→1.403 | 0.4003 | 0.3958 | -0.128→+0.000 | 0.000 | 0.41/0.41 | +0.033 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.070 | 0.0141 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.031 | 0.1520 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.048 | 0.0199 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.031 | 0.2596 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.023 | 0.3869 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.065 | 0.0194 | 15/15 |

## Interpretation

- 本目录是 4 细胞交叉抑制版的自动表格；完整分析见 `results/phase4_cross_inhibition_report.md`。
- 关键结果：static 0.194 vs symmetric 0.162（+0.031，p=0.152，不显著）；exclusive 0.0221
  （2-cell 0.0217，无分化）；I_up/I_down spike 数差异 <0.5%；no_hs 显著低于 static（−0.048，p=0.020）。
