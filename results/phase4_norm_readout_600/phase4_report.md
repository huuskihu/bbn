# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: normalized, k_norm=5.00 bins/s, eps=1.0e-03 Hz
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 360 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.173 ± 0.078 | 10.1 | 58.4 | 49.53 | 0.00 | 0.01 |
| phase4_pushpull_3b_no_hs | 0.181 ± 0.051 | 10.5 | 58.3 | 48.87 | 0.00 | 0.24 |
| phase4_pushpull_3b_play_hs | 0.134 ± 0.071 | 7.9 | 59.0 | 52.13 | 0.00 | 0.02 |
| phase4_pushpull_static | 0.202 ± 0.080 | 11.7 | 58.1 | 47.60 | 0.00 | 0.20 |
| phase4_random_3b | 0.159 ± 0.039 | 9.3 | 58.5 | 50.20 | 0.00 | 0.00 |
| phase4_random_paddle | 0.128 ± 0.065 | 7.5 | 58.9 | 52.13 | 0.00 | 0.11 |
| phase4_symmetric_static | 0.162 ± 0.045 | 9.5 | 58.5 | 50.13 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.6 | 21.6 | 0.05 | 0.23 | 0.20 | +0.146 | +0.135 | +0.128 | +0.163 | +0.183 ± 0.059 | 0.037 | -0.010 | -0.034 |
| phase4_pushpull_3b_no_hs | 14.9 | 14.9 | 0.93 | 0.23 | 3.03 | +0.651 | +0.596 | +0.536 | +0.660 | +0.856 ± 0.031 | 0.733 | +0.233 | -0.273 |
| phase4_pushpull_3b_play_hs | 21.3 | 21.3 | 0.16 | 0.22 | 0.60 | +0.229 | +0.199 | +0.193 | +0.255 | +0.271 ± 0.046 | 0.076 | +0.013 | -0.054 |
| phase4_pushpull_static | 17.9 | 17.8 | 1.48 | 0.23 | 5.13 | +0.745 | +0.678 | +0.652 | +0.887 | +0.918 ± 0.017 | 0.843 | +0.457 | -0.492 |
| phase4_random_3b | 21.6 | 21.6 | 0.02 | 0.23 | 0.07 | -0.004 | +0.005 | -0.007 | +0.009 | -0.002 ± 0.108 | 0.011 | -0.050 | -0.050 |
| phase4_random_paddle | 17.7 | 17.7 | 0.80 | 0.22 | 2.64 | -0.140 | -0.092 | -0.089 | -0.158 | -0.219 ± 0.420 | 0.213 | -0.048 | +0.074 |
| phase4_symmetric_static | 17.7 | 17.7 | 0.00 | 0.23 | 0.00 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.006 | -0.006 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_3b_no_hs | 0.014 | +0.987 |
| phase4_pushpull_3b_play_hs | 0.002 | +0.998 |
| phase4_pushpull_static | 0.021 | +0.976 |
| phase4_random_3b | 0.000 | +1.000 |
| phase4_random_paddle | 0.015 | +0.992 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.0 | 0 | 0 | 21.6 | 0.001 | 0.192 | +0.000 | +0.000 |
| phase4_pushpull_3b_no_hs | 0.0 | 0 | 0 | 14.9 | 0.014 | 0.130 | +0.000 | +0.000 |
| phase4_pushpull_3b_play_hs | 0.0 | 0 | 0 | 21.3 | 0.002 | 0.189 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.9 | 0.021 | 0.153 | +0.000 | +0.000 |
| phase4_random_3b | 0.0 | 0 | 0 | 21.6 | 0.000 | 0.192 | +0.000 | +0.000 |
| phase4_random_paddle | 0.0 | 0 | 0 | 17.7 | 0.015 | 0.155 | +0.000 | +0.000 |
| phase4_symmetric_static | 0.0 | 0 | 0 | 17.7 | 0.000 | 0.162 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.386 | 1.000→1.386 | 0.3858 | 0.3858 | +1.000→+0.000 | 0.000 | 0.33/0.33 | +0.097 |
| phase4_pushpull_3b_no_hs | 1.000→0.367 | 1.000→0.368 | 0.6329 | 0.6320 | +1.000→+0.865 | 0.090 | 0.00/0.00 | +0.019 |
| phase4_pushpull_3b_play_hs | 1.000→1.428 | 1.000→1.428 | 0.4276 | 0.4276 | +1.000→+0.000 | 0.000 | 0.16/0.16 | -0.082 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.390 | 1.007→1.390 | 0.3886 | 0.3825 | -0.128→+0.000 | 0.000 | 0.40/0.40 | +0.084 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.074 | 0.0083 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.040 | 0.0990 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | -0.021 | 0.4034 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | -0.068 | 0.0179 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.029 | 0.3276 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.031 | 0.1276 | 15/15 |

## Interpretation

- 本目录是归一化读出（k_norm=5.0）的自动表格；完整分析见 `results/phase4_norm_readout_report.md`。
- 关键结果：static 0.202 / hit 0.167（difference 版本 0.204 / 0.169）；K_eff 0.141→0.177，
  但行为不变；static−random p=0.008，static−symmetric p=0.099；play_hs 显著更差（p=0.018）。
