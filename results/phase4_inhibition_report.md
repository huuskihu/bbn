# Phase 4 三细胞抑制版（v0.10.0）结果

- 日期：2026-10-22
- 预注册：`HANDOFF.md` §6H；参数变更记录：`docs/parameter_policy.md`
- 架构：2 个 motor 池（up/down，push-pull）+ 1 个抑制性中间神经元 I
- I 细胞：同一 Pospischil RS；接收与 motor 池相同的感觉事件（均匀权重 \(1.0\times40\) nS）
  与同一套反馈；权重静态；每个 spike 向两池各投递 10 nS 抑制电导
  （\(E_{inh}=-80\) mV，\(\tau_{inh}=10\) ms）
- 7 条件 × 15 seeds × 600 s；trace 10× 降采样
- 对照：v0.9.0 两细胞 `results/phase4_600/`（跨臂只做描述性比较，RNG 流不共享）
- 统计：两组标签置换检验（20,000 次）；条件之间不能按 seed 配对

---

## 1. 引擎与回退验证

`FastHH` 新增标量抑制电导 `g_inh`（默认 0）、`E_inh`、`tau_inh`。关闭抑制时：

- `phase4_pushpull_static` seed 0 / 120 s 的全部共享 trace 列与 v0.9.0 **逐位一致**；
- 新增列 `spikes_inh`、`inh_rate_used` 全为 0。

因此 v0.10.0 不改变任何既有 Phase 1/3/4 结果。

---

## 2. 校准（只看放电率）

1 seed × 60 s，`phase4_pushpull_static`：

| \(g_{inh}\) (nS) | motor 平均率 (Hz) | I 平均率 (Hz) | exclusive | both spike |
|---:|---:|---:|---:|---:|
| 5 | 17.4 | 18.6 | 0.0275 | 0.1465 |
| **10（选中）** | **16.5** | **18.6** | **0.0272** | **0.1428** |
| 20 | 14.4 | 18.6 | 0.0257 | 0.1267 |

全部落在 5–40 Hz，按预注册规则选中间值 **10 nS** 并冻结。

---

## 3. 行为结果

| condition | 3-cell rally | 2-cell rally | diff | 3-cell hit | 2-cell hit |
|---|---:|---:|---:|---:|---:|
| pushpull_static | **0.222 ± 0.051** | 0.204 ± 0.043 | +0.018 | **0.181** | 0.169 |
| pushpull_3b_no_hs | 0.161 ± 0.058 | 0.178 ± 0.045 | −0.017 | 0.150 | 0.150 |
| pushpull_3b_play_hs | 0.161 ± 0.074 | 0.165 ± 0.061 | −0.004 | 0.139 | 0.147 |
| pushpull_3b | 0.163 ± 0.076 | 0.151 ± 0.063 | +0.012 | 0.129 | 0.129 |
| random_3b | 0.149 ± 0.049 | 0.168 ± 0.048 | −0.019 | 0.129 | 0.142 |
| random_paddle | 0.107 ± 0.056 | 0.125 ± 0.055 | −0.018 | 0.096 | 0.109 |
| symmetric_static | 0.162 ± 0.045 | 0.162 ± 0.045 | 0.000 | 0.138 | 0.138 |

3-cell 同臂内两组置换检验：

| contrast | mean diff | p |
|---|---:|---:|
| static − random_paddle | +0.115 | <0.0001 |
| static − symmetric_static | **+0.059** | **0.0025** |
| no_hs − static | **−0.061** | **0.0060** |
| play_hs − static | **−0.061** | **0.0170** |
| 3b − static | **−0.059** | **0.0204** |
| random_3b − random_paddle | +0.043 | 0.0407 |

- 3-cell static 比 2-cell static 高 +0.018（跨臂描述性，未达显著）；抑制没有带来行为增益。
- symmetric 在 3-cell 与 2-cell 完全相同（0.1622），因为差分恒 0、动作不受抑制影响——
  这是干净的零对照。

---

## 4. 抑制与 motor 分化（H1 的核心）

| condition | I rate (Hz) | motor rate (Hz) | exclusive | both spike | corr(I, motor) |
|---|---:|---:|---:|---:|---:|
| pushpull_static | 18.8 | 16.4 | **0.022** | 0.142 | +0.985 |
| symmetric_static | 18.7 | 16.3 | 0.000 | 0.153 | +0.984 |
| 3b | 18.7 | 20.2 | 0.001 | 0.183 | +0.927 |
| no_hs | 18.7 | 13.9 | 0.013 | 0.124 | +0.633 |
| play_hs | 18.5 | 19.9 | 0.002 | 0.181 | +0.921 |
| random_3b | 18.7 | 20.2 | 0.000 | 0.184 | +0.930 |
| random_paddle | 18.4 | 16.3 | 0.015 | 0.145 | +0.979 |

- 2-cell 的 exclusive fraction 是 0.0217；3-cell static 是 0.0220——**没有变化**。
- 两池率相关仍为 0.970（2-cell 0.975）；both-spike 0.142（2-cell 0.150）。
- I 细胞与 motor 共同活动的相关高达 0.985：它只是跟踪共同驱动，没有产生选择。
- 共享前馈抑制把 motor 平均率从 17.8 降到 16.4 Hz（约 −8%），但两池仍一起放电。

**H1 不支持**：共享前馈抑制不足以产生排他放电/motor 分化。

---

## 5. 可塑性与稳态（H3/H4）

- 3b：rally 0.163，比 static 低 0.059（p=0.020）；`w_diff corr = 0.000`，
  `at w_max` 0.40，impact corr 只剩 0.177。
- no_hs：rally 0.161，比 static 低 0.061（p=0.006）；权重均值降到 0.445，
  梯度相关 0.835（仍保留方向但增益被削弱）。
- play_hs：0.161，比 static 低 0.061（p=0.017）。
- **H3 支持（可塑性仍无收益，且有害）**；**H4 支持（稳态饱和）**。

---

## 6. 预注册假设判定

| 假设 | 判定 |
|---|---|
| H1：抑制降低 both-spike、提高 exclusive | **不支持**：exclusive 0.022 vs 2-cell 0.0217；both-spike 0.142 vs 0.150；率相关 0.970 |
| H2：3-cell static 不差于 2-cell static | **弱支持**：0.222 vs 0.204（+0.018，跨臂描述性，未达显著） |
| H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static） | **支持且更强**：3b −0.059（p=0.020）、no_hs −0.061（p=0.006）、play_hs −0.061（p=0.017） |
| H4：稳态饱和仍存在 | **支持**：3b w_diff=0，40% 权重在 w_max，impact corr 0.177 |

---

## 7. 结论

1. **共享前馈抑制不产生 motor 分化**：它只提供共同抑制（common-mode），
   两池仍几乎完全共活动；exclusive fraction 与 2-cell 相同。
2. **行为上没有收益**：3-cell static 与 2-cell static 持平（+0.018，n.s.）；
   结构读出仍显著优于 symmetric（+0.059，p=0.0025）和 random（+0.115，p<0.0001）。
3. **可塑性仍有害**：三个可塑条件都显著低于 static；稳态继续把两池权重抹成相同。
4. **下一步（若继续）**：需要真正的交叉抑制（2 个 I 细胞：I_up 抑制 down、I_down 抑制 up）
   或 motor 池之间的递归竞争，才能形成 winner-take-all；这是新的预注册版本，
   不能通过继续调 \(g_{inh}\) 或加共享抑制来“凑”分化。

---

## 8. 限制

- 跨臂（2-cell vs 3-cell）不是同一 RNG 流；symmetric 因动作恒 0 可精确复现，
  其余条件只能做描述性比较。
- 抑制性中间神经元权重静态、无稳态；本版本只检验“共享前馈抑制”这一最小 motif。
- 每条件 15 seeds × 600 s，~60 rallies/seed；同臂 p 值未做多重比较校正。
- 未实现交叉抑制、抑制性可塑性或 I 细胞的背景噪声。
