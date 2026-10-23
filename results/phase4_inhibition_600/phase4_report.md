# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory interneuron: ON (g_inh=10.0 nS/spike, tau=10.0 ms, E_inh=-80.0 mV)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 524 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.163 ± 0.076 | 9.5 | 58.5 | 50.00 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.161 ± 0.058 | 9.4 | 58.6 | 50.80 | 0.00 | 0.11 |
| phase4_pushpull_3b_play_hs | 0.161 ± 0.074 | 9.3 | 58.5 | 50.20 | 0.00 | 0.02 |
| phase4_pushpull_static | 0.222 ± 0.051 | 12.8 | 57.9 | 46.87 | 0.07 | 0.19 |
| phase4_random_3b | 0.149 ± 0.049 | 8.7 | 58.6 | 50.80 | 0.07 | 0.00 |
| phase4_random_paddle | 0.107 ± 0.056 | 6.3 | 59.1 | 53.53 | 0.00 | 0.09 |
| phase4_symmetric_static | 0.162 ± 0.045 | 9.5 | 58.5 | 50.13 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 20.2 | 20.1 | 0.06 | 0.23 | 0.21 | +0.147 | +0.177 ± 0.045 | 0.033 | -0.031 | -0.060 |
| phase4_pushpull_3b_no_hs | 13.9 | 13.9 | 0.92 | 0.23 | 3.09 | +0.637 | +0.823 ± 0.026 | 0.678 | +0.254 | -0.268 |
| phase4_pushpull_3b_play_hs | 19.9 | 19.9 | 0.17 | 0.23 | 0.62 | +0.239 | +0.278 ± 0.054 | 0.080 | +0.018 | -0.059 |
| phase4_pushpull_static | 16.4 | 16.3 | 1.55 | 0.24 | 5.37 | +0.755 | +0.930 ± 0.013 | 0.864 | +0.503 | -0.604 |
| phase4_random_3b | 20.2 | 20.2 | 0.02 | 0.22 | 0.08 | -0.013 | -0.033 ± 0.106 | 0.012 | -0.023 | -0.022 |
| phase4_random_paddle | 16.3 | 16.3 | 0.81 | 0.22 | 2.78 | -0.162 | -0.222 ± 0.472 | 0.258 | -0.061 | +0.091 |
| phase4_symmetric_static | 16.3 | 16.3 | 0.00 | 0.23 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.014 | -0.014 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.013 | +0.984 |
| phase4_pushpull_3b_play_hs | 0.002 | +0.998 |
| phase4_pushpull_static | 0.022 | +0.970 |
| phase4_random_3b | 0.000 | +1.000 |
| phase4_random_paddle | 0.015 | +0.991 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Inhibition (3-cell version)

Only meaningful when `--inhibitory` is on. `I rate` is the 300 ms windowed inhibitory-interneuron rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | motor rate (Hz) | exclusive | both spike | corr(I, motor) |
|---|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 18.7 | 20.2 | 0.001 | 0.183 | +0.927 |
| phase4_pushpull_3b_no_hs | 18.7 | 13.9 | 0.013 | 0.124 | +0.633 |
| phase4_pushpull_3b_play_hs | 18.5 | 19.9 | 0.002 | 0.181 | +0.921 |
| phase4_pushpull_static | 18.8 | 16.4 | 0.022 | 0.142 | +0.985 |
| phase4_random_3b | 18.7 | 20.2 | 0.000 | 0.184 | +0.930 |
| phase4_random_paddle | 18.4 | 16.3 | 0.015 | 0.145 | +0.979 |
| phase4_symmetric_static | 18.7 | 16.3 | 0.000 | 0.153 | +0.984 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.402 | 1.000→1.402 | 0.4023 | 0.4023 | +1.000→+0.000 | 0.000 | 0.40/0.40 | -0.039 |
| phase4_pushpull_3b_no_hs | 1.000→0.445 | 1.000→0.447 | 0.5567 | 0.5590 | +1.000→+0.835 | 0.066 | 0.00/0.00 | -0.042 |
| phase4_pushpull_3b_play_hs | 1.000→1.448 | 1.000→1.448 | 0.4477 | 0.4477 | +1.000→+0.000 | 0.000 | 0.33/0.33 | -0.146 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.441 | 1.007→1.441 | 0.4388 | 0.4342 | -0.128→+0.000 | 0.000 | 0.53/0.53 | -0.018 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.115 | 0.0000 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.059 | 0.0025 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.061 | 0.0060 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.061 | 0.0170 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.059 | 0.0204 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.043 | 0.0407 | 15/15 |

## Interpretation

- 本目录是 3 细胞抑制版的自动表格；完整分析见 `results/phase4_inhibition_report.md`。
- 关键结果：static 0.222 vs symmetric 0.162（+0.059，p=0.0025）、vs random 0.107（+0.115，p<0.0001）；
  exclusive 0.022（2-cell 0.0217，无分化）；3b/no_hs/play_hs 均显著低于 static（−0.059/−0.061/−0.061）。
