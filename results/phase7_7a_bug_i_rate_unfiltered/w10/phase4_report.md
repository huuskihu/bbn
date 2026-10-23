# Phase 4: Two-pool differential readout (2 cells)

- Config: `config/phase4.yaml`
- Duration: 60.0 s; seeds: [0, 1, 2]
- ball_speed: 0.500 bins/s (approach ≈ 2.0 s)  (main Phase 4 value)
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- readout: difference (v = k·(up−down))
- background activity: 0.00 Hz, weight=40.0 nS/spike (independent per pool)
- credit assignment: global scalar D(t)
- homeostasis: point target 20 Hz, all periods
- short-term plasticity: off
- control: proportional, v = Kp·Δr
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- inhibitory network: off (2-cell network)
- Conditions: ['rec_static']
- Parallel jobs: 3; total wall: 48 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| rec_static | 0.222 ± 0.255 | 1.3 | 6.0 | 5.00 | 0.00 | 0.07 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | norm corr | early norm | late norm | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rec_static | 106.5 | 106.4 | 2.22 | 0.24 | 1.98 | +0.008 | +0.023 | +0.015 | +0.008 | +0.415 ± 0.117 | 0.182 | +0.114 | +0.057 |

## Background activity

Mean motor rate during quiet rest (timeout after the unpredictable feedback has ended) and during play. With `bg_noise_hz=0` the quiet-rest rate is 0; with spontaneous activity it should be in the 1–5 Hz target range.

| condition | quiet-rest rate (Hz) | rest rate (Hz) | play rate (Hz) | bg weight (nS) |
|---|---:|---:|---:|---:|
| rec_static | 98.54 | 113.35 | 85.0 | 40 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| rec_static | 0.041 | +0.992 |

## Network activity (10-cell)

Mean firing rate over the whole session for the sensory relays (S1–S4), the two excitatory interneurons (E_up/E_down) and the two inhibitory interneurons (I_up/I_down). Zero for 2-cell conditions.

| condition | S (mean of 4) | E_up | E_down | I_up | I_down |
|---|---:|---:|---:|---:|---:|
| rec_static | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Latency readout (v0.21.0)

`lat corr` is the tick-level correlation between the frame first-spike latency difference (down − up) and ball_y during play; `Δt P95` is the 95th percentile of |Δt| in ms; `zero` is the fraction of playing ticks with no spike in either pool during the frame.

| condition | lat corr | Δt P95 (ms) | zero frac |
|---|---:|---:|---:|
| rec_static | +0.000 | 0.0 | 0.00 |

## Inhibition (3/4-cell version)

Only meaningful when inhibition is on. `I rate` is the 300 ms windowed total inhibitory rate during play; `corr(I, motor)` is the tick-level correlation between I rate and the mean motor rate.

| condition | I rate (Hz) | I_up spikes | I_down spikes | motor rate (Hz) | exclusive | both spike | corr(I_up−I_down, y) | corr(I_up, I_down) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rec_static | 0.0 | 0 | 0 | 106.5 | 0.041 | 0.879 | +0.000 | +0.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rec_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|

## Interpretation

- 见下方人工结论（基于本表，不调参）。
