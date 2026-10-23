# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 120.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 20.0–20.0 Hz  ← rate-range override
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 73 s

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.217 ± 0.167 | 2.5 | 11.9 | 9.67 | 0.00 | 0.04 |
| phase4_pushpull_3b_no_hs | 0.249 ± 0.175 | 2.9 | 11.7 | 9.60 | 0.00 | 0.18 |
| phase4_pushpull_3b_play_hs | 0.278 ± 0.144 | 3.3 | 11.9 | 9.20 | 0.00 | 0.11 |
| phase4_pushpull_static | 0.244 ± 0.179 | 2.8 | 11.7 | 9.53 | 0.00 | 0.19 |
| phase4_random_3b | 0.172 ± 0.160 | 2.0 | 11.9 | 10.20 | 0.00 | 0.02 |
| phase4_random_paddle | 0.119 ± 0.143 | 1.4 | 11.9 | 10.80 | 0.00 | 0.09 |
| phase4_symmetric_static | 0.219 ± 0.148 | 2.6 | 11.8 | 9.93 | 0.07 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 20.9 | 20.8 | 0.32 | 0.24 | 1.07 | +0.346 | +0.389 ± 0.213 | 0.194 | -0.013 | -0.140 |
| phase4_pushpull_3b_no_hs | 16.8 | 16.8 | 1.42 | 0.24 | 4.88 | +0.782 | +0.844 ± 0.075 | 0.718 | +0.392 | -0.307 |
| phase4_pushpull_3b_play_hs | 20.5 | 20.5 | 0.92 | 0.25 | 2.98 | +0.535 | +0.565 ± 0.163 | 0.344 | +0.124 | -0.179 |
| phase4_pushpull_static | 17.2 | 17.3 | 1.49 | 0.24 | 5.22 | +0.789 | +0.857 ± 0.047 | 0.736 | +0.382 | -0.417 |
| phase4_random_3b | 20.7 | 20.7 | 0.15 | 0.23 | 0.44 | -0.080 | -0.093 ± 0.338 | 0.115 | -0.051 | -0.031 |
| phase4_random_paddle | 17.2 | 17.2 | 0.77 | 0.22 | 2.63 | -0.116 | -0.175 ± 0.438 | 0.210 | +0.012 | +0.103 |
| phase4_symmetric_static | 17.3 | 17.3 | 0.00 | 0.24 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | +0.027 | +0.027 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.005 | +0.996 |
| phase4_pushpull_3b_no_hs | 0.021 | +0.978 |
| phase4_pushpull_3b_play_hs | 0.013 | +0.986 |
| phase4_pushpull_static | 0.022 | +0.976 |
| phase4_random_3b | 0.003 | +0.999 |
| phase4_random_paddle | 0.015 | +0.992 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.381 | 1.000→1.381 | 0.3814 | 0.3808 | +1.000→+0.000 | 0.000 | 0.31/0.31 | +0.074 |
| phase4_pushpull_3b_no_hs | 1.000→0.841 | 1.000→0.839 | 0.1672 | 0.1720 | +1.000→+0.987 | 0.194 | 0.00/0.00 | +0.138 |
| phase4_pushpull_3b_play_hs | 1.000→1.431 | 1.000→1.431 | 0.4309 | 0.4308 | +1.000→-0.000 | 0.001 | 0.04/0.04 | -0.174 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.474 | 1.007→1.474 | 0.4713 | 0.4667 | -0.128→+0.000 | 0.000 | 0.53/0.53 | +0.118 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.125 | 0.0470 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.025 | 0.6964 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | +0.006 | 0.9541 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | +0.034 | 0.5664 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.027 | 0.6855 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.053 | 0.3132 | 15/15 |

## Interpretation

### 1. 信号层面：早期信息确实增强（部分支持 H1）

- early 窗口（play 且 ball_x > 0.5）的差分率与 ball_y 相关从 **0.659 → 0.769**，
  mean |diff| 从 **3.09 → 4.90 Hz**；K_eff 从 **0.197 → 0.251 /s**（+27%），
  impact error 从 **1.844 → 1.726 bins**。这说明恒定率确实让位置信息在回合早期更可用。
- 但代价是末端信号减弱：率因子上限从 40 Hz 降到 20 Hz，冲击前斜率从 **4.76 → 2.75 Hz/bin**，
  late（ball_x ≤ 0.5）mean |diff| 从 6.82 → 5.53，冲击前相关从 0.919 → 0.852。
  这不是单纯的“把信息提前”，而是用末端信噪比换早期信噪比。

### 2. 行为层面：无法判定（对照漂移大于效应）

- static：rally 0.214 → 0.244，hit 0.168 → 0.180，看起来略好。
- 但 frozen-paddle 对照（`symmetric_static`，差分恒 0、球拍完全不动）从 0.106 漂到 **0.219**，
  hit 从 0.089 漂到 **0.171**。球拍静止时理论命中率是 1/7 ≈ 0.143；两次运行分别落在两侧，
  说明 ~14 rallies/seed 的行为指标有 ~0.1 的采样噪声。
- static − symmetric = +0.025（p = 0.696）；static − random paddle = +0.125（p = 0.047），
  但 random paddle 的 0.119 本身是被随机大速度伤害的基线（见 gain 敏感性），
  而 symmetric 的 0.219 与 static 的 0.244 无法区分。
- **因此 H1 在行为层面不成立**：恒定率带来的信号改善没有超出行为指标的噪声地板；
  H2（symmetric 应保持 ~0.1）也被对照漂移破坏——这不是机制变化，而是有限样本噪声的量化。

### 3. 可塑性仍然没有收益

- `no_hs` 0.249 ≈ static 0.244（p = 0.954）；`3b` 0.217（p = 0.686）；
  `play_hs` 0.278（p = 0.566）。没有任何条件超过 static。
- `random_3b` 的冲击前差分率与 ball_y 的相关为负（−0.093），没有学到位置映射。
- **H3 不支持**：即使把信息提前，全局标量 D(t) 仍未解决 up/down 两池的信用分配。

### 4. 稳态饱和不变（支持 H4）

- `3b` 的 `frac at w_max` = 0.308，`mean|w_up−w_down|` = 0.000，读出斜率仍约 0.77 Hz/bin；
  `play_hs` 的梯度相关 ≈ 0.000。稳态抹掉差分结构与感觉率是否恒定无关。

### 5. 判定与下一步

- H1：信号层面部分支持（early corr / |diff| / K_eff 上升），行为层面不支持。
- H2：不成立（对照从 0.106 漂到 0.219；是噪声，不是机制）。
- H3：不支持（无学习收益）。
- H4：支持（稳态饱和不变）。
- 结论：**20/20 Hz 恒定率不是足够的修复**。它把信号从末端搬到早期，但没有同时保住末端增益；
  行为效应被噪声淹没。更强但仍需预注册的检验是“保末端增益的早期增强”（例如 20–40 Hz）
  或读出归一化；在做跨版本行为比较前，必须先提高 rally 数（更长会话/更多 seeds）。
- 不因本结果回头改率值；本版本到此为止。

