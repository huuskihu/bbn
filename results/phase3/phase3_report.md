# Phase 3: Single-cell closed-loop learning

- Config: `config\phase3.yaml`
- Duration: 120.0 s; seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
- Conditions: ['phase3a_full', 'phase3a_full_no_hs', 'phase3b_full', 'phase3b_full_no_hs', 'phase3b_no_feedback', 'phase3b_silent', 'phase3b_shuffled', 'static_full', 'random_paddle', 'always_up', 'always_down']

## Behavior + weights

| condition | avg rally | hits | misses | mean rate | w init | w final | |Δw| | y corr init→final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| always_down | 0.079 ± 0.037 | 4.3 | 55.7 | 21.5 | 1.002 | 1.002 | 0.0000 | -0.038 → -0.038 |
| always_up | 0.069 ± 0.025 | 3.9 | 56.1 | 21.5 | 1.002 | 1.002 | 0.0000 | -0.038 → -0.038 |
| phase3a_full | 0.089 ± 0.102 | 1.1 | 12.0 | 21.5 | 1.002 | 1.465 | 0.4621 | -0.038 → -0.018 |
| phase3a_full_no_hs | 0.094 ± 0.113 | 1.1 | 12.0 | 20.3 | 1.002 | 1.416 | 0.4138 | -0.038 → +0.074 |
| phase3b_full | 0.089 ± 0.102 | 1.1 | 12.0 | 21.3 | 1.002 | 1.444 | 0.4419 | -0.038 → +0.083 |
| phase3b_full_no_hs | 0.167 ± 0.130 | 2.0 | 12.0 | 17.3 | 1.002 | 0.766 | 0.2412 | -0.038 → -0.343 |
| phase3b_no_feedback | 0.171 ± 0.061 | 8.7 | 51.3 | 18.1 | 1.002 | 0.875 | 0.1289 | -0.038 → -0.038 |
| phase3b_shuffled | 0.179 ± 0.072 | 8.7 | 49.7 | 18.5 | 1.002 | 0.886 | 0.1259 | -0.038 → -0.065 |
| phase3b_silent | 0.050 ± 0.042 | 1.0 | 20.0 | 13.6 | 1.002 | 1.486 | 0.4840 | -0.038 → +0.000 |
| random_paddle | 0.161 ± 0.076 | 8.2 | 51.8 | 21.7 | 1.002 | 1.002 | 0.0000 | -0.038 → -0.038 |
| static_full | 0.178 ± 0.104 | 2.1 | 12.0 | 18.0 | 1.002 | 1.002 | 0.0000 | -0.038 → -0.038 |

## Interpretation

- 3a = 字面 DishBrain（STDP + 稳态，反馈只作刺激）；3b = 资格迹 + 三因子。
- 协议：rest 期间暂停整局（球与球拍一起冻结），修复了旧实现中“球继续前进 → 永久 rest”的 bug。
  带 timeout 的条件每 120 s 只有 ~12–13 个 rally；不带 timeout 的 no_feedback / shuffled /
  always_up / always_down 有 ~60 个 rally。跨条件比较 rally 时必须注意这个采样差异。
- `phase3a_full` / `phase3b_full`：稳态把权重推到 w_max 附近（1.44–1.47），通道-权重相关接近 0，
  rally 0.089，比 static_full 的 0.178 更差。机制与 Phase 4 相同：rest 期细胞沉默 →
  1 s 一次的稳态缩放按 20 Hz 目标上调约 1.16×/s → 权重饱和。
- `phase3b_full_no_hs`：STDP 造成 |Δw| = 0.24，但最终通道-权重相关为 −0.343（方向错误：
  高 y 通道被削弱），rally 0.167，与 static 0.178 / random_paddle 0.161 无差异。
- `phase3b_no_feedback`（0.171）与 `phase3b_shuffled`（0.179）有 ~60 个 rally，
  与 random_paddle 同量级，说明反馈刺激本身没有提供方向性。
- `phase3b_silent`：权重饱和到 1.486，rally 0.050。
- **结论：没有学习效应。** 单细胞标量率不携带可用的 ball_y 信息（Phase 1 诊断 R² = 0.007，
  斜率 −0.22 Hz/bin）；三因子规则在单一标量 D(t) 下无法给不同通道分配信用；
  稳态在对局/休息切换中反而主导了权重变化。负结果成立，不通过调参美化。

