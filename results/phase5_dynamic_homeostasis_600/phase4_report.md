# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: pool-specific local for conditions tagged `local` (phase4_pushpull_local_3b_dyn, phase4_pushpull_local_3b_no_hs); global scalar D(t) otherwise
- homeostasis: functional band [5, 30] Hz, play-only, α=0.05 for: phase4_pushpull_local_3b_dyn, phase4_pushpull_dyn_3b
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_local_3b_dyn', 'phase4_pushpull_dyn_3b', 'phase4_pushpull_local_3b_no_hs', 'phase4_pushpull_static', 'phase4_pushpull_3b']
- Parallel jobs: 10; total wall: 300 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.151 ± 0.063 | 8.8 | 58.6 | 51.13 | 0.00 | 0.01 |
| phase4_pushpull_dyn_3b | 0.183 ± 0.058 | 10.7 | 58.3 | 49.60 | 0.00 | 0.05 |
| phase4_pushpull_local_3b_dyn | 0.196 ± 0.049 | 11.4 | 58.1 | 48.00 | 0.00 | 0.06 |
| phase4_pushpull_local_3b_no_hs | 0.220 ± 0.079 | 12.7 | 57.9 | 47.27 | 0.07 | 0.28 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.5 | 21.5 | 0.05 | 0.22 | 0.21 | +0.145 | +0.138 | +0.132 | +0.163 | +0.179 ± 0.046 | 0.034 | -0.012 | -0.039 |
| phase4_pushpull_dyn_3b | 21.3 | 21.3 | 0.41 | 0.23 | 1.43 | +0.321 | +0.278 | +0.266 | +0.360 | +0.381 ± 0.076 | 0.150 | +0.019 | -0.115 |
| phase4_pushpull_local_3b_dyn | 21.5 | 21.5 | 0.55 | 0.23 | 1.75 | +0.310 | +0.277 | +0.261 | +0.354 | +0.353 ± 0.076 | 0.130 | +0.074 | -0.058 |
| phase4_pushpull_local_3b_no_hs | 18.7 | 18.9 | 2.25 | 0.24 | 8.09 | +0.636 | +0.592 | +0.569 | +0.740 | +0.735 ± 0.107 | 0.551 | +0.429 | -0.446 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.681 | +0.656 | +0.886 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.57 | 17.90 | 33.8 | 40 |
| phase4_pushpull_dyn_3b | 1.59 | 17.89 | 32.7 | 40 |
| phase4_pushpull_local_3b_dyn | 1.57 | 17.84 | 33.8 | 40 |
| phase4_pushpull_local_3b_no_hs | 1.57 | 17.53 | 22.8 | 40 |
| phase4_pushpull_static | 1.58 | 17.45 | 19.0 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_dyn_3b | 0.006 | +0.995 |
| phase4_pushpull_local_3b_dyn | 0.008 | +0.995 |
| phase4_pushpull_local_3b_no_hs | 0.031 | +0.950 |
| phase4_pushpull_static | 0.022 | +0.975 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.0 | 0 | 0 | 21.5 | 0.001 | 0.191 | +0.000 | +0.000 |
| phase4_pushpull_dyn_3b | 0.0 | 0 | 0 | 21.3 | 0.006 | 0.187 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_dyn | 0.0 | 0 | 0 | 21.5 | 0.008 | 0.188 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_no_hs | 0.0 | 0 | 0 | 18.8 | 0.031 | 0.155 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.370 | 1.000→1.370 | 0.3743 | 0.3718 | +1.000→+0.000 | 0.000 | 0.34/0.34 | -0.088 |
| phase4_pushpull_dyn_3b | 1.000→1.431 | 1.000→1.431 | 0.4312 | 0.4312 | +1.000→+0.000 | 0.000 | 0.14/0.14 | +0.039 |
| phase4_pushpull_local_3b_dyn | 1.000→1.448 | 1.000→1.463 | 0.4484 | 0.4629 | +1.000→+0.498 | 0.049 | 0.25/0.29 | +0.223 |
| phase4_pushpull_local_3b_no_hs | 1.000→1.204 | 1.000→1.141 | 0.2336 | 0.1915 | +1.000→+0.780 | 0.327 | 0.07/0.04 | -0.201 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_3b − phase4_pushpull_static | -0.053 | 0.0131 | 15/15 |
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_static | +0.015 | 0.5162 | 15/15 |
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_3b | +0.069 | 0.0150 | 15/15 |
| phase4_pushpull_local_3b_dyn − phase4_pushpull_static | -0.008 | 0.6431 | 15/15 |
| phase4_pushpull_local_3b_dyn − phase4_pushpull_local_3b_no_hs | -0.023 | 0.3336 | 15/15 |
| phase4_pushpull_dyn_3b − phase4_pushpull_static | -0.021 | 0.2812 | 15/15 |
| phase4_pushpull_dyn_3b − phase4_pushpull_3b | +0.033 | 0.1533 | 15/15 |

## Interpretation

- 本目录是 P2 动态稳态目标带的自动表格；完整分析见 `results/phase5_dynamic_homeostasis_report.md`。
- 饱和：`3b` at w_max 0.34 → `dyn_3b` 0.14；impact corr 0.179 → 0.381，但 `w_diff corr` 仍为 0.000。
- 局部 D + 动态带：`w_diff corr` 0.364（固定点）→ 0.498（动态带）→ 0.780（无稳态）；
  at w_max 0.40 → 0.25 → 0.07；行为 0.196，与 static 0.204 无差异（p=0.643）。
- H1 不支持（at w_max >0.10、corr 0.498 <0.5）；H2 不支持；H3 支持；H4 未触发。
- 按预注册停止规则，动态稳态带线停止；不再调边界或 α。
