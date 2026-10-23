# Phase 4: Two-pool differential readout (2 cells)

- Config: `config\phase4.yaml`
- Duration: 120.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- velocity_gain: 0.150 bins/s/Hz  (main Phase 4 value)
- sensory rate factor: 4.0–40.0 Hz  (distance-gated, main Phase 4)
- Conditions: ['phase4_pushpull_3b', 'phase4_pushpull_3b_no_hs', 'phase4_pushpull_3b_play_hs', 'phase4_pushpull_static', 'phase4_random_3b', 'phase4_symmetric_static', 'phase4_random_paddle']
- Parallel jobs: 10; total wall: 67 s
- Companion sensitivity report: `results/phase4_gain_sensitivity.md` (velocity_gain 0.30/0.60; refutes the simple gain-limit hypothesis)
- Constant-rate experiment (v0.8.0): `results/phase4_const_rate/phase4_report.md`
- 600 s long-session follow-up (v0.9.0): `results/phase4_long_session.md` — behavior conclusions use this version

## Structure

Two Pospischil RS cells (up/down) receive the **same** 8-channel sensory event times and the same feedback stimulation, each with its own plastic weights. Paddle velocity = k * (rate_up - rate_down), so common drive from ball distance and feedback cancels.

`phase4_pushpull_static` already contains a hand-set anti-symmetric weight profile, so plasticity must be judged against it, not only against random paddle.

## Behavior

| condition | avg rally | hits | misses | aces | long rallies | mean |v| |
|---|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 0.200 ± 0.117 | 2.4 | 11.9 | 9.87 | 0.00 | 0.03 |
| phase4_pushpull_3b_no_hs | 0.280 ± 0.138 | 3.3 | 11.7 | 9.00 | 0.00 | 0.18 |
| phase4_pushpull_3b_play_hs | 0.244 ± 0.150 | 2.9 | 11.8 | 9.40 | 0.00 | 0.11 |
| phase4_pushpull_static | 0.214 ± 0.130 | 2.5 | 11.9 | 9.93 | 0.00 | 0.18 |
| phase4_random_3b | 0.169 ± 0.120 | 2.0 | 11.9 | 10.13 | 0.00 | 0.01 |
| phase4_random_paddle | 0.141 ± 0.155 | 1.7 | 11.9 | 10.60 | 0.00 | 0.09 |
| phase4_symmetric_static | 0.106 ± 0.097 | 1.3 | 12.0 | 11.07 | 0.00 | 0.00 |

## Readout information

`impact corr` = Pearson correlation over rallies between the mean rate difference in the last 300 ms before impact and the ball y at impact (pooled per seed, then averaged). `play corr` is the tick-level correlation restricted to ticks where the game is running (rest timeouts excluded).

| condition | rate up (Hz) | rate down (Hz) | mean |diff| (all) | play fraction | play |diff| | play corr | impact corr | impact R² | up corr | down corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 21.5 | 21.4 | 0.27 | 0.24 | 0.96 | +0.314 | +0.395 ± 0.100 | 0.165 | -0.122 | -0.215 |
| phase4_pushpull_3b_no_hs | 17.3 | 17.3 | 1.43 | 0.25 | 4.69 | +0.711 | +0.919 ± 0.038 | 0.845 | +0.387 | -0.492 |
| phase4_pushpull_3b_play_hs | 20.8 | 20.9 | 0.89 | 0.24 | 3.03 | +0.507 | +0.586 ± 0.150 | 0.364 | +0.013 | -0.281 |
| phase4_pushpull_static | 18.0 | 18.0 | 1.47 | 0.24 | 4.99 | +0.746 | +0.926 ± 0.038 | 0.858 | +0.462 | -0.499 |
| phase4_random_3b | 21.4 | 21.4 | 0.14 | 0.23 | 0.40 | -0.009 | +0.011 ± 0.254 | 0.061 | +0.126 | +0.126 |
| phase4_random_paddle | 17.9 | 17.9 | 0.83 | 0.23 | 2.69 | -0.141 | -0.237 ± 0.428 | 0.227 | -0.111 | +0.021 |
| phase4_symmetric_static | 17.8 | 17.8 | 0.00 | 0.22 | 0.00 | +0.000 | +0.000 ± 0.000 | 0.000 | -0.056 | -0.056 |

## Motor differentiation

Fraction of ticks in which exactly one pool spikes, and the tick-level correlation between the two pools' rates. Shared input and shared feedback drive both pools together; true motor differentiation would show up as higher exclusivity and lower co-activity.

| condition | exclusive spiking | rate up/down corr |
|---|---:|---:|
| phase4_pushpull_3b | 0.004 | +0.997 |
| phase4_pushpull_3b_no_hs | 0.022 | +0.977 |
| phase4_pushpull_3b_play_hs | 0.012 | +0.988 |
| phase4_pushpull_static | 0.021 | +0.977 |
| phase4_random_3b | 0.003 | +0.999 |
| phase4_random_paddle | 0.015 | +0.992 |
| phase4_symmetric_static | 0.000 | +1.000 |

## Weights and plasticity

| condition | w_up init→final | w_down init→final | |Δw| up | |Δw| down | corr(w_up−w_down, channel) init→final | mean |w_up−w_down| | frac at w_max (up/down) | corr(w_up+w_down, channel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| phase4_pushpull_3b | 1.000→1.384 | 1.000→1.384 | 0.3836 | 0.3836 | +1.000→+0.000 | 0.000 | 0.17/0.17 | +0.056 |
| phase4_pushpull_3b_no_hs | 1.000→0.794 | 1.000→0.798 | 0.2261 | 0.2226 | +1.000→+0.977 | 0.194 | 0.00/0.00 | +0.027 |
| phase4_pushpull_3b_play_hs | 1.000→1.421 | 1.000→1.421 | 0.4216 | 0.4211 | +1.000→+0.030 | 0.001 | 0.07/0.07 | +0.154 |
| phase4_pushpull_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +1.000→+1.000 | 0.229 | 0.00/0.00 | +0.000 |
| phase4_random_3b | 1.002→1.396 | 1.007→1.396 | 0.3931 | 0.3887 | -0.128→+0.000 | 0.000 | 0.18/0.18 | -0.244 |
| phase4_random_paddle | 1.002→1.002 | 1.007→1.007 | 0.0000 | 0.0000 | -0.128→-0.128 | 0.130 | 0.00/0.00 | +0.022 |
| phase4_symmetric_static | 1.000→1.000 | 1.000→1.000 | 0.0000 | 0.0000 | +0.000→+0.000 | 0.000 | 0.00/0.00 | +0.000 |

## Two-sample permutation tests (rally length)

Conditions do **not** share RNG streams: different actions change the Poisson sensory event counts, so seed labels are not paired. Tests are two-sided label-shuffling permutations (20,000), descriptive only — no multiple-comparison correction.

| contrast | mean diff | p | n_a / n_b |
|---|---:|---:|---:|
| phase4_pushpull_static − phase4_random_paddle | +0.072 | 0.1807 | 15/15 |
| phase4_pushpull_static − phase4_symmetric_static | +0.108 | 0.0180 | 15/15 |
| phase4_pushpull_3b_no_hs − phase4_pushpull_static | +0.066 | 0.2015 | 15/15 |
| phase4_pushpull_3b_play_hs − phase4_pushpull_static | +0.031 | 0.5592 | 15/15 |
| phase4_pushpull_3b − phase4_pushpull_static | -0.014 | 0.7714 | 15/15 |
| phase4_random_3b − phase4_random_paddle | +0.028 | 0.6268 | 15/15 |

## Interpretation

### 1. 差分读出确实解决了信息瓶颈（结构性正结果）

- `phase4_pushpull_static` 的冲击前差分率与 ball_y 的 pooled r = **+0.919**（斜率 +4.76 Hz/bin），
  而 `phase4_random_3b` 只有 r = +0.014。up 池与 down 池对 ball_y 的相关系数分别为 +0.46 / −0.50，
  方向相反，说明差分确实抵消了共同的距离/反馈驱动，保留了两个池对球位置的相反调谐。
- 单细胞对照（Phase 1 修复协议后重跑，120 s）只有 R² = 0.007、斜率 −0.22 Hz/bin，且符号是错误的。
  两池差分把“球在哪”变成了可读的方向信号，这一条成立。Phase 3 `static_full` 的 rally（0.178）
  与 Phase 4 `pushpull_static`（0.214）差异不大，且每 seed 只有 ~12 个 rally；优势来自读出结构，
  不是多细胞涌现。

### 2. 行为增益很小；瓶颈不是简单的标量增益

- 平均 rally：static 0.214，random paddle 0.141，symmetric 0.106。
  static vs symmetric +0.108（p = 0.018）；static vs random paddle +0.072（p = 0.181，不显著）。
- 预注册的 Tier 1 增益敏感性（`velocity_gain` 0.15 / 0.30 / 0.60，见
  `results/phase4_gain_sensitivity.md`）**否定了“提高增益就能改善”的假设**：
  static 的 rally 为 0.214 → 0.201 → 0.246（非单调），hit rate 0.168 → 0.151 → 0.180；
  但 impact error 单调下降（1.84 → 1.64 → 1.32），play |v| 从 0.18 升到 0.60。
  更关键的是，play 期速度–误差回归的 K_eff 始终 ≈ **0.20 /s**，不随 gain 缩放。
- 预注册的恒常率实验（v0.8.0：感觉率 20/20 Hz，见 `results/phase4_const_rate/phase4_report.md`）
  在信号层面支持“早期信息不足”：early（ball_x>0.5）差分率与 ball_y 的相关从 0.659 升到 0.769，
  mean |diff| 从 3.09 升到 4.90 Hz，K_eff 0.197→0.251，impact error 1.844→1.726。
  但它同时把末端率因子从 40 降到 20 Hz，冲击前斜率从 4.76 降到 2.75 Hz/bin；
  行为层面不可判定：frozen-paddle 对照的 rally 从 0.106 漂移到 0.219（hit 0.089→0.171），
  而 static 只从 0.214 变到 0.244；static − symmetric 的 p = 0.696。
- 解释：感觉率随 ball_x 从 4 Hz 升到 40 Hz，控制信息集中在回合末端；300 ms 读出窗口 + 2 s 回合
  使提高增益只放大末端响应，不能把信息提前。恒常率只是把信号从末端搬到早期，
  并没有同时保住末端增益。要改善需要改变读出的时间形状而不牺牲末端信噪比，
  或延长回合/放慢球；单纯调 `velocity_gain` 或把率设成常数都不够。
- **600 s 长会话（v0.9.0，~60 rallies/seed）解决了功效问题**：frozen-paddle 的 hit
  0.138/0.152 ≈ 理论 1/7；static 比 symmetric 高 +0.042/+0.056（p=0.016/0.018），
  比 random paddle 高 +0.079/+0.111（p=0.0002/0.0001）；恒定率没有额外收益
  （+0.031，p=0.183）。可塑性在长会话中变差：3b −0.053/−0.083（p=0.013/0.002），
  no_hs 的 T1→T2 hit 从 0.190 降到 0.109（p=0.0001）。详见 `results/phase4_long_session.md`。
- 每个回合后固定 8 s timeout（4 s 不可预测 + 4 s rest），play fraction 只有约 0.24；
  120 s 内每条件只有 ~12 个 rally，600 s 版本约 60 个，行为结论以后者为准。

### 3. 可塑性没有带来可靠增益，稳态还会抹掉差分编码

- `phase4_pushpull_3b` 与 static 基本持平（−0.014，p = 0.771）；`play_hs` +0.031（p = 0.559）；
  `no_hs` 均值最高（0.280）但差异 +0.066（p = 0.202），不能称为学习效应。
  在 gain=0.60 的敏感性版本中，3b 显著更差（−0.152，p = 0.010）；
  在 600 s 长会话中，3b 两臂都显著更差（−0.053/−0.083，p=0.013/0.002），
  no_hs 在 T1→T2 从 0.190 降到 0.109（p=0.0001）。**可塑性在长会话中有害，而不只是无效。**
- `phase4_random_3b`（随机初始权重 + 三因子）与 random paddle 无差异（+0.028，p = 0.627），
  差分读出也没有获得 ball_y 信息（r = 0.014）。三因子规则没有学会位置映射。
- 稳态是差分结构的杀手：完整稳态下两个池的权重在每个通道上变成**完全相同**
  （corr(w_up−w_down, channel) = 0.000，mean |w_up−w_down| = 0.000，17% 权重顶在 w_max），
  读出斜率从 4.76 掉到 0.77 Hz/bin。机制有两段：
  1. 8 s rest 期间细胞完全沉默，1 s 一次的稳态缩放按 20 Hz 目标以约 1.16×/s 上调权重，
     数秒内把两个池都推到 `w_max`，差异被饱和抹平；
  2. 对局期的乘性归一化把每个池的平均权重拉向同一目标，进一步压缩两池的增益差。
- 只在 play 期施加稳态（`play_hs`）能缓解但不能保住梯度（最终 corr = 0.030，斜率 1.94 Hz/bin），
  说明只要保留“每池独立归一化到同一目标率”，push-pull 的增益差就难以长期维持。
  注意 play_hs 的实现仍会在每个 epoch 的第一 tick 用 rest 末尾的零率窗口做一次上调，
  所以它只是减少、而非消除静息期的稳态饱和。
- `no_hs` 保留了梯度（corr = 0.977，mean |w_up−w_down| = 0.194），读出 r = 0.909，
  但 STDP 本身在 120 s 内只造成 |Δw| ≈ 0.22，且两个池的更新大部分是共同的，
  没有产生“up 池增强高 y 通道、down 池增强低 y 通道”的差异化学习。
  在一个全局标量 D(t) 下，两个池收到相同的奖励与几乎相同的资格迹，信用分配问题没有解决。

### 4. 协议 bug（重要，已修复并重跑）

- 旧实现中 rest 只冻结球拍、球继续以 0.5/s 前进：每次 miss 都会在 2 s 后再次到达并重置 rest，
  于是第一次 miss 之后系统永久锁在休息态。旧 Phase 4 trace 实测 94.5% 的 tick 无球拍动作；
  旧 Phase 1/3 的 60 次事件/120 s（2 s 周期）也与永久 rest 模式一致。
  “平均 rally 0.16–0.18”主要是球重生后偶然落在静止球拍附近，而不是闭环控制结果。
- 修复：rest 期间暂停整个游戏（球与球拍都冻结）。Phase 1/3 已用修复后的协议重跑；
  本报告的所有结论均基于修复后的 Phase 4 数据。

### 5. 统计与限制

- 条件之间**不共享 RNG 流**（不同动作改变 Poisson 事件数，第一个 tick 后就分叉），
  因此按 seed 配对无效；本报告使用两组标签置换检验（20,000 次），n = 15/组。
- 120 s 版本每 seed 只有 ~12 个 rally；600 s 版本（v0.9.0）约 60 个，
  frozen-paddle 的 hit 收敛到 0.138/0.152（理论 1/7），行为噪声地板降到 ~0.02。
  **行为结论以 600 s 版本为准**；120 s 的结果用于机制筛查。
- 未做多重比较校正；探索性 p 值需谨慎。
- 没有背景噪声：rest 期细胞完全沉默，这与真实培养物的自发活动不符，也是稳态饱和的直接诱因。
- Tier 1 增益敏感性（0.30/0.60）与恒常率实验（20/20 Hz）均为负/不确定结果；
  未测试“保末端增益的早期增强”（如 20–40 Hz）、更慢球或更长回合。
- 2 细胞、无抑制性中间神经元；“最小涌现”问题只回答了读出层面，行为层面尚未回答。

