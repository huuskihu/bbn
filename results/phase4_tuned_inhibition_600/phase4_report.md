# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: tuned (4-cell: I_up/I_down receive 8-channel sensory with push-pull weights ×1.00; g_inh=10.0 nS/spike, E_inh=-80.0 mV)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 742 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.172 ± 0.053 | 10.0 | 58.5 | 50.47 | 0.00 | 0.04 |
| phase4_pushpull_3b_no_hs | 0.173 ± 0.061 | 10.1 | 58.3 | 49.47 | 0.07 | 0.12 |
| phase4_pushpull_3b_play_hs | 0.193 ± 0.058 | 11.2 | 58.1 | 48.47 | 0.00 | 0.06 |
| phase4_pushpull_static | 0.228 ± 0.064 | 13.1 | 57.7 | 46.53 | 0.00 | 0.21 |
| phase4_random_3b | 0.173 ± 0.058 | 10.1 | 58.3 | 49.47 | 0.00 | 0.04 |
| phase4_random_paddle | 0.095 ± 0.047 | 5.6 | 59.3 | 54.13 | 0.00 | 0.09 |
| phase4_symmetric_static | 0.180 ± 0.052 | 10.5 | 58.3 | 48.80 | 0.07 | 0.04 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.1 | 21.1 | 0.45 | 0.23 | 1.26 | +0.212 | +0.350 ± 0.080 | 0.129 | -0.013 | -0.112 |
| phase4_pushpull_3b_no_hs | 14.7 | 14.7 | 1.04 | 0.23 | 3.51 | +0.645 | +0.842 ± 0.035 | 0.709 | +0.310 | -0.304 |
| phase4_pushpull_3b_play_hs | 20.9 | 20.9 | 0.56 | 0.23 | 1.65 | +0.274 | +0.365 ± 0.103 | 0.143 | +0.045 | -0.092 |
| phase4_pushpull_static | 17.2 | 17.3 | 1.72 | 0.24 | 5.97 | +0.762 | +0.929 ± 0.015 | 0.863 | +0.569 | -0.571 |
| phase4_random_3b | 21.1 | 21.1 | 0.41 | 0.23 | 1.11 | +0.163 | +0.255 ± 0.150 | 0.086 | -0.004 | -0.067 |
| phase4_random_paddle | 17.2 | 17.2 | 0.80 | 0.22 | 2.69 | +0.042 | +0.087 ± 0.472 | 0.216 | -0.003 | -0.045 |
| phase4_symmetric_static | 17.2 | 17.1 | 0.46 | 0.23 | 1.28 | +0.441 | +0.621 ± 0.073 | 0.390 | +0.078 | -0.145 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.006 | +0.997 |
| phase4_pushpull_3b_no_hs | 0.014 | +0.983 |
| phase4_pushpull_3b_play_hs | 0.008 | +0.995 |
| phase4_pushpull_static | 0.024 | +0.967 |
| phase4_random_3b | 0.006 | +0.998 |
| phase4_random_paddle | 0.015 | +0.992 |
| phase4_symmetric_static | 0.007 | +0.997 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 18.7 | 2994 | 3023 | 21.1 | 0.006 | 0.186 | +0.195 | +0.757 |
| phase4_pushpull_3b_no_hs | 18.5 | 2984 | 2994 | 14.7 | 0.014 | 0.128 | +0.199 | +0.760 |
| phase4_pushpull_3b_play_hs | 18.6 | 3032 | 3040 | 20.9 | 0.008 | 0.184 | +0.196 | +0.757 |
| phase4_pushpull_static | 18.9 | 3127 | 3140 | 17.2 | 0.024 | 0.147 | +0.196 | +0.761 |
| phase4_random_3b | 18.5 | 2989 | 2976 | 21.1 | 0.006 | 0.187 | +0.197 | +0.756 |
| phase4_random_paddle | 18.3 | 2857 | 2832 | 17.2 | 0.015 | 0.151 | +0.195 | +0.760 |
| phase4_symmetric_static | 18.6 | 3010 | 2993 | 17.1 | 0.007 | 0.154 | +0.198 | +0.756 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.349 | 1.000→1.352 | 0.3493 | 0.3530 | +1.000→+0.036 | 0.006 | 0.20/0.20 | -0.015 |
| phase4_pushpull_3b_no_hs | 1.000→0.444 | 1.000→0.444 | 0.5562 | 0.5565 | +1.000→+0.704 | 0.061 | 0.00/0.00 | +0.005 |
| phase4_pushpull_3b_play_hs | 1.000→1.437 | 1.000→1.437 | 0.4374 | 0.4371 | +1.000→+0.085 | 0.007 | 0.15/0.14 | -0.091 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.404 | 1.007→1.408 | 0.4026 | 0.4007 | -0.128→-0.053 | 0.005 | 0.47/0.47 | -0.135 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.133 | 0.0000 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.048 | 0.0330 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.055 | 0.0236 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.035 | 0.1256 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.057 | 0.0119 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.078 | 0.0003 | 15/15 |

## Interpretation

- 本目录是差分调谐抑制版的自动表格；完整分析见 `results/phase4_tuned_inhibition_report.md`。
- 关键结果：static 0.228 为四臂最高，但仅比 2-cell 0.204 高 0.024；corr(I_up−I_down, y)=0.196
  （H1 要求 >0.5，失败）；I_up/I_down spike 数差异 <1%；no_hs/3b 显著低于 static。
- 注意：tuned 臂的 symmetric 不再是冻结球拍（调谐 I 注入差分），static−symmetric 不能当作干净结构对照。
