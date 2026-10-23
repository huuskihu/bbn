# 参数政策：固定参数、校准参数与可塑状态变量

> 本文回答一个核心质疑：**“如果参数不可调整，那可塑性/学习能力从哪里来？”**
> 结论：学习不来自“所有参数都能变”，而来自一组**有生理对应物的状态变量**按局部规则更新。固定的是细胞身份，变化的是细胞经验。

---

## 1. 问题的来源

上一版方案里有一句话：“基础电生理参数来自论文，不在游戏上训练；只有可塑性变量随活动变化。”这句话容易被理解成“细胞是死的，什么都不能变”。不是这个意思。

真实神经元在分钟到小时尺度上：

- **不会**改写 Na⁺ 通道的门控方程、膜电容、反转电位；
- **会**改变突触权重、通道密度、受体数量、通道的电压依赖性、胞内信号状态。

如果让所有参数自由变化去拟合 Pong 成绩，那就变成了机器学习，细胞也不再是“皮层 RS 神经元”。所以必须把“身份”和“经验”分开。

---

## 2. 一句话答案

**学习 = 输入-输出映射的变化；映射由可塑状态变量（突触权重、通道密度、受体池、资格迹）承载；这些变量由局部生物规则更新，而不是由全局误差反向传播更新。**

---

## 3. 四层参数结构

| 层级 | 名称 | 是否变化 | 例子 | 谁决定 |
|---|---|---|---|---|
| **Tier 0** | 身份参数 | **固定** | \(C_m\)、门控方程、\(E_{Na/K/Ca}\)、基础 \(g_{\max}^0\)、形态 | 文献/ModelDB，阶段 0 写入后锁定 |
| **Tier 1** | 接口/校准参数 | **校准一次后冻结** | 感觉突触电导、反馈增益、噪声、读出增益、目标放电率 | 阶段 0/1 校准；所有条件共用 |
| **Tier 2** | 可塑状态变量 | **随活动变化** | \(w_{ij}\)、\(e_{ij}\)、\(s_i\)（gmax 缩放）、\(\delta_i\)（V1/2 偏移）、受体池 \(S/I\) | 局部可塑性规则 |
| **Tier 3** | 实验变量 | 由实验设计决定 | 反馈条件、种子、会话长度、T1/T2 | 预注册的实验方案 |

### 3.1 关键实现方式：基线 × 可塑缩放

为了避免“到底哪个 gmax 在变”的歧义，通道电导写成：

\[
g_i(t) = g_i^0 \cdot s_i(t), \qquad s_i \in [s_{\min}, s_{\max}]
\]

- \(g_i^0\)：Tier 0 的基线最大电导，固定；
- \(s_i\)：Tier 2 的活动依赖缩放因子，可塑，有上下限。

半激活电压写成：

\[
V_{1/2,i}(t) = V_{1/2,i}^0 + \delta_i(t), \qquad \delta_i \in [-\delta_{\max}, +\delta_{\max}]
\]

这样既保留“这是一只 Pospischil RS 细胞”的身份，又允许它通过通道密度/电压依赖性发生经验依赖的变化。

---

## 4. 可塑状态变量与更新规则

### 4.1 突触权重 \(w_{ij}\)：STDP + 资格迹 + 三因子调制

**双相 STDP（局部、毫秒级）**

\[
\Delta w =
\begin{cases}
A_+ \exp(-\Delta t/\tau_+), & \Delta t > 0 \quad (\text{pre before post}) \\
-A_- \exp(\Delta t/\tau_-), & \Delta t < 0 \quad (\text{post before pre})
\end{cases}
\]

- 生理对应：NMDAR 作为 coincidence detector；Ca²⁺ 内流幅度/时序决定 LTP vs LTD。
- 文献：Markram et al. 1997；Song, Miller & Abbott 2000；Andrade-Talavera et al. 2023。
- 边界：\(w_{ij} \in [0, w_{\max}]\)。

**资格迹（把毫秒事件记到秒级）**

\[
\tau_e \frac{de_{ij}}{dt} = -e_{ij} + \eta_{\text{STDP}} \cdot \text{STDP event}_{ij}(t)
\]

- 生理对应：Ca²⁺/CaMKII 等局部“记忆痕迹”，使延迟反馈仍能作用到正确的突触。
- 文献：Izhikevich 2007；Frémaux & Gerstner 2016。

**三因子调制（把“可预测/不可预测”变成全局信号）**

\[
\Delta w_{ij} = \eta \, D(t) \, e_{ij}
\]

- \(D(t)\)：全局神经调质样信号。可预测反馈 → \(D>0\)；不可预测反馈 → \(D<0\)；静默 → \(D\approx 0\) 或弱负；无反馈 → \(D=0\)。
- 生理对应：多巴胺/血清素/胶质递质等对可塑性的门控；星形胶质细胞参与突触与非突触可塑性。
- 文献：Izhikevich 2007；Sanz-Gálvez et al. 2024。
- **注意**：这是本项目对 DishBrain“可预测=奖励、不可预测=惩罚”的最小化解释，不是全局反向传播。

### 4.2 稳态突触缩放：把平均放电率拉回目标

\[
\frac{dw_{ij}}{dt} = \eta_w \, (r_{\text{target}} - \bar r) \, w_{ij}
\]

或离散形式：

\[
w_{ij} \leftarrow w_{ij} \cdot \left(\frac{r_{\text{target}}}{\bar r}\right)^{\alpha}
\]

- \(\bar r\)：滑动窗口平均放电率；\(r_{\text{target}}\)：目标放电率（默认 20 Hz，与 DishBrain 的 gain 一致）。
- 生理对应：Turrigiano 的突触缩放；Ca²⁺ 依赖传感器检测放电率，调控 AMPA 受体在突触部位的累积。
- 文献：Turrigiano 2012。
- 作用：防止 STDP 正反馈导致权重爆炸；它是**稳定器**，不是奖励信号。

### 4.3 内在可塑性：通道密度与电压依赖性

采用 O'Leary et al. 2014 的“活动依赖通道表达”框架的简化版：

\[
\frac{ds_i}{dt} = \varepsilon_i \, S(t) \, s_i, \qquad S(t) = \frac{[\mathrm{Ca}^{2+}]_{\text{target}} - [\mathrm{Ca}^{2+}]_{\text{sensor}}(t)}{[\mathrm{Ca}^{2+}]_{\text{target}}}
\]

- \(s_i\)：通道 \(i\) 的密度缩放因子；\(S(t)\)：活动误差信号。
- 可选：\(\delta_i\) 随活动缓慢偏移，改变 \(V_{1/2}\)。
- 生理对应：通道密度/定位/生物物理特性的活动依赖变化；内吞/外排；翻译后修饰。
- 文献：O'Leary et al. 2014；Remy, Beck & Yaari 2010；Tyagi et al. 2025；Haan et al. 2026。
- 边界：\(s_i \in [0.8, 1.2]\)，\(\delta_i \in [-5, +5]\) mV（初值，阶段 2 可调，但必须有依据）。

> 具体方程在阶段 2 对照 O'Leary 原文与 ModelDB 落地；上面的形式是“活动误差 → 通道密度”的通用骨架，不是最终定稿。

### 4.4 受体池：表面池 / 胞内池

\[
\frac{dS_{ij}}{dt} = k_{\text{exo}}(t) \, I_{ij} - k_{\text{end}}(t) \, S_{ij}, \qquad S_{ij} + I_{ij} = \text{const}
\]

- \(S_{ij}\)：膜上（有效）受体；\(I_{ij}\)：胞内池。
- \(k_{\text{exo}}, k_{\text{end}}\)：活动依赖的外排/内吞速率。
- 生理对应：AMPA 受体内吞/外排；SNARE 异构体、endophilin 等共享机制。
- 文献：Haan et al. 2026；Turrigiano 2012。
- 时间尺度：分钟级；主要作为慢稳态调节，不负责秒级“奖惩”。

### 4.5 短时程可塑性（可选，但有用）

\(u_{ij}, x_{ij}\)（突触易化/抑制）也是 Tier 2 状态变量。它们不改变“长期学习”，但会影响秒级放电模式，应记录并纳入消融。

---

## 5. 为什么这不是机器学习

| 机器学习做法 | 本项目做法 |
|---|---|
| 定义全局损失（如 cross-entropy） | 没有全局损失；只有局部可塑性规则 |
| 反向传播计算梯度 | 没有梯度；权重变化由前后脉冲时序、活动误差、调制信号决定 |
| 用优化器调所有参数 | Tier 0 固定；Tier 1 校准后冻结；只有 Tier 2 按规则变化 |
| 用验证集挑超参数 | 参数变化必须是预注册的实验变量，或有生理依据 |
| 目标是最大化 Pong 分数 | 目标是观察**有方向性的适应**，并如实报告 |

**判定标准**：如果某个参数变化不能用一句话解释成“因为某类活动/某个信号，按某条生物规则，变化了多少”，那它就不该出现在模型里。

---

## 6. 校准与冻结流程

### 6.1 什么需要校准

| 参数 | 为什么需要校准 | 校准目标 |
|---|---|---|
| 感觉输入突触电导 | 论文的 75 mV 是细胞外电压，单房室模型没有直接的细胞外场 | 使 4–40 Hz 编码驱动细胞产生 4–40 Hz 放电 |
| 反馈突触增益 | 100 Hz/100 ms 与 5 Hz/4 s 的有效驱动不同 | 可预测反馈能引起可测的短时放电增加；不可预测反馈能引起持续扰动 |
| 噪声水平 | 没有背景网络，需要人为背景噪声 | 自发放电率在合理范围（如 1–5 Hz），不完全静默 |
| 读出增益 | 把放电率映射到球拍速度 | 球拍速度范围合理，不因饱和卡死 |
| 目标放电率 | 稳态设定点 | 与 20 Hz 参考一致或按实验设计设定 |

### 6.2 校准规则

1. 校准只在阶段 0/1 进行；
2. 每次校准记录：参数名、初值、搜索范围、目标、最终值、依据、日期；
3. 校准完成后写入 `config/experiment_default.yaml`，计算 `config_hash`；
4. 阶段 3 开始后，Tier 1 不再变化；若必须变化，视为新版本，所有条件重跑。

### 6.3 什么不算校准

- 看完 Pong 成绩后回头调感觉增益、STDP 学习率、稳态时间常数，让它“看起来学会了”——这是调参，不是校准。
- 为了让某个 seed 好看而改边界——这是挑结果。

---

## 7. 参数总表（实现时填数值）

| 层级 | 参数 | 符号 | 初始/边界 | 更新规则 | 生理来源 |
|---|---|---|---|---|---|
| 0 | 膜电容 | \(C_m\) | 文献值 | 固定 | Pospischil 2008 |
| 0 | 通道门控 | \(m,h,n,\dots\) | 文献方程 | 固定 | Pospischil 2008 |
| 0 | 反转电位 | \(E_{Na},E_K,E_{Ca},E_L\) | 文献值 | 固定 | Pospischil 2008 |
| 0 | 基线最大电导 | \(g_i^0\) | 文献值 | 固定 | Pospischil 2008 |
| 0 | 抑制性突触反转电位 | \(E_{\text{inh}}\) | −80 mV | 固定 | GABA_A 典型反转电位（本模型新增的抑制性电导） |
| 1 | 感觉突触电导 | \(\bar g_{\text{sens}}\) | 待校准 | 冻结 | 实验接口 |
| 1 | 反馈增益 | \(k_{\text{fb}}\) | 待校准 | 冻结 | 实验接口 |
| 1 | 背景噪声 | \(\sigma_{\text{noise}}\) | 待校准 | 冻结 | 实验接口 |
| 1 | 读出增益 | \(k_{\text{motor}}\) | 待校准 | 冻结 | 实验接口 |
| 1 | 目标放电率 | \(r_{\text{target}}\) | 20 Hz | 冻结 | DishBrain gain |
| 1 | 抑制性突触权重 | \(\bar g_{\text{inh}}\) | 校准集 {5, 10, 20} nS | 校准后冻结 | 实验接口（3 细胞版新增） |
| 1 | 抑制性时间常数 | \(\tau_{\text{inh}}\) | 10 ms | 冻结 | GABA_A IPSC 衰减（~10 ms） |
| 2 | 突触权重 | \(w_{ij}\) | \([0,w_{\max}]\) | STDP + 三因子 | Markram 1997; Song 2000; Izhikevich 2007 |
| 2 | 资格迹 | \(e_{ij}\) | \([0,e_{\max}]\) | 指数衰减 + STDP 事件 | Izhikevich 2007 |
| 2 | 通道密度缩放 | \(s_i\) | \([0.8,1.2]\) | 活动误差驱动 | O'Leary 2014; Remy 2010 |
| 2 | 半激活偏移 | \(\delta_i\) | \([-5,5]\) mV | 活动依赖 | Remy 2010 |
| 2 | 受体表面池 | \(S_{ij}\) | 守恒 | 内吞/外排 | Haan 2026 |
| 2 | STP 变量 | \(u_{ij},x_{ij}\) | \([0,1]\) | 活动依赖 | 待阶段 2 定 |
| 3 | 条件/种子/时长 | — | 预注册 | — | 实验设计 |

> 表中的边界值是**初值**，阶段 2 可以依据文献调整；调整必须记录在变更日志，并说明生理依据。

---

## 8. 参数变更日志模板

每次修改 Tier 0/1/2 的参数，复制一行：

| 日期 | 参数 | 旧值 → 新值 | 层级 | 原因/依据 | 影响的条件 | 是否重跑 |
|---|---|---|---|---|---|---|
| 2026-10-21 | 示例：\(A_+\) | 0.01 → 0.005 | 2 | Song 2000 的经典窗口；降低 LTP 饱和度 | 全部 | 是 |
| 2026-10-21 | 感觉突触权重 `syn_weight_nS` | 初值 → 40 nS（jitter 0.4） | 1 | Phase 1 校准：使细胞在 4–40 Hz 编码下落在 0–40 Hz 放电区间 | Phase 1/3 | 是 |
| 2026-10-21 | 读出窗口 `readout_window_ms` | 150 → 300 ms | 1 | 单细胞放电稀疏，300 ms 降低率估计方差 | Phase 1/3 | 是 |
| 2026-10-21 | 率平滑 `rate_smoothing` | 无 → 0.2 | 1 | 抑制单细胞率的高频抖动，避免球拍抖动 | Phase 1/3 | 是 |
| 2026-10-21 | 球拍增益 `velocity_gain` | 0.15 bins/s/Hz；max 4 bins/s | 1 | 2 s 回合内可覆盖 1–8 bins | Phase 1/3 | 是 |
| 2026-10-21 | 可预测反馈权重 | 10 → 5 nS | 1 | 10 nS 使 full_feedback 平均率升至 60+ Hz、球拍饱和 | Phase 1/3 | 是 |
| 2026-10-21 | 不可预测反馈权重 | 150 → 60 nS | 1 | 150 nS 过度驱动细胞；60 nS 产生可测扰动但不等同于持续兴奋 | Phase 1/3 | 是 |
| 2026-10-21 | STDP 学习率 A+/A− | 0.01 / 0.012 | 2 | Phase 2 验证窗口：峰值 LTP/LTD 与理论一致；Song 2000 量级 | Phase 3 | 是 |
| 2026-10-21 | STDP 时间常数 τ+/τ− | 20 / 20 ms | 2 | Markram 1997 的经典窗口；Phase 2 扫描 −50…+50 ms | Phase 3 | 是 |
| 2026-10-21 | 资格迹 τ_e | 1000 ms | 2 | Phase 2 延迟奖励验证：0–5 s 内衰减可见；Izhikevich 2007 | Phase 3 | 是 |
| 2026-10-21 | 三因子 η | 验证用 1.0 | 2 | 仅用于让验证曲线可见；Phase 3 重新设定生物合理值 | Phase 3 | 是 |
| 2026-10-21 | 稳态目标/α/边界 | 20 Hz / 0.1 / [2,80] nS | 2 | Phase 2 收敛验证：高/低起始都收敛到 20 Hz | Phase 3 | 是 |
| 2026-10-21 | rest 协议（循环实现） | rest 期间球继续前进 → rest 期间暂停整局 | —（协议修复，不是参数） | 旧实现中球在休息期继续到达，每次 miss 重置 rest，导致永久休息态；Phase 1/3 结论被污染 | Phase 1/3/4 | 是（三个阶段的全部条件重跑） |
| 2026-10-21 | 两池初始权重（Phase 4） | 无 → \(w_{up}=1+0.2x,\ w_{down}=1-0.2x\)，\(x=(ch-4.5)/3.5\) | Tier 3（实验初始状态） | 预注册的 push-pull 结构：给差分读出先验方向，plasticity 必须相对 static 评估 | Phase 4 | — |
| 2026-10-21 | 球拍增益 `velocity_gain`（敏感性版本 v0.7.1） | 0.15 → 0.30 / 0.60 bins/s/Hz | 1 | 预注册的机制检验：判断行为上限是否由闭环增益决定；主结果 v0.7.0 保持冻结 | Phase 4 增益敏感性（7 条件 × 15 seeds × 120 s × 两个剂量点） | 是（仅写入 `results/phase4_gain030`、`results/phase4_gain060`，不覆盖主结果） |
| 2026-10-21 | 感觉率范围 `rate_min_hz/rate_max_hz`（v0.8.0） | 4 / 40 → 20 / 20 Hz（恒定） | 1 | 预注册的时间形状检验：去掉 ball_x 距离门控，让位置信息在回合早期就可用；主结果保持冻结 | Phase 4 恒常率（7 条件 × 15 seeds × 120 s） | 是（仅写入 `results/phase4_const_rate`，不覆盖主结果） |
| 2026-10-21 | 会话时长 `duration_s`（v0.9.0） | 120 → 600 s | 3 | 预注册的行为功效实验：120 s 只有 ~14 rallies/seed，frozen-paddle 对照漂移 ~0.11；延长会话以降低行为噪声 | Phase 4 长会话两臂（主协议 + 恒常率；7 条件 × 15 seeds）；trace 10× 降采样 | 是（写入 `results/phase4_600`、`results/phase4_const_rate_600`，不覆盖主结果） |
| 2026-10-21 | 新增抑制性突触与 3 细胞网络（v0.10.0） | 无 → `g_inh` 标量、\(E_{inh}=-80\) mV、\(\tau_{inh}=10\) ms；1 个抑制性中间神经元 | 0（反转电位）/1（权重、时间常数） | 预注册的 motor 分化实验；引擎默认 `g_inh=0`，关闭时不得改变现有 Phase 1/3/4 结果（需回归验证） | Phase 4 抑制版（7 条件 × 15 seeds × 600 s） | 是（新目录 `results/phase4_inhibition_600`；另做关闭抑制的回归对比） |
| 2026-10-22 | 交叉抑制 4 细胞（v0.11.0） | 新增 \(g_{rec}=40\) nS/spike、\(g_{inh}\in\{5,10,20\}\) nS、10 ms 环路延迟；2 个 I 细胞 | 1（两个突触权重；I 细胞身份仍为 Tier 0） | 预注册的 winner-take-all motif：I_up 抑制 down、I_down 抑制 up；关闭时与 v0.9.0 逐位一致 | Phase 4 交叉抑制（7 条件 × 15 seeds × 600 s） | 是（新目录 `results/phase4_cross_inhibition_600`） |
| 2026-10-22 | 差分调谐抑制 4 细胞（v0.12.0） | 新增 `tuned_inh_gain=1.0`、\(g_{inh}\in\{5,10,20\}\) nS；I 接收 8 通道感觉并按 push-pull 调谐 | 1（抑制权重/输入增益；I 身份仍为 Tier 0） | 预注册：让抑制环路读取位置差分，而不是池总率；关闭时与 v0.9.0 逐位一致 | Phase 4 差分调谐（7 条件 × 15 seeds × 600 s） | 是（新目录 `results/phase4_tuned_inhibition_600`） |
| 2026-10-22 | 球速 `ball_speed`（v0.13.0） | 0.5 → 0.25 bins/s（回合 2 s → 4 s） | 1 | 预注册的任务时间尺度检验：判断剩余行为上限是否由 2 s 窗口决定；主结果保持冻结 | Phase 4 放慢球（7 条件 × 15 seeds × 600 s，2 细胞） | 是（新目录 `results/phase4_slow_ball_600`） |
| 2026-10-22 | 归一化读出（v0.14.0） | 新增 `velocity_gain_norm=5.0` bins/s、`norm_eps_hz=1e-3`；v = k_norm·(up−down)/(up+down+ε) | 1 | 预注册：消除距离门控对差分幅度的影响；k_norm 由旧末端命令匹配推导（≈5.4，取 5.0） | Phase 4 归一化（7 条件 × 15 seeds × 600 s，2 细胞） | 是（新目录 `results/phase4_norm_readout_600`） |
| 2026-10-22 | 背景自发活动（v0.15.0） | 新增 `bg_noise_hz=3.0`、`bg_noise_weight_nS`（校准 {10,20,40,80} 到 1–5 Hz 自发率）；独立 RNG | 1 | 预注册：rest 期绝对静默导致稳态饱和；补 1–5 Hz 自发活动，检验梯度是否保持 | Phase 5 P0（4 条件 × 15 seeds × 600 s，2 细胞） | 是（新目录 `results/phase5_bg_noise_600`） |
| 2026-10-22 | 局部信用分配（v0.16.0） | D 从全局标量改为池特异：Miss 时按球侧 D_up/D_down = ±1；**由条件名（含 `local`）选择，无全局开关** | 1（调制规则；幅度沿用 ±1） | 预注册：全局 D 无法给 Up/Down 分配信用；局部符号相反，检验能否形成正确 y 梯度。首跑因全局开关污染对照臂（`3b` 也变 local），已改为条件驱动并重跑；污染批次存档 `results/phase5_local_credit_600_bug_globalflag/`，不参与推断 | Phase 5 P1（5 条件 × 15 seeds × 600 s） | 是（`results/phase5_local_credit_600`） |
| 2026-10-23 | 动态稳态目标带（v0.17.0） | 稳态目标由 20 Hz 点改为 `[5, 30] Hz` 带；带内不缩放；仅 play 期应用；α=0.05 不变 | 1（稳态目标语义；`use_band=False` 时与旧版逐位一致） | 预注册：固定点目标在 play 期（每池 ≈17 Hz）持续上调导致饱和；生理稳态维持功能范围而非精确点 | Phase 5 P2（5 条件 × 15 seeds × 600 s） | 是（`results/phase5_dynamic_homeostasis_600`）；结果：at w_max 0.34→0.14、impact corr 0.179→0.381，但全局 D 仍 0 梯度，local_dyn 行为 0.196 ≈ static 0.204（p=0.643）；H1 不支持，线停止 |
| 2026-10-23 | 短时程突触可塑性（v0.18.0） | 新增 TM 参数 `U=0.4`、`τ_rec=200 ms`、`τ_fac=1000 ms`；单事件电导乘 `(u·R)/U`；仅感觉事件 | 1（短时程状态，不改变 Tier 0；关闭时与 v0.17.0 逐位一致） | 预注册：2 细胞缺乏短时程动力学，无法把率斜坡转成时序敏感响应；按 TM 中值冻结，不搜索 | Phase 5 P3（5 条件 × 15 seeds × 600 s，`no_hs` 设置） | 是（`results/phase5_stp_600`）；结果：early 0.569→0.699、gap 0.171→0.118、impact 0.735→0.809、梯度 0.780→0.880，但命令减半，行为 0.187 < 0.220（p=0.243）；H2 不支持，线停止 |
| 2026-10-23 | 10 细胞 E/I 前馈网络（v0.19.0） | 新增 `net_se_weight_nS`、`net_em_weight_nS`、`net_sigma_bins=1.5`；4 S + 2 E + 2 I + 2 M | 1（S→E/I 与 E→M 电导按存活准则校准后冻结；Tier 0 不变） | 预注册：唯一未检验的维度是群体动力学；校准：g_S→E ∈{10,20,40} 取 E 率 10–25 Hz 的最小值（40），g_E→M 取 play motor 最接近 17.5 Hz 的网格点（40，14.1 Hz） | Phase 5 P4（5 条件 × 15 seeds × 600 s） | 是（`results/phase5_ten_cell_600`）；结果：网络存活（E/I 14.4 Hz、play motor 12.5 Hz）、net_static 0.203 ≈ 2 细胞 0.204（p=0.990），但 impact 0.920→0.479；net_local 0.127（p=0.005）、net_global 0.148；H3 不支持，线停止 |
| 2026-10-23 | PD 读出（v0.20.0） | 新增 `pd_tau_ms=50`（预注册单一值）；`v = Kp·Δr + Kp·τ_pred·dΔr/dt`；微分经 α 低通 | 1（读出接口；关闭时与 v0.19.0 逐位一致） | 预注册：检验微分前馈能否补偿环路延迟；明确它不能补偿 2 s 距离门控延迟；不搜索 τ_pred | Phase 5 P5（4 条件 × 15 seeds × 600 s） | 是（`results/phase5_pd_readout_600`）；结果：`local_pd` 0.220 ≡ `local_no_hs` 0.220（p=0.998）、`static_pd` 0.210 vs 0.204（p=0.722）；impact corr +0.01；H1/H2 不支持，线停止 |
| 2026-10-23 | 帧式延迟编码（v0.21.0） | 新增 `lat_frame_ms=100`、`lat_max_ms=100`、`lat_gain`（6a 校准）；8 通道每帧 1 事件，延迟 ∝ \|ch−y\|；首脉冲延迟差读出 | 1（输入编码+解码；`lat` 条件外与 v0.20.0 逐位一致） | 预注册：改信息到达方式而非接口增益；6a Gate `corr(Δt,y)>0.5` 且 5/5 符号一致；不调帧长/延迟上限 | Phase 6a（1 条件 × 5 seeds × 60 s，冻结球拍） | 是（`results/phase6a_latency`）；结果：corr 0.442（seed 0.320–0.798）、Δt P95 4.0 ms、率 20.8 Hz；Gate 不通过，A 线停止，未进入 6b |
| 2026-10-23 | 递归 E-I 网络（v0.22.0） | 新增 `rec_w_se_nS=20`、`rec_w_ei_nS=20`、`rec_g_ie_nS=10`、`rec_bg_hz=3`、`rec_bg_weight_nS=80`、`rec_w_em_nS=5`；待校准 `rec_w_ee_nS ∈ {0,5,10,20}`；4S+8E+8I+2M | 1（S→E、E→I、I→E、E→M 与背景按 §6T 固定；Tier 0 不变） | 预注册：用户明确要求覆盖 §6S 硬停止；7a Gate 要求 E 率 5–25 Hz、I>0、单细胞<60 Hz、CV>0.5、两两相关<0.8、漂移<30%；只允许按 E 率在 4 点网格中选 `w_ee`，不调其它参数 | Phase 7a（4 个 `w_ee` × 3 seeds × 60 s，静态权重） | 是（`results/phase7_7a`）；结果：E 率 3.67/4.07/158.0/253.2 Hz，网格内无 5–25 Hz 点；`w_ee=10` 同步化 0.90、漂移 30%；Gate 不通过，B 线永久关闭 |

> 以上 Tier 1 参数在 Phase 1 校准后冻结；Phase 3 开始后不再改。若必须改，视为新版本，所有条件重跑。

---

## 9. 如果固定细胞学不会怎么办

这是合法结果，不是失败。按顺序处理：

1. **先归因**：是感觉驱动不足？读出基准不对？信用分配缺失？稳态把学习压掉了？
2. **不要动 Tier 0**：不要为了成绩去改门控方程、电容、反转电位。
3. **可以做的**：
   - 换一个**预注册的**可塑性规则组合（STDP-only → STDP+稳态 → 三因子）；
   - 换一个**预注册的**细胞类型（RS → FS/IB）作为对照，而不是把 RS 调成别的细胞；
   - 进入网络阶段，看是否是单细胞容量不足；
   - 报告负结果，并给出机制解释。
4. **不可以做的**：网格搜索学习率/增益直到曲线好看；挑 seed；挑时间窗。

---

## 10. FAQ

**Q：参数固定，细胞岂不是永远输出一样？**  
A：不是。固定的是身份参数；膜电位、通道门控、适应电流、突触权重、资格迹、受体池都是动态状态。相同输入下，细胞的历史不同，输出就不同。

**Q：可塑性不就是调参数吗？**  
A：可塑性是**按规则**改变状态变量；调参是**按结果**改变模型常数。前者有生理对应，后者是拟合。

**Q：稳态缩放会不会把学习抹掉？**  
A：会压制过大的权重漂移，但不会抹掉输入特异性。它的时间常数（数十秒）比 STDP（数十毫秒）慢，二者形成快慢分离。阶段 3 会做“有/无稳态”的消融。

**Q：三因子规则算不算机器学习？**  
A：不算。它是局部资格迹 + 全局神经调质信号，没有反向传播、没有全局损失、没有梯度。它是生物可塑性的标准建模方式之一。

**Q：为什么不用 NEURON 的多房室模型？**  
A：单房室足以承载通道可塑性与闭环学习；多房室增加算力与调参面，但对 Pong 范式没有必要的增益。NEURON 可作为后续验证，不作为第一阶段。

**Q：为什么不用 Plastic Arbor？它已经内置同突触/稳态/异突触可塑性。**  
A：Plastic Arbor 的异突触优势依赖树突分支内的钙扩散，而本项目是单房室模型，没有树突空间可用。Brian 2 足以实现本项目需要的 STDP、资格迹、稳态缩放、内在可塑性和三因子调制，而且闭环控制与自定义规则更直接。Plastic Arbor 留作阶段 5 的形态扩展分支，不作为主平台。

---

## 11. 参考文献

- Markram, H., Lübke, J., Frotscher, M., & Sakmann, B. (1997). Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs. *Science*, 275, 213–215.
- Song, S., Miller, K. D., & Abbott, L. F. (2000). Competitive Hebbian learning through spike-timing-dependent synaptic plasticity. *Nature Neuroscience*, 3(9), 919–926.
- Turrigiano, G. (2012). Homeostatic synaptic plasticity: local and global mechanisms for stabilizing neuronal function. *Cold Spring Harbor Perspectives in Biology*, 4, a005736.
- Remy, S., Beck, H., & Yaari, Y. (2010). Plasticity of voltage-gated ion channels in pyramidal cell dendrites. *Current Opinion in Neurobiology*, 20, 503–509.
- O'Leary, T., Williams, A. H., Caplan, J. S., & Marder, E. (2014). Cell types, network homeostasis, and pathological compensation from a biologically plausible ion channel expression model. *Neuron*, 82(4), 809–821.
- Tyagi, S., Higerd-Rusli, G. P., Akin, E. J., Waxman, S. G., & Dib-Hajj, S. D. (2025). Sculpting excitable membranes: voltage-gated ion channel delivery and distribution. *Nature Reviews Neuroscience*, 26, 313–332.
- Haan, K. D., Gaudet, E., & Fisher, T. E. (2026). Common themes in evoked ion channel translocation in neuroplastic and homeostatic plasticity. *Frontiers in Pharmacology*, 17, 1727525.
- Izhikevich, E. M. (2007). Solving the distal reward problem through linkage of STDP and dopamine signaling. *Cerebral Cortex*, 17(10), 2443–2452.
- Sanz-Gálvez, R., Falardeau, D., Kolta, A., & Inglebert, Y. (2024). The role of astrocytes from synaptic to non-synaptic plasticity. *Frontiers in Cellular Neuroscience*, 18, 1477985.
- Andrade-Talavera, Y., Fisahn, A., & Rodríguez-Moreno, A. (2023). Timing to be precise? An overview of spike timing-dependent plasticity, brain rhythmicity, and glial cells interplay within neuronal circuits. *Molecular Psychiatry*, 28, 2177–2188.
- Pospischil, M., Toledo-Rodriguez, M., Monier, C., Piwkowska, Z., Bal, T., Frégnac, Y., Markram, H., & Destexhe, A. (2008). Minimal Hodgkin-Huxley type models for different classes of cortical and thalamic neurons. *Biological Cybernetics*, 99, 427–441. ModelDB 123623.
