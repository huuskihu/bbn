# DishBrain 协议与生物映射

> 本文把 Kagan et al. 2022（DishBrain）的实验协议翻译成可执行的单细胞/极小网络模型，并逐项标注生物对应物与简化假设。

---

## 1. 为什么选 DishBrain 作为范式

DishBrain 的核心不是“让神经元玩 Pong”，而是：

1. 用**低延迟闭环**把神经活动与外部环境耦合；
2. 用**可预测 / 不可预测刺激**作为“奖励 / 惩罚”的生物学等价物；
3. 不施加任何机器学习解码或权重更新，所有学习必须发生在生物网络内部。

这三条正好对应本项目的约束：闭环、局部可塑性、无反向传播。

---

## 2. 论文中的可操作参数

| 环节 | 论文参数 | 备注 |
|---|---|---|
| 培养物 | 人 iPSC 皮层神经元（DSI 或 NGN2）或 E15.5 小鼠皮层 | 单层、HD-MEA |
| 记录 | 1024 个电极；626 个属于感觉区；其余分 4 个 motor region | MaxOne 系统 |
| 感觉输入 | 8 个电极；位置编码 + 频率编码 4–40 Hz；75 mV | 球越近，频率越高 |
| 运动输出 | motor region 1 活动 → 球拍上；motor region 2 → 下；区域活动高者驱动；gain 目标 20 Hz | 无 ML 解码 |
| 命中反馈 | 75 mV，100 Hz，100 ms，8 电极同时 | 可预测刺激 |
| 未命中反馈 | 150 mV，5 Hz，4 s，随机位点/时序；之后 4 s rest | 不可预测刺激 |
| 静默反馈 | 等长 4 s 无刺激；球随机重置 | Silent |
| 无反馈 | 球反弹继续，不 reset | Open-loop |
| 学习窗口 | T1 = 0–5 min；T2 = 6–20 min | 同会话内 |
| 主要指标 | average rally length、aces、long rallies (>3) | 行为层 |
| 电生理指标 | 感觉-运动互相关、排他性运动事件、信息熵、功能可塑性（center of activity） | 机制层 |
| 关键对照 | 培养基、HEK293T、无反馈、静默、in-silico 随机球拍 | 排除非神经/非闭环解释 |

**论文的关键结果**：只有 MCC/HCC 出现学习；HCC 初期更差、后期更好；无反馈不学习；静默也能学一点但弱于可预测反馈；会话间学习不稳健；游戏期功能可塑性升高；可预测交换降低内部熵，不可预测反馈升高熵。

---

## 3. 模型映射

### 3.1 状态与动作

采用与 DishBrain / Paul et al. 2025 一致的低维状态：

- 球 \(y\)：8 个离散位置（对应 8 个感觉通道）；
- 球 \(x\)：到球拍的距离，映射为 4–40 Hz 的频率编码；
- 球拍 \(p\)：8 个离散位置；
- 动作：上 / 下（单细胞用连续速度，见下）。

### 3.2 感觉编码

对第 \(i\) 个通道（\(i=1,\dots,8\)）：

\[
r_i(x,y) = r_{\min} + (r_{\max}-r_{\min}) \cdot \frac{1-x}{1} \cdot \exp\left(-\frac{(i-y)^2}{2\sigma^2}\right)
\]

- \(r_{\min}=4\) Hz，\(r_{\max}=40\) Hz；
- \(x\in[0,1]\)：球到球拍的距离（1 = 最远，0 = 到达球拍）；
- \(\sigma\)：place code 宽度，默认 1 个 bin；
- 每个通道是一个 Poisson 脉冲序列，驱动一个 AMPA 型突触电导。

**简化**：论文用细胞外 75 mV 刺激；单房室模型没有细胞外场，因此把刺激强度映射为**每个突触前脉冲的有效电导**。这个映射是 Tier 1 校准参数，阶段 1 校准后冻结。

### 3.3 运动解码

**单细胞阶段**：

\[
v(t) = k_{\text{motor}} \cdot \left( r_{\text{cell}}(t) - r_{\text{ref}} \right)
\]

- \(r_{\text{cell}}\)：最近 100 ms 的放电率；
- \(r_{\text{ref}}=20\) Hz（DishBrain 的 gain 目标）；
- \(v\)：球拍速度，限幅到 \([-v_{\max}, +v_{\max}]\)；
- 球拍位置 \(p \leftarrow \mathrm{clip}(p + v\,\Delta t, 1, 8)\)。

**网络阶段**：两个 motor 细胞（up / down），或两个群体：

\[
v(t) = k_{\text{motor}} \cdot \left( r_{\text{up}}(t) - r_{\text{down}}(t) \right)
\]

可选一个抑制性中间神经元，提供侧抑制，帮助形成排他性运动事件。

### 3.4 反馈刺激

| 条件 | 模型实现 | 作用 |
|---|---|---|
| 可预测（命中） | 8 个通道同时 100 Hz 爆发，持续 100 ms | 同步、低方差驱动；三因子规则中 \(D>0\) |
| 不可预测（未命中） | 随机通道、随机时序的 Poisson 5 Hz，持续 4 s，幅度 ×2；之后 4 s rest | 高方差、高幅度驱动；\(D<0\) |
| 静默 | 4 s 无刺激；球随机重置 | \(D\approx 0\) 或弱负；对照 |
| 无反馈 | 球反弹继续；感觉刺激照常 | \(D=0\)；open-loop 对照 |

**关键简化**：论文的 150 mV / 5 Hz 是细胞外电压与频率；模型中用“有效突触电导 × 随机 Poisson”实现。幅度与频率的乘积决定总驱动量，阶段 1 校准。

**rest 的协议约定**：rest（以及未命中的不可预测刺激）期间**整局暂停**——球停在起点、球拍不移动；rest 结束后球从 `x = 1` 重新接近。不能让球在 rest 中继续前进：那样每次 miss 都会在 2 s 后再次到达并重置 rest，系统会永久锁在休息态（Phase 4 发现并修复的 bug）。

### 3.5 时间尺度

| 过程 | 时间尺度 | 模型实现 |
|---|---|---|
| 动作电位 / 突触事件 | ms | HH 方程 + 突触电导 |
| STDP 窗口 | 10–50 ms | 双相指数 |
| 资格迹 | 0.5–3 s | 指数衰减 |
| 反馈延迟 | 0.1–4 s | 游戏事件调度 |
| 稳态缩放 | 10–60 s | 慢变量 |
| 通道密度调节 | 30–300 s | 更慢变量 |
| 受体转运 | 1–10 min | 可选慢变量 |
| 学习评估 | 5–20 min | T1/T2 |

**注意**：毫秒级反馈是**驱动信号**，不是“毫秒级学习”。学习评估必须看秒到分钟的统计变化。

---

## 4. 生物映射表

| 模型元素 | 生物对应物 | 文献 | 备注 |
|---|---|---|---|
| 膜电位 \(V\) | 神经元膜电位 | Pospischil 2008 | 单房室 |
| Na/K/Ca/KCa/leak 通道 | 皮层规则放电细胞的电压门控通道 | Pospischil 2008 | 参数固定 |
| 突触电导 \(g_{\text{syn}}\) | AMPA 型兴奋性突触 | 常规 | 8 个感觉通道 |
| 突触权重 \(w_{ij}\) | 突触效能（受体数量/释放概率的集合变量） | Markram 1997; Song 2000 | 可塑 |
| STDP | NMDAR 依赖的时序可塑性 | Markram 1997; Andrade-Talavera 2023 | 双相窗口 |
| 资格迹 \(e_{ij}\) | Ca²⁺/CaMKII 局部痕迹 | Izhikevich 2007 | 桥接延迟反馈 |
| 三因子调制 \(D(t)\) | 多巴胺/神经调质/胶质递质 | Izhikevich 2007; Sanz-Gálvez 2024 | 全局但非反向传播 |
| 稳态缩放 | 突触缩放；Ca²⁺ 传感器；AMPA 转运 | Turrigiano 2012 | 负反馈 |
| \(g_{\max}\) 缩放 \(s_i\) | 通道密度/膜上通道数量 | O'Leary 2014; Tyagi 2025 | 内在可塑性 |
| \(V_{1/2}\) 偏移 \(\delta_i\) | 通道电压依赖性/翻译后修饰 | Remy 2010 | 内在可塑性 |
| 受体池 \(S/I\) | AMPA 表面池/胞内池；内吞/外排 | Haan 2026 | 慢稳态 |
| 短时程可塑性 | 突触易化/抑制 | 待阶段 2 定 | 可选 |
| 球拍读出 | MEA 的 motor region 活动 | Kagan 2022 | 最小退化 |
| 反馈刺激 | 8 个感觉电极的电刺激 | Kagan 2022 | 有效电导映射 |

---

## 5. 简化与局限（必须在报告中写明）

1. **单房室，不是全细胞**：没有树突形态、胞体-树突空间整合、细胞外场。通道动力学是简化的 HH 型。
2. **没有网络背景**：单细胞阶段没有其他神经元、没有胶质细胞、没有神经调质扩散；三因子信号是一个显式的“调制输入”，不是生化模拟。
3. **刺激映射是有效的**：论文的 75/150 mV 是细胞外电压；模型用突触电导等效。不能声称“复现了细胞外刺激”。
4. **学习规则是注入的**：STDP、稳态、通道调节都是我们写进去的，不是从生物物理细节涌现的。报告必须诚实说明。
5. **没有结构可塑性**：默认不生成/修剪突触；可选阶段 5 再加。
6. **没有短期记忆/长期记忆的完整生化**：资格迹是现象学变量。
7. **没有 proprioception**：与 DishBrain 一样，细胞看不到球拍位置；球拍位置通过闭环动力学隐式体现。
8. **“sentience”是形式定义**：论文指“对感觉印象作出适应性反应”，不是意识。

---

## 6. 与 DishBrain 的对照关系

| DishBrain | 本项目 | 是否可比 |
|---|---|---|
| 活体神经元网络 | 单细胞 / 2–12 细胞 | 规模大幅缩小 |
| HD-MEA 电刺激 | 突触电导驱动 | 有效刺激，不是细胞外场 |
| 两个 motor region | 单细胞 20 Hz 参考 / 两个 motor 细胞 | 结构退化 |
| 5 min 学习 | 5–20 min 会话 | 时间尺度可比 |
| 行为指标 rally length | 同 | 可比 |
| 功能可塑性（center of activity） | 单细胞用权重/参数轨迹；网络用活动中心 | 部分可比 |
| 信息熵 | 同（spike bin entropy） | 可比 |
| 无反馈/静默/随机对照 | 同 | 可比 |

---

## 7. 参考文献

- Kagan, B. J., et al. (2022). In vitro neurons learn and exhibit sentience when embodied in a simulated game-world. *Neuron*, 110, 3952–3969.
- Friston, K. J., et al. (2025). Active Inference and Intentional Behavior. *Neural Computation*, 37(4), 666–700.
- Paul, A., Khajehnejad, M., Habibollahi, F., Kagan, B. J., & Razi, A. (2025). Simulating Biological Intelligence: Active Inference with Experiment-Informed Generative Model. arXiv:2508.06980.
- Pospischil, M., et al. (2008). Minimal Hodgkin-Huxley type models for different classes of cortical and thalamic neurons. *Biological Cybernetics*, 99, 427–441.
- Markram, H., et al. (1997). Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs. *Science*, 275, 213–215.
- Song, S., Miller, K. D., & Abbott, L. F. (2000). Competitive Hebbian learning through spike-timing-dependent synaptic plasticity. *Nature Neuroscience*, 3(9), 919–926.
- Turrigiano, G. (2012). Homeostatic synaptic plasticity. *Cold Spring Harbor Perspectives in Biology*, 4, a005736.
- O'Leary, T., et al. (2014). Cell types, network homeostasis, and pathological compensation from a biologically plausible ion channel expression model. *Neuron*, 82(4), 809–821.
- Remy, S., Beck, H., & Yaari, Y. (2010). Plasticity of voltage-gated ion channels in pyramidal cell dendrites. *Current Opinion in Neurobiology*, 20, 503–509.
- Tyagi, S., et al. (2025). Sculpting excitable membranes: voltage-gated ion channel delivery and distribution. *Nature Reviews Neuroscience*, 26, 313–332.
- Haan, K. D., Gaudet, E., & Fisher, T. E. (2026). Common themes in evoked ion channel translocation in neuroplastic and homeostatic plasticity. *Frontiers in Pharmacology*, 17, 1727525.
- Izhikevich, E. M. (2007). Solving the distal reward problem through linkage of STDP and dopamine signaling. *Cerebral Cortex*, 17(10), 2443–2452.
- Sanz-Gálvez, R., et al. (2024). The role of astrocytes from synaptic to non-synaptic plasticity. *Frontiers in Cellular Neuroscience*, 18, 1477985.
