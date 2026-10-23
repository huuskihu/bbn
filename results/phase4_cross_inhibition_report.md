# Phase 4 交叉抑制 4 细胞版（v0.11.0）结果

- 日期：2026-10-22
- 预注册：`HANDOFF.md` §6I；参数变更记录：`docs/parameter_policy.md`
- 架构：2 个 motor 池（up/down，push-pull）+ I_up + I_down
  - up spike → I_up（兴奋性，40 nS/spike，τ=5 ms）
  - down spike → I_down（同样）
  - I_up spike → down 池抑制（10 nS/spike，E_inh=−80 mV，τ=10 ms）
  - I_down spike → up 池抑制
  - I 细胞不接收感觉输入；10 ms 环路延迟
- 7 条件 × 15 seeds × 600 s；trace 10× 降采样
- 对照：2-cell `results/phase4_600/`；shared-inhibition `results/phase4_inhibition_600/`
- 统计：两组标签置换检验（20,000 次）；跨臂只做描述性比较

---

## 1. 回退验证

关闭所有抑制时，`phase4_pushpull_static` seed 0 / 120 s 的共享 trace 列与 v0.9.0 **逐位一致**；
v0.10.0 shared 模式也保持不变。交叉模式只在 `cross_inhibition_enabled=True` 时生效。

---

## 2. 校准（只看率）

1 seed × 60 s，`pushpull_static`，\(g_{rec}=40\) nS：

| \(g_{inh}\) (nS) | motor 率 (Hz) | I 合计率 (Hz) | exclusive | both spike |
|---:|---:|---:|---:|---:|
| 5 | 17.5 | 7.0 | 0.0297 | 0.1463 |
| **10（选中）** | **17.3** | **6.6** | **0.0268** | **0.1455** |
| 20 | 17.2 | 7.0 | 0.0298 | 0.1410 |

全部落在 5–40 Hz；选中间值 **10 nS** 并冻结。

---

## 3. 行为结果（三臂对照）

| condition | 2-cell rally | shared rally | **cross rally** | cross hit |
|---|---:|---:|---:|---:|
| pushpull_static | 0.204 | 0.222 | **0.194 ± 0.070** | 0.162 |
| pushpull_3b_no_hs | 0.178 | 0.161 | 0.146 ± 0.037 | 0.130 |
| pushpull_3b_play_hs | 0.165 | 0.161 | 0.163 ± 0.077 | 0.140 |
| pushpull_3b | 0.151 | 0.163 | 0.170 ± 0.074 | 0.144 |
| random_3b | 0.168 | 0.149 | 0.188 ± 0.063 | 0.155 |
| random_paddle | 0.125 | 0.107 | 0.123 ± 0.077 | 0.106 |
| symmetric_static | 0.162 | 0.162 | 0.162 ± 0.045 | 0.138 |

cross 臂内两组置换检验：

| contrast | mean diff | p |
|---|---:|---:|
| static − random_paddle | +0.070 | 0.0141 |
| static − symmetric_static | +0.031 | 0.1520 |
| no_hs − static | **−0.048** | **0.0199** |
| play_hs − static | −0.031 | 0.2596 |
| 3b − static | −0.023 | 0.3869 |
| random_3b − random_paddle | +0.065 | 0.0194 |

- 4-cell static 0.194 低于 2-cell 0.204 与 shared 0.222；跨臂描述性，未达显著。
- **结构优势在 cross 臂内不再显著**：static − symmetric +0.031（p=0.152）；
  这与 2-cell（+0.042，p=0.016）和 shared（+0.059，p=0.0025）形成对比。
- no_hs 显著低于 static（−0.048，p=0.020）；3b/play_hs 方向也更低，但未达显著。
- random_3b 的 rally 偏高（0.188），但其 impact corr = −0.041，没有位置映射；
  这是随机策略的采样效应，不是学习。

---

## 4. Motif 机制（H1 的核心）

| condition | I_up spikes | I_down spikes | I_up−I_down | exclusive | both spike | I rate (Hz) |
|---|---:|---:|---:|---:|---:|---:|
| pushpull_static | 3721 | 3712 | **+9 (0.25%)** | 0.0221 | 0.146 | 6.6 |
| symmetric_static | 3688 | 3688 | 0 | 0.000 | 0.156 | 6.5 |
| 3b | 4717 | 4716 | +1 (0.02%) | 0.001 | 0.184 | 13.2 |
| no_hs | 3030 | 3035 | −5 (0.18%) | 0.014 | 0.125 | 2.2 |
| play_hs | 4681 | 4684 | −3 (0.06%) | 0.003 | 0.181 | 12.9 |
| random_3b | 4738 | 4738 | 0 | 0.000 | 0.185 | 13.3 |
| random_paddle | 3704 | 3720 | −16 (0.43%) | 0.015 | 0.148 | 6.6 |

**关键**：两个 I 细胞的 spike 数几乎完全相同（差异 <0.5%），即使 motor 池的
*y 调谐* 是相反的。原因是 I_up/I_down 只读取各自 motor 池的**总发放率**，
而 push-pull 设计下两池的总率本来就相近（static: 17.13 vs 17.11 Hz）。
交叉抑制因此被平衡抵消，不能放大两池的差异。

- **H1 不支持**：exclusive 0.0221，与 2-cell 0.0217、shared 0.0220 相同；
  both-spike 0.146（2-cell 0.150，shared 0.142）。没有 motor 分化。
- **H2 弱/不支持**：4-cell static 0.194 略低于 2-cell 0.204；cross 臂内
  static−symmetric 不显著（p=0.152）。
- **H3 部分支持**：no_hs 显著更差（−0.048，p=0.020）；3b/play_hs 方向更差但不显著。
  可塑性仍无收益。
- **H4 支持**：3b 的 `w_diff corr=0.000`，`at w_max` 0.467，impact corr 0.170；
  no_hs 权重均值 0.359、梯度相关 0.777。

---

## 5. 结论

1. **速率层面的交叉抑制对这个 push-pull 网络是“盲”的**：两个 I 细胞只看到各自池的
   总率，而两池总率相近，因此 I_up/I_down 几乎等量放电，交叉抑制变成平衡的 common-mode，
   没有 winner-take-all。
2. **行为上没有收益，甚至削弱了结构优势**：cross static 0.194 < 2-cell 0.204 < shared 0.222；
   cross 臂内 static−symmetric 不显著。
3. **可塑性仍无收益**：no_hs 显著更低；3b/play_hs 方向相同。
4. **下一步若继续**，需要让抑制环路读取**差分/位置特异性**，而不是池总率：
   - I 细胞接收与 motor 池相同的 8 通道感觉输入，并按 push-pull 权重调谐；
   - 或 motor 池之间直接相互抑制（各自读对方的 rate，而非经过一个共同 I）；
   - 或使用不同细胞类型/时间尺度（FS 中间神经元、抑制性 STP）。
   这些都需要新的预注册版本；不再调 \(g_{rec}/g_{inh}\) 或加更多同质 I 细胞。

---

## 6. 限制

- I 细胞纯递归驱动、静态权重；g_rec=40 nS、g_inh=10 nS 为预注册校准值。
- 10 ms 环路延迟；未测试更短延迟或抑制性可塑性。
- 跨臂比较不是同一 RNG 流；symmetric 因动作恒 0 可精确复现（0.1622），其余为描述性。
- 每条件 15 seeds × 600 s；p 值未做多重比较校正。
