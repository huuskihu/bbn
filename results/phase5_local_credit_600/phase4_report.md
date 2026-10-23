# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 600.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: pool-specific local for conditions tagged `local` (phase4_pushpull_local_3b, phase4_pushpull_local_3b_no_hs, phase4_pushpull_local_3b_play_hs); global scalar D(t) otherwise
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['phase4_pushpull_local_3b', 'phase4_pushpull_local_3b_no_hs', 'phase4_pushpull_local_3b_play_hs', 'phase4_pushpull_static', 'phase4_pushpull_3b']
- Parallel jobs: 10; total wall: 345 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.151 ± 0.063 | 8.8 | 58.6 | 51.13 | 0.00 | 0.01 |
| phase4_pushpull_local_3b | 0.151 ± 0.051 | 8.8 | 58.6 | 50.60 | 0.00 | 0.01 |
| phase4_pushpull_local_3b_no_hs | 0.220 ± 0.079 | 12.7 | 57.9 | 47.27 | 0.07 | 0.28 |
| phase4_pushpull_local_3b_play_hs | 0.164 ± 0.064 | 9.5 | 58.5 | 50.33 | 0.07 | 0.03 |
| phase4_pushpull_static | 0.204 ± 0.043 | 11.9 | 58.1 | 48.47 | 0.00 | 0.18 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.5 | 21.5 | 0.05 | 0.22 | 0.21 | +0.145 | +0.138 | +0.132 | +0.163 | +0.179 ± 0.046 | 0.034 | -0.012 | -0.039 |
| phase4_pushpull_local_3b | 21.5 | 21.5 | 0.06 | 0.22 | 0.22 | +0.140 | +0.134 | +0.129 | +0.160 | +0.173 ± 0.046 | 0.032 | -0.045 | -0.073 |
| phase4_pushpull_local_3b_no_hs | 18.7 | 18.9 | 2.25 | 0.24 | 8.09 | +0.636 | +0.592 | +0.569 | +0.740 | +0.735 ± 0.107 | 0.551 | +0.429 | -0.446 |
| phase4_pushpull_local_3b_play_hs | 21.3 | 21.3 | 0.26 | 0.23 | 0.83 | +0.229 | +0.200 | +0.191 | +0.264 | +0.266 ± 0.061 | 0.074 | +0.015 | -0.059 |
| phase4_pushpull_static | 17.8 | 17.8 | 1.52 | 0.23 | 5.23 | +0.751 | +0.681 | +0.656 | +0.886 | +0.920 ± 0.012 | 0.847 | +0.512 | -0.478 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.57 | 17.90 | 33.8 | 40 |
| phase4_pushpull_local_3b | 1.56 | 17.87 | 33.8 | 40 |
| phase4_pushpull_local_3b_no_hs | 1.57 | 17.53 | 22.8 | 40 |
| phase4_pushpull_local_3b_play_hs | 1.55 | 17.84 | 33.3 | 40 |
| phase4_pushpull_static | 1.58 | 17.45 | 19.0 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.001 | +0.999 |
| phase4_pushpull_local_3b | 0.001 | +0.999 |
| phase4_pushpull_local_3b_no_hs | 0.031 | +0.950 |
| phase4_pushpull_local_3b_play_hs | 0.004 | +0.997 |
| phase4_pushpull_static | 0.022 | +0.975 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.0 | 0 | 0 | 21.5 | 0.001 | 0.191 | +0.000 | +0.000 |
| phase4_pushpull_local_3b | 0.0 | 0 | 0 | 21.5 | 0.001 | 0.191 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_no_hs | 0.0 | 0 | 0 | 18.8 | 0.031 | 0.155 | +0.000 | +0.000 |
| phase4_pushpull_local_3b_play_hs | 0.0 | 0 | 0 | 21.3 | 0.004 | 0.189 | +0.000 | +0.000 |
| phase4_pushpull_static | 0.0 | 0 | 0 | 17.8 | 0.022 | 0.152 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.370 | 1.000→1.370 | 0.3743 | 0.3718 | +1.000→+0.000 | 0.000 | 0.34/0.34 | -0.088 |
| phase4_pushpull_local_3b | 1.000→1.394 | 1.000→1.402 | 0.3943 | 0.4034 | +1.000→+0.364 | 0.032 | 0.40/0.42 | +0.173 |
| phase4_pushpull_local_3b_no_hs | 1.000→1.204 | 1.000→1.141 | 0.2336 | 0.1915 | +1.000→+0.780 | 0.327 | 0.07/0.04 | -0.201 |
| phase4_pushpull_local_3b_play_hs | 1.000→1.464 | 1.000→1.467 | 0.4635 | 0.4667 | +1.000→+0.426 | 0.040 | 0.35/0.40 | -0.182 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_3b − phase4_pushpull_static | -0.053 | 0.0131 | 15/15 |
| phase4_pushpull_local_3b − phase4_pushpull_static | -0.054 | 0.0057 | 15/15 |
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_static | +0.015 | 0.5119 | 15/15 |
| phase4_pushpull_local_3b_play_hs − phase4_pushpull_static | -0.040 | 0.0537 | 15/15 |
| phase4_pushpull_local_3b_no_hs − phase4_pushpull_3b | +0.069 | 0.0140 | 15/15 |
| phase4_pushpull_local_3b_play_hs − phase4_pushpull_3b | +0.013 | 0.5732 | 15/15 |

## Interpretation

- 本目录是 P1 局部信用的干净批次（信用分配由条件名选择）；完整分析见 `results/phase5_local_credit_report.md`。
- 梯度：`w_diff corr` 0.000（全局 3b）→ 0.780（local_no_hs）/ 0.426（local_play_hs）；H1 支持。
- 行为：local_no_hs 0.220 ≈ static 0.204（+0.015，p=0.512），显著优于全局 3b（+0.069，p=0.014）；
  play_hs 0.164 < static（−0.040，p=0.054）；H2 不支持。
- 稳态：local_3b 仍把 40% 权重推到 w_max，行为 −0.054（p=0.006）；H4 触发，局部信用线停止。
- 首跑的对照污染（全局 `--local-credit` 开关）已修复，旧目录 `../phase5_local_credit_600_bug_globalflag/` 不参与推断。
