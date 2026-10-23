# Phase 4 归一化读出（v0.14.0）结果

- 日期：2026-10-22
- 预注册：`HANDOFF.md` §6L；参数变更记录：`docs/parameter_policy.md`
- 唯一改动：读出 `v = k_norm·(up−down)/(up+down+ε)`，`k_norm=5.0` bins/s，`ε=1e-3` Hz
- 其余全部冻结：2 细胞 push-pull、`ball_speed=0.5`、感觉率 4–40 Hz、
  7 条件 × 15 seeds × 600 s、可塑性/稳态参数
- 对照：v0.9.0 2-cell 600 s（`results/phase4_600/`，difference readout）
- 统计：两组标签置换检验；跨臂描述性

---

## 1. 行为结果（difference vs normalized）

| condition | diff rally (v0.9) | norm rally | diff hit | norm hit |
|---|---:|---:|---:|---:|
| pushpull_static | 0.204 | **0.202 ± 0.080** | 0.169 | **0.167** |
| pushpull_3b_no_hs | 0.178 | 0.181 ± 0.051 | 0.150 | 0.151 |
| pushpull_3b_play_hs | 0.165 | 0.134 ± 0.071 | 0.147 | 0.134 |
| pushpull_3b | 0.151 | 0.173 ± 0.078 | 0.129 | 0.144 |
| random_3b | 0.168 | 0.159 ± 0.039 | 0.142 | 0.142 |
| random_paddle | 0.125 | 0.128 ± 0.065 | 0.109 | 0.109 |
| symmetric_static | 0.162 | 0.162 ± 0.045 | 0.138 | 0.138 |

norm 臂内：

| contrast | mean diff | p |
|---|---:|---:|
| static − random_paddle | +0.074 | 0.0083 |
| static − symmetric_static | +0.040 | 0.0990 |
| no_hs − static | −0.021 | 0.4034 |
| play_hs − static | −0.068 | 0.0179 |
| 3b − static | −0.029 | 0.3276 |
| random_3b − random_paddle | +0.031 | 0.1276 |

- **H1 不支持**：static hit 0.169→0.167，rally 0.204→0.202；归一化没有改善行为。
- **H2 部分支持**：static − random +0.074（p=0.008）；static − symmetric +0.040（p=0.099，不显著）；
  symmetric 仍为冻结球拍（0.162，hit 0.138≈1/7）。
- **H3 部分支持**：no_hs ≈ static（−0.021，p=0.40）；3b −0.029（p=0.33）；
  play_hs 显著更差（−0.068，p=0.018）。可塑性仍无收益。
- **H4 支持**：3b `w_diff=0`，`at w_max` 0.333；no_hs 权重 0.367、梯度相关 0.865。

---

## 2. 有效增益与读出信息

| condition | K_eff diff (v0.9) | K_eff norm | T1→T2 hit (norm) |
|---|---:|---:|---:|
| pushpull_static | 0.141 | **0.177** | 0.180 → 0.154 |
| pushpull_3b_no_hs | 0.120 | — | — |
| pushpull_3b | 0.017 | — | — |

- 归一化把 K_eff 提高了约 26%（0.141→0.177），但 hit/rally 完全没变。
  这与 v0.7.1 的增益敏感性结论一致：**闭环增益本身不是限制因素**。
- 归一化信号的相关：play 0.678、early（ball_x>0.5）0.652、late 0.887；
  与旧差分信号的 early/late 相关（0.659/0.862）几乎相同。
  归一化改变了幅度映射，但没有增加信息量。
- T1→T2 0.180→0.154，无正向学习趋势。

---

## 3. 预注册假设判定

| 假设 | 判定 |
|---|---|
| H1：归一化提高早期相关/K，static hit/rally 高于 v0.9 | **不支持**：K +26%，但 hit 0.169→0.167、rally 0.204→0.202；early corr 0.652 ≈ 旧 0.659 |
| H2：结构优势保持/扩大；symmetric ≈1/7 | **部分支持**：static−random p=0.008；static−symmetric p=0.099；symmetric hit 0.138≈1/7 |
| H3：可塑性仍无收益 | **部分支持**：no_hs/3b 与 static 无显著差异；play_hs 显著更差（p=0.018） |
| H4：稳态饱和仍存在 | **支持**：3b w_diff=0，at w_max 0.333 |

---

## 4. 结论

1. **归一化不是修复**：K_eff 提高 26%，但命中率/ rally 不变；读出增益与信息量都不是限制因素。
2. **结构优势仍在**：static 仍显著优于随机球拍（p=0.008），但与 symmetric 的差异不显著（p=0.099）。
3. **可塑性仍无收益**：no_hs/3b 无改善，play_hs 更差。
4. **按预注册停止规则，读出这条线到此为止**。剩余唯一未做的 Tier 1 机制是背景噪声；
   若也不改善，项目应停在当前结论并整理最终报告。

---

## 5. 限制

- 跨臂（diff vs norm）不是同一 RNG 流；描述性比较。
- k_norm=5.0 为预注册推导值，未做行为调参。
- 未测试“归一化 + 放慢球”的组合；两者都单独失败，组合的先验也很低。
- 未加入背景噪声或抑制网络（2 细胞版）。
