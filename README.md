# BBN — 单细胞 DishBrain 式闭环学习实验

> 用 Brian 2 构建一个生理可解释的单房室皮层神经元，按 DishBrain 的闭环反馈协议训练它玩简化 Pong。先完成一个细胞，再扩展到 2–12 个细胞的极小网络。

**版本**：v0.22.0-phase7-recurrent-ei  
**状态**：阶段 0/1/2/3/4 已完成；Phase 5 P0–P5、Phase 6a 与 Phase 7a 已完成。600 s 长会话给出目前最强的行为结果：push-pull static 显著优于 symmetric 与 random paddle，但绝对命中率仍只有 0.17–0.19。三种抑制 motif 都不产生 motor 分化，抑制线已停止。放慢球使 K_eff 0.141→0.094、hit 0.169→0.150；归一化读出使 K_eff 0.141→0.177，但 hit 0.169→0.167。P0 背景噪声（3 Hz/80 nS）使 quiet-rest 达 4.6 Hz，但 3b 仍饱和（at w_max 0.40，w_diff −0.027），噪声线停止。P1 局部信用首次在干净对照下形成正确 y 梯度（w_diff 0.000→0.780，显著优于全局 3b，p=0.014），但行为仅与 static 持平（0.220 vs 0.204，p=0.512），局部信用线停止。P2 动态稳态带（[5,30] Hz，仅 play）把 at w_max 0.34→0.14、impact corr 0.179→0.381，但全局 D 仍 0 梯度，local_dyn 行为 0.196 ≈ static 0.204（p=0.643），动态带线停止。P3 的 TM STP 真实改变时间形状（early 0.569→0.699、gap 0.171→0.118）并提高梯度与读出（0.780→0.880、impact 0.735→0.809），但命令幅度减半使行为未升（0.187 vs 0.220，p=0.243），时间维度线停止。P4 的 10 细胞 E/I 网络存活且静态等价（0.203 vs 0.204，p=0.990），但读出信息减半（impact 0.920→0.479），可塑性使行为显著变差（net_local 0.127，p=0.005；net_global 0.148，权重崩到 0.27），扩网络线停止。P5 的 PD 读出（τ_pred=50 ms）对行为无影响（local_pd 0.220 ≡ local_no_hs 0.220，p=0.998；static_pd 0.210 vs 0.204，p=0.722），接口线停止。6a 的帧式延迟编码开环验证未过 Gate（corr(Δt, ball_y)=0.442 < 0.5，Δt P95 仅 4.0 ms），A 线关闭。7a 按用户授权覆盖硬停止、检验 22 细胞递归 E-I：允许的 w_ee 网格内 E 率为 3.67 / 4.07 / 158.0 / 253.2 Hz，**没有 5–25 Hz 工作点**，网络呈“~4 Hz 背景态 ↔ >150 Hz 点火态”双稳态，Gate 不通过，B 线永久关闭。**八条线合起来说明：在 2–22 细胞极小网络中，行为上限由读出结构、信息到达时刻与执行器增益决定；改可塑性、稳态、动力学、规模、接口、输入编码或递归拓扑都无法突破。** 另修复了一个污染 Phase 1/3 的 rest 锁死协议 bug，并已重跑。  
**最后更新**：2026-10-23

---

## 0. 先读这两份

- **README.md（本文）**：项目是什么、为什么这样设计、路线图。
- **[HANDOFF.md](HANDOFF.md)**：当前进度、已拍板的决定、下一步、如何恢复运行。

详细文档：

- [docs/protocol_and_biology.md](docs/protocol_and_biology.md)：DishBrain 协议与生物对应物
- [docs/parameter_policy.md](docs/parameter_policy.md)：固定参数 / 校准参数 / 可塑状态变量的边界（**回答“参数不可调，学习从哪来”**）
- [docs/experiment_plan.md](docs/experiment_plan.md)：阶段 0–5 的任务、对照、指标、断点续跑
- [docs/literature_notes.md](docs/literature_notes.md)：文献笔记与引用

---

## 1. 项目是什么 / 不是什么

### 是什么

- 一个**计算神经科学**的探索性项目：用生物物理可解释的脉冲神经元，复现 DishBrain 的“闭环反馈驱动适应”范式。
- 一个**方法学实验**：验证“单细胞在闭环反馈下能否产生有方向性的适应”，以及“最小网络能否比单细胞更好”。
- 一个**可复现的工程框架**：固定随机种子、预注册指标、多种子对照、断点续跑。

### 不是什么

- **不是机器学习项目**。禁止反向传播、全局损失函数、梯度下降调参、用 Transformer/CNN 拟合学习曲线。
- **不是“打赢 Pong”的产品**。学习效果不佳是合法结果；负结果同样有科学价值。
- **不是全细胞生化模拟**。没有蛋白质合成、代谢、完整信号通路；只有电生理 + 局部可塑性规则。
- **不是对湿实验的替代**。它是“协议验证 + 机制筛选”的干实验。

---

## 2. 核心科学问题

1. **单细胞**：一个具有 HH 通道、STDP、稳态缩放、内在可塑性的单房室神经元，在 DishBrain 式闭环反馈下，能否产生可观测的、有方向性的输入-输出映射变化？还是只能表现出稳态抵抗？
2. **极小网络**：2–12 个同类细胞组成的网络，能否比单细胞表现出更好的适应？最低的“涌现”门槛在哪里？
3. **可塑性规则**：STDP、稳态缩放、内在通道调节、受体转运，各自在闭环扰动下的相对贡献是什么？时间尺度如何叠加？

---

## 3. 关键设计决策（已拍板）

| # | 决策 | 选择 | 理由 |
|---|---|---|---|
| 1 | 仿真平台 | **Brian 2 2.10.1 + Python 3.12**（Arbor/Plastic Arbor 仅作阶段 5 可选分支） | 纯 Python、易改方程、支持闭环；本项目不需要 NEURON；Plastic Arbor 的异突触优势依赖树突 |
| 2 | 基础细胞 | **Pospischil et al. 2008 的 RS 单房室 HH 模型**（ModelDB 123623） | 已发表的皮层规则放电细胞，含 Na/K/Ca/KCa/leak；参数固定即可复现电生理 |
| 3 | 参数政策 | **三层：身份参数（固定）/ 接口参数（校准后冻结）/ 可塑状态变量（变化）** | 既保证生理真实性，又给学习留出生物学自由度；详见 `docs/parameter_policy.md` |
| 4 | 单细胞读出 | **放电率相对 20 Hz 参考 → 球拍速度** | 对 DishBrain 两个 motor region + 20 Hz gain 的最小忠实退化 |
| 5 | 单细胞主实验 | **三因子资格迹（STDP + 可预测性调制）为主；纯 STDP 为消融对照** | 全通道反馈会抹掉位置编码；单细胞必须补信用分配 |
| 6 | 网络阶段 | **先 2–5 个细胞；若稳定再扩到 ~12 个** | 先回答“最小网络是否更好”，避免一次性上大网络 |
| 7 | 断点续跑 | **trial 级 checkpoint + run manifest + `--resume`** | 支持 24 h 连续运行与随时关机恢复 |
| 8 | 统计 | **多种子、预注册指标、配对/混合效应、效应量、对照** | 防止用单次幸运结果编故事 |
| 9 | 成功标准 | **可复现、可解释、对照完整；不要求打赢 Pong** | 探索性项目，负结果合法 |

---

## 4. “参数固定”与“学习能力”的矛盾：本项目怎么解决

这是本项目最容易被误解的一点，必须说清楚。

### 4.1 细胞有两层，不是一层

- **身份层（Tier 0，固定）**：膜电容、通道门控方程、反转电位、基础最大电导、形态。这些定义“这是一只什么细胞”。如果让它们自由变化，细胞就不再是皮层 RS 神经元，而变成一个任意的函数拟合器——那就是机器学习，不是生理学。
- **状态层（Tier 2，可塑）**：突触权重、资格迹、通道最大电导的缩放因子、半激活电压偏移、受体表面/胞内池。这些是细胞的“经验”，随活动按局部生物规则变化。

**学习来自状态层，不来自身份层。** 真实神经元在分钟尺度上也不会改写 Na 通道的门控方程；它改变的是突触强度、通道密度、受体数量。这就是本项目的科学合法性。

### 4.2 四个可塑状态变量（都有生理对应物）

| 可塑变量 | 更新规则 | 生理对应 | 关键文献 |
|---|---|---|---|
| 突触权重 \(w_{ij}\) | 双相 STDP + 资格迹 + 可预测性调制：\(\Delta w_{ij} = \eta \, D(t) \, e_{ij}\) | NMDAR 作为 coincidence detector；多巴胺/神经调质门控 | Markram 1997；Song 2000；Izhikevich 2007 |
| 通道最大电导 \(g_{\max,i}\) | 活动/Ca²⁺ 低通信号驱动的表达规则，带上下限 | 通道密度/膜上通道数量变化（内吞/外排、表达调控） | O'Leary 2014；Remy 2010；Tyagi 2025 |
| 半激活电压 \(V_{1/2,i}\) | 活动依赖的偏移，带上下限 | 通道电压依赖性的翻译后修饰/亚基组成变化 | Remy 2010 |
| 受体池 \(S_{ij}\) / \(I_{ij}\) | 活动依赖的内吞/外排：\(dS/dt = k_{exo} I - k_{end} S\) | AMPA 受体表面池与胞内池的转运 | Turrigiano 2012；Haan 2026 |

此外还有**稳态缩放**：\(\Delta w_{ij} = \eta_w (r_{\text{target}} - \bar r) w_{ij}\)，把平均放电率拉回目标值。它不是“奖励”，而是负反馈稳定器。

### 4.3 还有一类“参数”是实验接口，不是细胞

DishBrain 里的 75 mV / 150 mV 是**细胞外刺激电压**；在我们的单房室模型里，它必须映射成**有效突触电导**。这类参数（感觉输入增益、反馈增益、噪声水平、读出增益）是“实验台的旋钮”，不是细胞的生物学参数。

处理方式：

1. 在阶段 0/1 **校准一次**，使细胞落在 4–40 Hz 工作区间、反馈强度能产生可测扰动；
2. 校准后**冻结**，所有条件、所有种子共用；
3. 在 `config/` 中记录来源和日期；
4. **不允许**在看完 Pong 成绩后回头调它。

### 4.4 因此，“不可调整”准确的意思是

- **不因为游戏成绩去调身份参数**；
- **不因为游戏成绩去调已冻结的接口参数**；
- **允许**可塑状态变量按局部规则变化；
- **允许**把可塑性规则本身作为**预注册的实验变量**（例如 STDP-only vs STDP+稳态 vs 三因子），而不是拟合旋钮。

详见 [docs/parameter_policy.md](docs/parameter_policy.md)。

---

## 5. 系统架构

```text
Pong 环境 ──球位置──> 8 通道感觉编码 ──突触输入──> 虚拟细胞（HH + 可塑性）
    ^                                                        │
    │                                                        │ 放电率
    └──球拍动作── 运动解码（放电率 → 速度） <────────────────┘
    │
    └──命中/未命中──> 反馈刺激（可预测/不可预测）──> 回到同一组 8 通道
```

| 模块 | 职责 | 目录（待实现） |
|---|---|---|
| 环境 | 球、球拍、碰撞、命中/未命中、reset | `src/env/` |
| 细胞 | HH 膜方程、通道门控、突触 | `src/cell/` |
| 可塑性 | STDP、资格迹、稳态缩放、内在可塑性、受体池 | `src/plasticity/` |
| 闭环 | 10 ms tick、刺激调度、状态机 | `src/loop/` |
| IO | 配置、run manifest、checkpoint、日志 | `src/io/` |
| 指标 | rally length、aces、long rallies、熵、权重轨迹 | `src/metrics/` |

---

## 6. 阶段路线图

| 阶段 | 目标 | 状态 | 通过标准（Gate） |
|---|---|---|---|
| **0** | 环境 + 基线细胞：跑通 Pospischil RS，验证 f-I、spike waveform、适应 | **已完成（全部 PASS）** | 静息电位、Rin、rheobase、spike、适应均在合理范围；无爆炸 |
| **1** | Pong + 静态闭环：8 通道编码、运动解码、四种反馈；无可塑性 | **已完成**（静态基线接近随机；闭环正常） | 无崩溃；静态细胞不优于 always-up/down 对照 |
| **2** | 可塑性模块 + 规则验证：STDP 窗口、稳态收敛、通道调节、受体池 | **已完成**（STDP/资格迹/稳态 PASS） | STDP 非对称窗口；放电率收敛；参数不越界 |
| **3** | 单细胞闭环学习：3a 字面 DishBrain；3b 三因子；完整对照 | **已完成（负结果；协议修复后重跑）** | 3b 优于对照（效应量可报告）；否则如实记录负结果 |
| **4** | 极小网络：2–5 细胞，必要时扩到 ~12；重复阶段 3 协议 | **已完成（2/3/4 细胞 + 慢球 + 归一化）**：push-pull 读出结构优势在 600 s 显著但小；三种抑制 motif 都无分化；慢球/归一化都不是修复；无可塑性学习，长会话中可塑性有害 | 网络不差于单细胞；记录任何“最小涌现” |
| **5** | 可选扩展 + 最终报告：受体转运、胶质样调制、结构可塑性 | **P0 背景噪声、P1 局部信用、P2 动态稳态带、P3 STP、P4 10 细胞 E/I、P5 PD、6a 延迟编码、7a 递归 E-I 已完成（均未带来行为增益；6a/7a 未过 Gate）** | 报告完整、可复现、局限清晰 |

**硬门控**：阶段 3 完成并写出报告后，才进入阶段 4。不要在单细胞还没跑完时并行铺开网络。

---

## 7. 成功标准

**一级成功（必须达到）**

- 仿真可复现：固定种子、配置、run manifest。
- 每一步都有生理对应物，没有“黑箱调参”。
- 对照完整：无反馈、静默、打乱反馈、静态细胞、随机球拍、always-up/down。
- 负结果如实报告，不挑 seed、不挑时间窗。

**二级成功（希望达到，不保证）**

- 单细胞出现**有方向性的**输入-输出映射变化（权重梯度、通道参数、放电率区间漂移）。
- 极小网络比单细胞表现出更好的 rally length 或更清晰的 motor 分化。

**明确**：成功 ≠ 打赢 Pong。一个干净的负结果，胜过一条调出来的假学习曲线。

---

## 8. 目录结构

```text
bbn/
├─ README.md                     # 项目概况（本文）
├─ HANDOFF.md                    # 工作交接文档（每次会话结束更新）
├─ config/
│  └─ experiment_default.yaml    # 参数骨架（阶段 0 填 Tier 0，阶段 1 校准 Tier 1）
├─ docs/
│  ├─ protocol_and_biology.md    # DishBrain 协议 + 生物映射
│  ├─ parameter_policy.md        # 固定/校准/可塑三层政策
│  ├─ experiment_plan.md         # 阶段任务、对照、指标、断点续跑
│  └─ literature_notes.md        # 文献笔记
├─ src/
│  ├─ cell/                      # HH 细胞、通道、突触
│  ├─ plasticity/                # STDP、资格迹、稳态、内在可塑性、受体池
│  ├─ env/                       # Pong 环境
│  ├─ loop/                      # 闭环控制器
│  ├─ io/                        # 配置、checkpoint、run manifest
│  └─ metrics/                   # 指标与分析
├─ experiments/                  # 阶段脚本（phase0_*.py …）
├─ tests/                        # 规则验证（STDP 窗口、f-I、收敛）
├─ runs/                         # 每次运行的 manifest、日志、checkpoint
├─ checkpoints/                  # 可选：集中式断点（或放 runs/<id>/）
├─ results/                      # 汇总结果、图、报告
└─ reference/                    # 已有文献（不要改动）
```

---

## 9. 环境与算力

**参考环境**

- 任意 4 核以上 CPU、8 GB 以上内存即可；**GPU 非必需**（Brian 2 与 Numba 均使用 CPU）。
- 开发与验证环境为 Windows + Python 3.12；Linux / macOS 同样适用，只需把激活命令换成
  `source .venv/bin/activate`。
- 完整复现（600 s × 15 seeds × 多条件）建议 10 核以上并行：
  每个 `(condition, seed)` 是单进程单线程，`--jobs` 不要超过物理核数，避免线程超订。

**运行环境（阶段 0/1 建立）**

```bash
python -m venv .venv
# Windows:  .\.venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
python -m pip install brian2 numpy matplotlib pandas pyyaml numba
```

- **Brian 2** 是 Phase 0 的参考实现；**Numba** 引擎（`src/cell/hh_numba.py`）是 Phase 1/3 的生产引擎，
  方程相同，速度快约 60–80×。本项目不需要 NEURON 或 GPU。
- 核数越多，可并行的 `(condition, seed)` 越多；显存与 GPU 与本项目无关。

**24 h 运行**

- 每个 `(condition, seed)` 是一个 run，独立进程。
- trial 边界保存 checkpoint；支持 `--resume`、`--max-wall-hours`、Ctrl+C 优雅退出。
- 设计细节见 [docs/experiment_plan.md](docs/experiment_plan.md) 的“断点续跑”一节。

---

## 10. 运行方式

阶段 0–4 已可用。以下命令假定已激活 `.venv`（见 §9）：

```bash
# 阶段 0：基线细胞（Brian 2 参考实现）
python experiments/phase0_baseline.py --config config/cell_pospischil_rs.yaml

# 阶段 1：静态闭环（Numba 快速引擎）
python experiments/phase1_static_loop.py --config config/phase1.yaml

# 阶段 1 诊断：单细胞率是否携带 ball_y 信息（120 s，与 Phase 3/4 对齐）
python experiments/phase1_diagnostic.py --config config/phase1.yaml --duration 120

# 阶段 2：可塑性规则验证
python experiments/phase2_stdp_window.py --config config/phase2.yaml
python experiments/phase2_eligibility.py --config config/phase2.yaml
python experiments/phase2_homeostasis.py --config config/phase2.yaml

# 阶段 3：单细胞闭环学习
python experiments/phase3_single_cell.py --config config/phase3.yaml

# 阶段 4：两池差分读出（2 细胞）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10

# 阶段 4 增益敏感性（预注册，仅用于机制检验）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --velocity-gain 0.30 --outdir results/phase4_gain030
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --velocity-gain 0.60 --outdir results/phase4_gain060

# 阶段 4 恒常率（预注册，v0.8.0）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --rate-min 20 --rate-max 20 --outdir results/phase4_const_rate

# 阶段 4 长会话（预注册，v0.9.0；trace 10× 降采样）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --outdir results/phase4_600
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --rate-min 20 --rate-max 20 --outdir results/phase4_const_rate_600

# 阶段 4 三细胞抑制版（v0.10.0；预注册，g_inh=10 nS）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --inhibitory --inh-weight 10 --outdir results/phase4_inhibition_600

# 阶段 4 四细胞交叉抑制版（v0.11.0；预注册，g_rec=40 nS，g_inh=10 nS）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --cross-inhibition --cross-rec-weight 40 --inh-weight 10 --outdir results/phase4_cross_inhibition_600

# 阶段 4 差分调谐抑制版（v0.12.0；预注册，g_inh=10 nS，tuned_gain=1.0）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --tuned-inhibition --inh-weight 10 --outdir results/phase4_tuned_inhibition_600

# 阶段 4 放慢球（v0.13.0；预注册，ball_speed=0.25）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --ball-speed 0.25 --outdir results/phase4_slow_ball_600

# 阶段 4 归一化读出（v0.14.0；预注册，k_norm=5.0）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --normalized-readout --outdir results/phase4_norm_readout_600

# 阶段 5 P0 背景自发活动（v0.15.0；预注册，3 Hz, 80 nS）
python experiments/phase4_network.py --config config/phase4.yaml --jobs 10 --duration 600 --trace-stride 10 --bg-noise-hz 3 --bg-noise-weight 80 --conditions phase4_pushpull_static,phase4_pushpull_3b,phase4_pushpull_3b_no_hs,phase4_symmetric_static --outdir results/phase5_bg_noise_600
```

---

## 10A. 数据可用性（Data availability）

**仓库内已包含**（足以复现报告中的全部数字与图）：

| 内容 | 位置 | 规模 |
|---|---|---|
| 每个 seed 的指标汇总 | `results/*/summary.csv`（46 份） | 约 1.5 MB |
| 每个条件的均值 / SD | `results/*/summary_by_condition.csv`（46 份） | 同上 |
| 报告与逐阶段报告 | `results/*.md` | — |
| 最终报告 PDF / 图 | `results/final_report.pdf`、`results/figures/`（7 张汇总图）及各阶段 PNG | 约 7 MB |
| 代码、配置、预注册与参数日志 | `src/`、`experiments/`、`config/`、`HANDOFF.md`、`docs/` | — |

**仓库内未包含**（原始逐 tick 输出，共约 2.9 GB）：

| 目录 | 内容 | 文件数 | 体积 |
|---|---|---:|---:|
| `results/**/traces/` | 每 10 ms 一行：球位置、放电率、速度、事件、spike 数（Phase 4 还含权重、reward、抑制指标） | 1,920 | 2,691 MB |
| `results/**/impacts/` | 每次击球一行：冲击时刻、`ball_y`、冲击前 300 ms 率差/上/下率、是否命中 | 1,724 | 7.1 MB |
| `results/**/weights/` | 每 5 s 的 16 通道权重快照 | 1,724 | 185 MB |

未纳入仓库的原因只有体积（会让每次 `git clone` 下载近 3 GB）；这些文件**不含任何个人信息**，只有仿真状态。`.gitignore` 中的
`results/**/traces/`、`results/**/impacts/`、`results/**/weights/` 即为对应规则。

**如何获得逐 tick 数据**：

1. **重跑**（推荐，固定 seed 可复现）：按 §10 的命令运行对应阶段；
   `--trace-stride 10` 会把 trace 降采样 10 倍，显著减小体积。600 s × 15 seeds 的计算量较大。
2. **不重跑**：如需原始 traces/impacts/weights 数据包，可联系作者，或从 Zenodo / OSF 获取
   （若已发布，在此补充 DOI）。

`summary.csv` 是**每个 seed 一行**，包含报告中使用的全部指标（rally、impact corr、`w_diff corr`、
early/late norm corr、at `w_max`、网络率等），因此统计复核与图表重绘不需要原始 traces。

---

## 11. 文档索引

| 文档 | 内容 |
|---|---|
| [HANDOFF.md](HANDOFF.md) | 当前状态、已拍板决定、下一步、恢复运行、交接清单 |
| [docs/protocol_and_biology.md](docs/protocol_and_biology.md) | DishBrain 参数、模型映射、生物对应表、简化与局限 |
| [docs/parameter_policy.md](docs/parameter_policy.md) | Tier 0/1/2/3 参数分层、更新规则、边界、校准与冻结规则 |
| [docs/experiment_plan.md](docs/experiment_plan.md) | 阶段 0–5 的任务、对照、指标、统计、checkpoint |
| [docs/literature_notes.md](docs/literature_notes.md) | 核心文献要点、用途、文献状态（已全部下载） |
| [results/final_report.md](results/final_report.md) | **最终报告**：Phase 0–5、6a、7a 的方法、逐阶段结果、7 张图、机制归因、统计与复现 |
| [results/phase4_long_session.md](results/phase4_long_session.md) | Phase 4 最终行为结论（600 s 长会话、两组置换检验、H1–H4 判定） |
| [results/phase4_inhibition_report.md](results/phase4_inhibition_report.md) | 三细胞抑制版（v0.10.0）：共享前馈抑制不产生 motor 分化 |
| [results/phase4_cross_inhibition_report.md](results/phase4_cross_inhibition_report.md) | 四细胞交叉抑制版（v0.11.0）：I_up/I_down 被平衡，仍无分化 |
| [results/phase4_tuned_inhibition_report.md](results/phase4_tuned_inhibition_report.md) | 差分调谐抑制版（v0.12.0）：差分信号不足，抑制线停止 |
| [results/phase4_slow_ball_report.md](results/phase4_slow_ball_report.md) | 放慢球（v0.13.0）：K_eff 减半，不是修复 |
| [results/phase4_norm_readout_report.md](results/phase4_norm_readout_report.md) | 归一化读出（v0.14.0）：K 提高 26%，行为不变 |
| [results/phase5_bg_noise_report.md](results/phase5_bg_noise_report.md) | Phase 5 P0 背景噪声（v0.15.0）：4.6 Hz 仍不足以阻止稳态饱和 |
| [results/phase5_local_credit_report.md](results/phase5_local_credit_report.md) | Phase 5 P1 局部信用（v0.16.0）：梯度形成，但行为未超过手工结构 |
| [results/phase5_dynamic_homeostasis_report.md](results/phase5_dynamic_homeostasis_report.md) | Phase 5 P2 动态稳态带（v0.17.0）：饱和减半，仍无梯度与行为增益 |
| [results/phase5_stp_report.md](results/phase5_stp_report.md) | Phase 5 P3 STP（v0.18.0）：时间形状改变、信息提高，行为未升 |
| [results/phase5_ten_cell_report.md](results/phase5_ten_cell_report.md) | Phase 5 P4 10 细胞 E/I（v0.19.0）：静态等价、信息减半，可塑性更差 |
| [results/phase5_pd_readout_report.md](results/phase5_pd_readout_report.md) | Phase 5 P5 PD 读出（v0.20.0）：τ_pred=50 ms 对行为无影响 |
| [results/phase6a_latency_validation_report.md](results/phase6a_latency_validation_report.md) | Phase 6a 帧式延迟编码（v0.21.0）：开环 Gate 不通过，A 线关闭 |
| [results/phase7a_rec_ei_gate_report.md](results/phase7a_rec_ei_gate_report.md) | Phase 7a 递归 E-I（v0.22.0）：网格内无 5–25 Hz 工作点，Gate 不通过，B 线永久关闭 |
| [results/phase4/phase4_report.md](results/phase4/phase4_report.md) | Phase 4 主报告（120 s 机制筛查 + 读出/权重分析） |
| [results/phase4_gain_sensitivity.md](results/phase4_gain_sensitivity.md) | Tier 1 增益敏感性（0.30/0.60，负结果） |

---

## 12. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-10-21 | v0.1.0-scaffold | 建立目录骨架；写入 README、HANDOFF、协议/参数政策/实验计划/文献笔记；未执行阶段 0 |
| 2026-10-21 | v0.2.0-phase0-ready | 创建 `.venv` 并安装 Brian 2；实现 `experiments/phase0_baseline.py`；smoke test 通过 |
| 2026-10-21 | v0.3.0-phase0-done | 正式 Phase 0 完成：全部基线指标 PASS；速度 25× 慢于实时，Phase 1 前需优化 |
| 2026-10-21 | v0.4.0-phase1-done | 加入 Numba 快速引擎（约 60–80×）；完成 Pong + 静态闭环 + 6 条件对照 + 诊断；静态单细胞接近随机，率读出几乎不携带 ball_y |
| 2026-10-21 | v0.5.0-phase2-done | 完成 STDP 窗口、资格迹 + 三因子、稳态缩放验证；全部 PASS；下一步 Phase 3 |
| 2026-10-21 | v0.6.0-phase3-done | 完成单细胞闭环学习（11 条件 × 15 seeds × 120 s）；负结果：3a/3b 与 static/random 无差异；权重变化主要由稳态主导；下一步 Phase 4 两池差分读出 |
| 2026-10-21 | v0.7.0-phase4-done | 发现并修复 rest 锁死协议 bug（旧实现中球在 rest 期间继续前进，约 94% tick 永久休息）；Phase 1/3 重跑。完成 2 细胞 push-pull：差分读出 r≈0.92（单细胞 R²=0.007），但 rally 仅 0.214 vs random 0.141（p=0.18）；可塑性无可靠增益，稳态使两池权重饱和趋同；当时推测 K≈0.20/s 是行为瓶颈（v0.7.1 证明它不是可调杠杆） |
| 2026-10-21 | v0.7.1-phase4-gain-sensitivity | 预注册 Tier 1 增益敏感性（velocity_gain = 0.30/0.60，7 条件 × 15 seeds）。H1/H3 被否定：static rally 0.214→0.201→0.246（非单调），impact error 单调下降（1.84→1.64→1.32）但命中率不升；no_hs 与 static 持平，3b 在 0.60 下显著更差（−0.152，p=0.010）；K_eff 保持 ≈0.20/s。H2/H4 成立。结论：瓶颈是读出信号的时间形状，不是标量增益 |
| 2026-10-21 | v0.8.0-phase4-const-rate | 预注册恒常率实验（20/20 Hz）。信号层面早期信息增强：early corr 0.659→0.769，mean |diff| 3.09→4.90 Hz，K_eff 0.197→0.251；但末端率因子 40→20 Hz，冲击前斜率 4.76→2.75 Hz/bin。行为层面不可判定：static 0.214→0.244，而 frozen-paddle 对照 0.106→0.219（static−symmetric p=0.696）。H1 仅信号层面部分支持，H2 被对照漂移破坏，H3 不支持，H4 支持。 |
| 2026-10-21 | v0.9.0-phase4-long-session | 预注册 600 s 长会话（主协议 + 恒常率，7 条件 × 15 seeds，trace 10× 降采样）。frozen-paddle hit 0.138/0.152 ≈ 理论 1/7；static 比 symmetric 高 +0.042/+0.056（p=0.016/0.018），比 random 高 +0.079/+0.111（p=0.0002/0.0001）；恒定率无额外收益（+0.031，p=0.183）。可塑性有害：3b −0.053/−0.083（p=0.013/0.002）；no_hs 的 T1→T2 hit 0.190→0.109（p=0.0001）。结论：结构读出真实但增益小；不再调 gain/率值 |
| 2026-10-22 | v0.10.0-phase4-inhibition | 新增抑制性电导与 3 细胞网络（2 motor + 1 I；g_inh=10 nS，E_inh=−80 mV，tau=10 ms）。关闭抑制时 trace 与 v0.9.0 逐位一致。结果：共享前馈抑制不产生 motor 分化（exclusive 0.022 vs 2-cell 0.0217；I–motor corr 0.985），行为无额外收益（static 0.222 vs 0.204）；可塑性仍有害（3b/no_hs/play_hs 均显著低于 static）。 |
| 2026-10-22 | v0.11.0-phase4-cross-inhibition | 4 细胞交叉抑制（I_up 抑制 down，I_down 抑制 up；g_rec=40 nS，g_inh=10 nS，10 ms 延迟）。回退验证逐位一致。结果：I_up/I_down spike 数差异 <0.5%（两池总率相近，交叉抑制被平衡），exclusive 0.0221 ≈ 2-cell 0.0217；static 0.194 < 2-cell 0.204/shared 0.222，cross 臂内 static−symmetric 不显著（p=0.152）；可塑性仍无收益。 |
| 2026-10-22 | v0.12.0-phase4-tuned-inhibition | 差分调谐抑制（I_up/I_down 接收 8 通道感觉，push-pull 权重；g_inh=10 nS）。结果：corr(I_up−I_down, y)=0.196 <0.5（H1 失败）；I_up/I_down 总 spike 差异 <1%，exclusive 0.0236；static 0.228 为四臂最高但仅比 2-cell 0.204 高 0.024；symmetric 不再是冻结球拍（调谐 I 注入差分），static−symmetric 不能作干净对照；no_hs/3b 显著低于 static。按预注册停止规则，抑制网络线到此为止 |
| 2026-10-22 | v0.13.0-phase4-slow-ball | 放慢球（ball_speed 0.5→0.25，回合 2 s→4 s；7 条件 × 15 seeds × 600 s）。结果：static hit 0.169→0.150、rally 0.204→0.178；K_eff 0.141→0.094（更多时间花在低率因子段）；static−symmetric 不显著（+0.030，p=0.171）；no_hs 持平、3b 更差（p=0.068）；无学习趋势。按预注册停止规则，任务时间尺度线到此为止 |
| 2026-10-22 | v0.14.0-phase4-normalized-readout | 归一化读出（v = 5.0·(up−down)/(up+down+1e-3)，7 条件 × 15 seeds × 600 s）。结果：K_eff 0.141→0.177（+26%），但 hit 0.169→0.167、rally 0.204→0.202；early/late 相关 0.652/0.887 ≈ 旧差值 0.659/0.862；static−random p=0.008、static−symmetric p=0.099；play_hs 显著更差。读出线停止 |
| 2026-10-22 | v0.15.0-phase5-spontaneous-activity | P0 背景自发活动（3 Hz，80 nS，独立 RNG；4 条件 × 15 seeds × 600 s）。校准：孤立细胞 3.1 Hz，闭环 quiet-rest 4.6 Hz。结果：3b 仍饱和（at w_max 0.40，w_diff −0.027）；static 0.189/hit 0.158（无噪声 0.204/0.169）；no_hs 梯度 0.809 但行为 0.162；symmetric 在噪声下不再冻结。按预注册 H4，噪声线停止 |
| 2026-10-23 | v0.16.0-phase5-local-credit | P1 局部信用（Miss 时按球侧给 Up/Down ±1；5 条件 × 15 seeds × 600 s）。修复一次对照污染：信用分配改由条件名选择，删除全局 `--local-credit` 开关，受影响首跑存档为 `phase5_local_credit_600_bug_globalflag/`。结果：`w_diff corr` 0.000→0.780（no_hs）/0.426（play_hs），首次形成正确 y 梯度，显著优于全局 3b（+0.069，p=0.014）；但 no_hs 行为 0.220 ≈ static 0.204（p=0.512），play_hs 0.164 更低，全时段稳态下仍饱和（0.40/0.42）。H1/H3 支持、H2 不支持、H4 触发，局部信用线停止 |
| 2026-10-23 | v0.17.0-phase5-dynamic-homeostasis | P2 动态稳态目标带（`[5, 30] Hz`，带内不缩放，仅 play 期；5 条件 × 15 seeds × 600 s）。结果：`3b` at w_max 0.34→0.14、impact corr 0.179→0.381，但全局 D 仍 0 梯度；`local_3b_dyn` `w_diff corr` 0.364→0.498、行为 0.196 ≈ static 0.204（p=0.643）、at w_max 仍 0.25/0.29；local_dyn 与 no_hs（0.220）无差异（p=0.334）。机制：300 ms 窗口率方差使 17 Hz 时常跌破 5 Hz 下界，仍触发上调。H1/H2 不支持、H3 支持、H4 未触发；按停止规则，动态带线停止 |
| 2026-10-23 | v0.18.0-phase5-stp | P3 短时程可塑性（TM：U=0.4、τ_rec=200 ms、τ_fac=1000 ms，仅感觉事件，电导除以 U；5 条件 × 15 seeds × 600 s，全部 no_hs）。结果：early 相关 0.569→0.699、early/late gap 0.171→0.118；`local_stp` impact corr 0.735→0.809、梯度 0.780→0.880，但 mean |diff| 2.25→1.36 Hz、命令减弱，行为 0.187 < 0.220（p=0.243），与 static_stp 0.177 无差异（p=0.638）。H1 支持、H2 不支持、H4 触发，时间维度线停止 |
| 2026-10-23 | v0.19.0-phase5-ten-cell | P4 10 细胞 E/I 前馈网络（4 S → 2 E + 2 I → 2 M；g_S→E=g_E→M=40 nS 按存活准则校准；5 条件 × 15 seeds × 600 s）。结果：S 7.6 Hz、E/I 14.4 Hz、play motor 12.5 Hz（H1 支持）；`net_static` 0.203 ≈ 2 细胞 static 0.204（p=0.990，H2 支持），但 impact corr 0.920→0.479；`net_local` 0.127（−0.076，p=0.005）、`net_global` 0.148（权重崩到 0.27）。H3 不支持、H4 触发，扩网络线停止；`w_diff corr` 在 2 通道下不适用 |
| 2026-10-23 | v0.20.0-phase5-pd-readout | P5 PD 读出（`v = Kp·Δr + Kp·τ_pred·dΔr/dt`，τ_pred=50 ms；4 条件 × 15 seeds × 600 s）。结果：`local_pd` 0.220 ≡ `local_no_hs` 0.220（p=0.998）；`static_pd` 0.210 vs 0.204（p=0.722）；impact corr 仅 +0.01、mean \|v\| 不变。H1/H2/H3 均不支持、H4 触发：τ_pred 只能补偿几十 ms，无法补偿 2 s 距离门控延迟；接口线停止 |
| 2026-10-23 | v0.21.0-phase6-temporal-coding | Phase 6a 帧式延迟编码开环验证（100 ms 帧、8 通道各 1 事件、延迟 0–100 ms ∝ \|ch−y\|、首脉冲延迟差读出；5 seeds × 60 s，球拍冻结）。结果：`corr(Δt, ball_y)` 均值 0.442（要求 >0.5），seed 范围 0.320–0.798；Δt P95 仅 4.0 ms；符号 5/5 一致；motor 率 20.8 Hz。Gate 不通过 → A 线关闭，未进入 6b；B/C 不再启动，项目转 negative-results 论文 |
| 2026-10-23 | v0.22.0-phase7-recurrent-ei | Phase 7a 递归 E-I 网络（用户明确要求覆盖 §6S 硬停止；4 S + 8 E + 8 I + 2 M；`w_se=20`、`w_ei=20`、`g_ie=10`、背景 3 Hz/80 nS 固定，`w_ee ∈ {0,5,10,20}` nS 校准；4 点 × 3 seeds × 60 s，静态权重）。结果：play 期 E 率 3.67 / 4.07 / 158.0 / 253.2 Hz，网格内**没有 5–25 Hz 工作点**；`w_ee=10` 起出现点火（两两相关 0.90、漂移 30%、单细胞 159 Hz）。网络为 ~4 Hz 背景态 ↔ >150 Hz 点火态的双稳态，G1/G3/G4 不通过。按硬停止：B 线永久关闭，不再调参或改拓扑 |
