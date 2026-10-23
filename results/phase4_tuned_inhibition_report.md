# Phase 4 差分调谐抑制 4 细胞版（v0.12.0）结果

- 日期：2026-10-22
- 预注册：`HANDOFF.md` §6J；参数变更记录：`docs/parameter_policy.md`
- 架构：2 motor 池 + I_up/I_down；I 细胞只接收 8 通道感觉事件，
  权重为 push-pull 调谐（I_up: 1+0.2x，I_down: 1−0.2x），
  I_up→down、I_down→up 同 tick 交叉抑制；\(g_{inh}=10\) nS，\(E_{inh}=-80\) mV，\(\tau=10\) ms
- 7 条件 × 15 seeds × 600 s；trace 10× 降采样
- 对照：2-cell `results/phase4_600/`、shared `results/phase4_inhibition_600/`、cross `results/phase4_cross_inhibition_600/`
- 统计：两组标签置换检验；跨臂描述性

---

## 1. 校准

1 seed × 60 s，`pushpull_static`：

| \(g_{inh}\) (nS) | motor 率 (Hz) | I 合计率 (Hz) | exclusive | corr(I_up−I_down, y) |
|---:|---:|---:|---:|---:|
| 5 | 17.3 | 18.4 | 0.0230 | +0.210 |
| **10（选中）** | **17.0** | **19.0** | **0.0303** | **+0.194** |
| 20 | 16.6 | 19.4 | 0.0313 | +0.217 |

按规则选 10 nS 并冻结。

---

## 2. 行为结果（四臂对照）

| condition | 2-cell | shared | cross | **tuned** | tuned hit |
|---|---:|---:|---:|---:|---:|
| pushpull_static | 0.204 | 0.222 | 0.194 | **0.228 ± 0.064** | 0.185 |
| pushpull_3b_no_hs | 0.178 | 0.161 | 0.146 | 0.173 ± 0.061 | 0.151 |
| pushpull_3b_play_hs | 0.165 | 0.161 | 0.163 | 0.193 ± 0.058 | 0.166 |
| pushpull_3b | 0.151 | 0.163 | 0.170 | 0.172 ± 0.053 | 0.146 |
| random_3b | 0.168 | 0.149 | 0.188 | 0.173 ± 0.058 | 0.147 |
| random_paddle | 0.125 | 0.107 | 0.123 | 0.095 ± 0.047 | 0.086 |
| symmetric_static | 0.162 | 0.162 | 0.162 | **0.180 ± 0.052** | 0.152 |

tuned 臂内：

| contrast | mean diff | p |
|---|---:|---:|
| static − random_paddle | +0.133 | <0.0001 |
| static − symmetric_static | +0.048 | 0.0330 |
| no_hs − static | −0.055 | 0.0236 |
| play_hs − static | −0.035 | 0.1256 |
| 3b − static | **−0.057** | **0.0119** |
| random_3b − random_paddle | +0.078 | 0.0003 |

- tuned static 0.228 是四臂中最高，但只比 2-cell 0.204 高 ~0.024（跨臂描述性）；
  比 shared 0.222 高 ~0.006。绝对增益很小。
- **重要：symmetric 不再是冻结球拍对照**。I_up/I_down 按 push-pull 调谐，
  即使 motor 权重相同，也会注入差分抑制：`mean_abs_rate_diff = 0.46`，
  exclusive = 0.007，symmetric 的 rally 从 0.162 升到 0.180。
  因此 tuned 臂内 static−symmetric（p=0.033）**不能**当作干净的结构读出证据；
  它是“motor 权重对称 + 调谐抑制不对称”的混合对照。

---

## 3. I 细胞的差分信号（H1 核心）

| condition | I_up spikes | I_down spikes | 差异 | corr(I_up−I_down, y) | corr(I_up, I_down) | exclusive | both |
|---|---:|---:|---:|---:|---:|---:|---:|
| pushpull_static | 3127 | 3140 | −0.4% | **+0.196** | +0.761 | 0.0236 | 0.147 |
| pushpull_3b_no_hs | 2984 | 2994 | −0.3% | +0.199 | +0.760 | 0.0144 | 0.128 |
| pushpull_3b_play_hs | 3032 | 3040 | −0.3% | +0.196 | +0.757 | 0.0081 | 0.184 |
| pushpull_3b | 2994 | 3023 | −1.0% | +0.195 | +0.757 | 0.0064 | 0.186 |
| random_3b | 2989 | 2976 | +0.4% | +0.197 | +0.756 | 0.0061 | 0.187 |
| random_paddle | 2857 | 2832 | +0.9% | +0.195 | +0.760 | 0.0150 | 0.151 |
| symmetric_static | 3010 | 2993 | +0.6% | +0.198 | +0.756 | 0.0070 | 0.154 |

- **H1 不支持（按预注册的每 tick 计数）**：`corr(I_up−I_down, y) ≈ 0.196 < 0.5`；
  I_up/I_down 总 spike 数差异 <1%；exclusive 0.0236，仅比 2-cell 0.0217 高 0.002，
  远未达到 winner-take-all。
- 机制：±26% 的 push-pull 权重差在单细胞率上是压缩的；两 I 细胞的共同感觉驱动
  （18–19 Hz）远大于差分分量，且每 tick 计数只有 0–1 个 spike，量化噪声大。
  因此交叉抑制仍然近似平衡。
- （探索性）如果用 300 ms 窗口率而不是每 tick 计数，相关可能更高；本报告不把它
  作为 H1 的替代判定，避免看完结果后移动阈值。

---

## 4. 可塑性与稳态

- no_hs：0.173，比 static 低 0.055（p=0.024）；权重均值 0.444，梯度相关 0.704。
- 3b：0.172，比 static 低 0.057（p=0.012）；`w_diff corr = 0.036`（接近 0），
  `at w_max` 0.20，impact corr 0.350。
- play_hs：0.193，−0.035（p=0.126）。
- **H3 支持**：可塑性仍无收益，no_hs/3b 显著更差。
- **H4 支持（部分）**：3b 的差分结构仍被稳态基本抹平（w_diff≈0.036），
  但本次 at w_max 只有 0.20，饱和程度低于 v0.11.0。

---

## 5. 预注册假设判定

| 假设 | 判定 |
|---|---|
| H1：corr(I_up−I_down, y) > 0.5；exclusive 高于其他臂 | **不支持**：r≈0.196；exclusive 0.0236 vs 0.0217–0.0221；I_up/I_down 差异 <1% |
| H2：tuned static 不差于 2-cell static；可能略升 | **弱支持**：0.228 vs 0.204（+0.024，跨臂描述性）；但 symmetric 对照已被污染，不能作强解释 |
| H3：可塑性仍无收益 | **支持**：no_hs −0.055（p=0.024）、3b −0.057（p=0.012） |
| H4：稳态饱和仍存在 | **支持（部分）**：3b w_diff≈0.036，at w_max 0.20 |

---

## 6. 结论

1. **差分调谐的强度不足**：±26% 的 push-pull 权重差只产生 <1% 的 I_up/I_down 总率差，
   每 tick 计数差与 ball_y 的相关仅 ~0.20。交叉抑制仍近似平衡，没有 winner-take-all。
2. **行为有微弱正向信号但不显著**：tuned static 0.228 为四臂最高，仅比 2-cell 高 0.024；
   由于 symmetric 对照被调谐抑制污染，不能把 static−symmetric 的 p=0.033 当作结构证据。
3. **可塑性仍有害**：no_hs 与 3b 都显著低于 static。
4. **按预注册停止规则，抑制网络这条线到此为止**：不再调 \(g_{inh}\)/gain、不再加同质 I 细胞。
   若继续，应转向背景噪声（rest 期沉默/稳态饱和）或任务时间尺度（放慢球/更长回合），
   或让 motor 池之间直接按**差分信号**相互抑制（需要新的预注册与更强的差分增益）。

---

## 7. 限制

- `symmetric_static` 在 v0.12.0 不再是冻结球拍对照（调谐 I 注入差分），
  这是本版本的设计缺陷；v0.9–v0.11 的 symmetric 仍是干净的零。
- I 细胞权重固定、无稳态；纯感觉驱动、无反馈。
- 每条件 15 seeds × 600 s；同臂 p 值未做多重比较校正。
- 未测试窗口率差分、抑制性可塑性或更强的 push-pull 增益。
