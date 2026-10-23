# 文献笔记

> 只记录“这篇文献给了我们什么、用在哪里”，不做全文复述。
> 已有 PDF 在 `reference/`；未下载的列在末尾。

---

## A. 范式与理论

### A1. Kagan et al. 2022, *Neuron* 110:3952–3969 — DishBrain

**核心**：人 iPSC 皮层神经元或 E15.5 小鼠皮层细胞培养在 HD-MEA 上，通过低延迟闭环与简化 Pong 耦合。感觉输入为 8 电极的位置编码 + 4–40 Hz 频率编码；运动输出由 motor region 活动驱动球拍；命中给可预测刺激（75 mV, 100 Hz, 100 ms, 全通道），未命中给不可预测刺激（150 mV, 5 Hz, 4 s, 随机位点）。5 min 内 rally length 增加，只有 MCC/HCC 学习，对照无学习。

**用在哪里**：协议参数、对照组、行为指标、电生理指标（功能可塑性、信息熵）、讨论中的 Hebbian + 稳态解释。

**注意**：论文没有说“STDP 是唯一机制”；它说的是功能性可塑性、Hebbian 与稳态的交互，以及“可预测刺激稳定权重、不可预测刺激破坏坏的自由能极小”。报告里不要把它简化成“STDP 驱动一切”。

### A2. Friston et al. 2025, *Neural Computation* 37(4):666–700 — Active Inference and Intentional Behavior

**核心**：用主动推断/自由能原理形式化 reactive、sentient、intentional 行为；用嵌套自由能最小化模拟 in vitro DishBrain 实验；区分“反应性”“感知性”“意向性”，后者用 inductive inference 形式化。

**用在哪里**：解释“为什么可预测刺激是奖励”；为三因子调制中的 \(D(t)\) 提供理论语言；报告的讨论部分。

### A3. Paul et al. 2025, arXiv:2508.06980 — Simulating Biological Intelligence

**核心**：用 POMDP 生成模型模拟 DishBrain 的 Pong；状态为 ball-x（38 级，4–41 Hz）、ball-y（8）、paddle-y（8）；动作为 up/down/stay；比较不同主动推断决策方案，强调记忆/反事实学习。

**用在哪里**：状态/动作空间设计；行为层基线；说明“行为层模拟”与“细胞层模拟”是两种不同层级，本项目做后者。

---

## B. 突触可塑性

### B1. Markram et al. 1997, *Science* 275:213–215

**核心**：双 whole-cell 记录皮层锥体神经元；突触后 AP 与 EPSP 的精确时序决定 EPSP 幅度上调或下调；pre-before-post → 增强，reverse → 减弱。

**用在哪里**：STDP 的实验奠基；学习窗口的方向性；报告中“STDP 有分子/电生理基础”的引用。

### B2. Song, Miller & Abbott 2000, *Nature Neuroscience* 3(9):919–926

**核心**：双相 STDP 可以产生竞争性 Hebbian 学习，不需要全局约束；权重分布、稳定性与学习窗口的关系。

**用在哪里**：STDP 数学形式；权重 clip 与稳定性；为什么“局部规则”可以产生竞争。

### B3. Andrade-Talavera et al. 2023, *Molecular Psychiatry* 28:2177–2188

**核心**：STDP 综述；时序精度、脑节律、胶质细胞（D-serine 等）在 STDP 中的作用；当前争议与局限。

**用在哪里**：说明 STDP 不是神经元孤立规则；支持加入慢调制/胶质样信号；提醒“in vitro 的 STDP 与 in vivo 不完全相同”。

---

## C. 内在可塑性与通道可塑性

### C1. Remy, Beck & Yaari 2010, *Current Opinion in Neurobiology* 20:503–509

**核心**：树突电压门控通道的密度、定位、生物物理特性随活动改变；可持久改变输入整合；可导致规则放电↔簇状放电的输出模式转换。

**用在哪里**：内在可塑性的生理依据；\(g_{\max}\) 缩放与 \(V_{1/2}\) 偏移；为什么单细胞可以通过内在可塑性改变输入-输出映射。

### C2. Tyagi et al. 2025, *Nature Reviews Neuroscience* 26:313–332

**核心**：电压门控通道的极化运输、囊泡分选、马达蛋白运输、靶向膜插入与 turnover；活动与疾病状态可动态调节通道定位，直接影响兴奋性。

**用在哪里**：“通道可塑性”不只是 AMPA；Na/K/Ca 通道密度也可变；为 \(s_i\) 的通用性提供依据。

### C3. Haan, Gaudet & Fisher 2026, *Frontiers in Pharmacology* 17:1727525

**核心**：诱发性通道转位（内吞/外排）；SNARE 异构体、endophilin 等共享分子组件；神经可塑性与稳态可塑性的共同执行机制；AMPA、TRPV1、渗透压调节等例子。

**用在哪里**：受体池 \(S/I\) 模型；内吞/外排速率的活动依赖；报告中的分子层面合法性。

---

## D. 稳态可塑性

### D1. Turrigiano 2012, *Cold Spring Harbor Perspectives in Biology* 4:a005736

**核心**：突触缩放；神经元通过 Ca²⁺ 依赖传感器检测自身放电率；调控 AMPA 受体在突触部位的累积；局部与全局稳态机制；稳定电路活动。

**用在哪里**：稳态缩放规则；目标放电率；防止 STDP 权重爆炸；“稳态不是学习，是稳定器”的论证。

### D2. O'Leary, Williams, Caplan & Marder 2014, *Neuron* 82(4):809–821

**核心**：从通道表达的分子生物学假设推导出一个简单模型；编码“活动设定点”；产生多样的自调节细胞类型；解释体内观察到的电导表达相关性；突触与内在电导都可被调节，从而自组装 CPG 网络。

**用在哪里**：通用的“活动依赖通道表达”规则；\(s_i\) 的更新骨架；比只做 AMPA 内吞更通用；回答“别的通道呢”。

---

## E. 胶质细胞与调制

### E1. Sanz-Gálvez et al. 2024, *Frontiers in Cellular Neuroscience* 18:1477985

**核心**：星形胶质细胞参与突触可塑性与非突触可塑性；通过 D-serine、ATP、谷氨酸等调制神经元兴奋性与可塑性。

**用在哪里**：三因子/慢调制的生理依据；可选的胶质样模块；讨论中“单细胞模型缺少胶质环境”的局限。

---

## F. 建模工具与细胞模型

### F1. Pospischil et al. 2008, *Biological Cybernetics* 99:427–441 — ModelDB 123623

**核心**：为不同皮层/丘脑细胞类型拟合“最小 HH 型模型”；RS、FS、IB、LTS 等；每个模型只包含复现该类型所需的少量电压依赖电流。

**用在哪里**：本项目的基础细胞（RS）；Tier 0 参数来源；f-I、spike waveform、适应的验证基准。

### F2. Izhikevich 2007, *Cerebral Cortex* 17(10):2443–2452

**核心**：用多巴胺调制的 STDP 解决 distal reward problem；STDP 在毫秒尺度触发，但后续可塑性对几秒内的多巴胺浓度敏感；随机网络可以学会奖励前的工作记忆模式。

**用在哪里**：三因子规则；资格迹；为什么毫秒级 STDP 可以服务秒级反馈。

### F3. Frémaux & Gerstner 2016, *Frontiers in Neural Circuits*

**核心**：神经调质 STDP 的综述；三因子规则、资格迹、奖励预测误差与局部可塑性的关系。

**用在哪里**：三因子规则的理论框架；与“强化学习”的边界（我们不做全局价值函数，只做局部资格迹 + 调制信号）。

### F4. Zenke, Agnes & Gerstner 2015, *Nature Communications* 6:6922

**核心**：多种突触可塑性机制（STDP、稳态、异突触）协同，形成并检索记忆；稳定性与竞争。

**用在哪里**：STDP + 稳态的组合；为什么需要负反馈；阶段 3 的消融设计。

### F5. Luboeinski et al. 2026, *PLOS Computational Biology* 22(2):e1013926 — Plastic Arbor

**核心**：扩展 Arbor，支持 spike-driven 的同突触、稳态、异突触可塑性；异突触例子基于树突分支内的钙扩散；与 Brian 2 交叉验证；面向大规模、形态详细的网络，支持 HPC/GPU。

**用在哪里**：阶段 5 的可选分支（形态详细细胞、树突异突触、大规模网络）；**不作为阶段 0–4 的主平台**。

**注意**：它的异突触优势依赖多房室树突的空间扩散；单房室模型没有树突，用不上这个优势。若单房室需要异突触效应，可以用 Brian 2 的 `network_operation`/`run_regularly` 做一个共享突触资源的现象学规则。

---

## G. 文献状态

> 用户已确认：核心文献全部下载完成，位于 `reference/`。

| 文献 | 用途 | 状态 |
|---|---|---|
| Pospischil et al. 2008 原文 PDF | Tier 0 参数与验证 | 已下载 |
| ModelDB 123623 模型代码 | 细胞实现 | 已下载（`reference/.../PospischilEtAl2008/`） |
| O'Leary et al. 2014 原文 PDF | 内在可塑性规则 | 已下载 |
| O'Leary et al. 2013 PNAS | 通道表达相关性 | 已下载 |
| Izhikevich 2007 原文 PDF | 三因子规则 | 已下载 |
| Frémaux & Gerstner 2016 综述 | 三因子框架 | 已下载 |
| Zenke et al. 2015 原文 | STDP + 稳态 | 已下载 |
| Vogels et al. 2011 原文 | 抑制性可塑性/E-I 平衡 | 已下载 |
| Bakkum et al. 2008 原文 | 具身网络学习前身 | 已下载 |
| Chao et al. 2008 原文 | 闭环塑造网络行为 | 已下载 |
| Isomura & Friston 2018 原文 | 体外网络最小化自由能 | 已下载 |
| Destexhe & Paré 1999 原文 | 两房室模型（可选） | 已下载 |
| Plastic Arbor 2026 原文 | Arbor 可塑性框架（可选分支） | 已下载 |
| Allen Cell Types Database（可选） | 多房室验证 | 可选，未下载 |

---

## H. 文献使用原则

1. **每个模型变量至少对应一篇文献**；没有对应物的变量不进入模型。
2. **不要把“有生理基础”说成“模型自动会学习”**；可塑性规则是注入的。
3. **不要把 DishBrain 的“sentience”说成意识**；它是形式定义。
4. **区分“现象学模型”与“生物物理模型”**：STDP 是现象学规则，不是 NMDAR 的分子模拟；报告要写明。
5. **引用具体参数时给出处**：A+/A−/τ、目标放电率、时间常数、边界，不要凭空写。
