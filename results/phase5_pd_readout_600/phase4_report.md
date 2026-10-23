# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: pool-specific local for conditions tagged `local` (phase4_pushpull_local_3b_no_hs_pd, phase4_pushpull_local_3b_no_hs); global scalar D(t) otherwise
- homeostasis: point target 20 Hz, off for `no_hs` arms
- short-term plasticity: off
- control: PD readout, v = Kp·Δr + Kp·τ_pred·dΔr/dt with Kp=0.150 bins/s/Hz, τ_pred=50 ms for: phase4_pushpull_local_3b_no_hs_pd, phase4_pushpull_static_pd
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_local_3b_no_hs_pd', 'phase4_pushpull_local_3b_no_hs', 'phase4_pushpull_static_pd', 'phase4_pushpull_static']
- Parallel jobs: 10; total wall: 238 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.220 ± 0.079 | 12.7 | 57.9 | 47.27 | 0.07 | 0.28 |
| phase4_pushpull_local_3b_no_hs_pd | 0.220 ± 0.077 | 12.7 | 57.8 | 47.20 | 0.07 | 0.28 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |
| phase4_pushpull_static_pd | 0.210 ± 0.047 | 12.1 | 57.9 | 47.87 | 0.00 | 0.19 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 18.7 | 18.9 | 2.25 | 0.24 | 8.09 | +0.636 | +0.592 | +0.569 | +0.740 | +0.735 ± 0.107 | 0.551 | +0.429 | -0.446 |
| phase4_pushpull_local_3b_no_hs_pd | 18.8 | 18.9 | 2.14 | 0.24 | 7.69 | +0.632 | +0.587 | +0.560 | +0.744 | +0.747 ± 0.066 | 0.562 | +0.423 | -0.428 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.681 | +0.656 | +0.886 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |
| phase4_pushpull_static_pd | 17.8 | 17.8 | 1.52 | 0.23 | 5.25 | +0.751 | +0.680 | +0.651 | +0.893 | +0.924 ± 0.011 | 0.854 | +0.484 | -0.491 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 1.57 | 17.53 | 22.8 | 40 |
| phase4_pushpull_local_3b_no_hs_pd | 1.58 | 17.56 | 23.0 | 40 |
| phase4_pushpull_static | 1.58 | 17.45 | 19.0 | 40 |
| phase4_pushpull_static_pd | 1.57 | 17.45 | 19.1 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.031 | +0.950 |
| phase4_pushpull_local_3b_no_hs_pd | 0.031 | +0.955 |
| phase4_pushpull_static | 0.022 | +0.975 |
| phase4_pushpull_static_pd | 0.022 | +0.975 |

## Network activity (10-cell)

Mean firing rate over the whole session for the sensory relays (S1–S4), the two excitatory interneurons (E_up/E_down) and the two inhibitory interneurons (I_up/I_down). Zero for 2-cell conditions.

| condition | S (mean of 4) | E_up | E_down | I_up | I_down |
|---|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase4_pushpull_local_3b_no_hs_pd | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase4_pushpull_static | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| phase4_pushpull_static_pd | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 0.0 | 0 | 0 | 18.8 | 0.031 | 0.155 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_no_hs_pd | 0.0 | 0 | 0 | 18.9 | 0.031 | 0.156 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |
| phase4_pushpull_static_pd | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs | 1.000→1.204 | 1.000→1.141 | 0.2336 | 0.1915 | +1.000→+0.780 | 0.327 | 0.07/0.04 | -0.201 |
| phase4_pushpull_local_3b_no_hs_pd | 1.000→1.200 | 1.000→1.161 | 0.2370 | 0.2147 | +1.000→+0.693 | 0.346 | 0.08/0.06 | -0.005 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_pushpull_static_pd | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_static | +0.015 | 0.5127 | 15/15 |
| phase4_pushpull_local_3b_no_hs_pd − phase4_pushpull_local_3b_no_hs | -0.000 | 0.9979 | 15/15 |
| phase4_pushpull_static_pd − phase4_pushpull_static | +0.005 | 0.7219 | 15/15 |
| phase4_pushpull_local_3b_no_hs_pd − phase4_pushpull_static | +0.015 | 0.5006 | 15/15 |

## Interpretation

- 本目录是 P5 PD 读出的自动表格；完整分析见 `results/phase5_pd_readout_report.md`。
- 行为：`local_pd` 0.220 ≡ `local_no_hs` 0.220（p=0.998）；`static_pd` 0.210 vs 0.204（p=0.722）。
- 读出：impact corr 0.735→0.747、0.920→0.924；mean |v| 与差分幅度基本不变。
- H1/H2/H3 均不支持，H4 触发：τ_pred=50 ms 无法补偿 2 s 量级的信息晚到；接口/PD 线停止。
