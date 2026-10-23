# 工作交接文档（HANDOFF）

> **用途**：每次会话结束前更新；下一个 agent/协作者先读这一份，再读 README。
> **原则**：只写“现在是什么状态、下一步做什么、哪些坑不能踩”；不写长篇背景（背景在 README 和 docs）。

**最后更新**：2026-10-22  
**更新人**：Trae（Phase 0–4）

---

## 1. 当前状态快照

| 项目 | 状态 |
|---|---|
| 文献阅读 | 已完成：`reference/` 下全部核心 PDF + ModelDB 代码 + `history.txt` |
| 总体方案 | 已确定（见 README §3） |
| 目录骨架 | 已创建（`config/ docs/ src/ experiments/ tests/ runs/ checkpoints/ results/`） |
| 文档 | README、HANDOFF、协议/生物映射、参数政策、实验计划、文献笔记已写入 |
| 阶段 0 | **已完成**：`results/phase0/`，全部指标 PASS |
| 阶段 1 | **已完成（协议修复后重跑，120 s）**：静态闭环；full_feedback 0.19 ≈ random_paddle 0.19；诊断 R²=0.007（斜率 −0.22 Hz/bin） |
| 阶段 2 | **已完成**：STDP 窗口、资格迹 + 三因子、稳态缩放全部 PASS |
| 阶段 3 | **已完成（负结果；修复 rest 协议后重跑）**：3a/3b 与 static/random 无可靠差异；权重变化主要由稳态主导 |
| 阶段 4 | **已完成（2 细胞 + 3/4 细胞抑制版 + 慢球 + 归一化）**：600 s 下 push-pull 结构优势显著，但绝对命中率仅 0.17–0.19；三种抑制 motif 都无 motor 分化；慢球使 K_eff 0.141→0.094、hit 0.169→0.150；归一化使 K_eff 0.141→0.177，但 hit 0.169→0.167（行为不变）；可塑性在长会话中有害（3b −0.053/−0.083；no_hs T1→T2 0.19→0.11） |
| 阶段 5 P0 | **已完成（v0.15.0，负结果）**：3 Hz/80 nS 背景使 quiet-rest 达 4.6 Hz，但 3b 仍饱和（at w_max 0.40，w_diff −0.027）；static 0.189/hit 0.158；噪声线停止 |
| 阶段 5 P1 | **已完成（v0.16.0，梯度正结果 / 行为负结果）**：局部信用使 `w_diff corr` 0.000→0.780（no_hs）/0.426（play_hs），显著优于全局 3b（p=0.014）；但 no_hs 行为 0.220 ≈ static 0.204（p=0.512），play_hs 0.164 更差；全时段稳态下仍饱和（0.40/0.42）。按 H4 停止局部信用线 |
| 阶段 5 P2 | **已完成（v0.17.0，弱正结果 / 行为负结果）**：动态带 `[5,30] Hz`（仅 play）使 at w_max 0.34→0.14、impact corr 0.179→0.381，但全局 D 仍 0 梯度；局部 D + 动态带 `w_diff corr` 0.364→0.498、行为 0.196 ≈ static 0.204（p=0.643）。H1 不支持 → 动态带线停止 |
| 阶段 5 P3 | **已完成（v0.18.0，机制正结果 / 行为负结果）**：TM STP 把 early/late 信息差从 0.171 压到 0.118、early 相关 0.569→0.699，局部臂 impact corr 0.735→0.809、梯度 0.780→0.880；但 mean |diff| 2.25→1.36 Hz、命令减弱，行为 0.187 < 0.220（p=0.243）。H1 成立、H2 不支持 → 时间维度线停止 |
| 阶段 5 P4 | **已完成（v0.19.0，存活/结构正结果、学习负结果）**：10 细胞 E/I 网络存活（E/I 14.4 Hz、play motor 12.5 Hz），`net_static` 0.203 ≈ 2 细胞 static 0.204（p=0.990），但 impact corr 0.920→0.479；`net_local` 0.127（−0.076，p=0.005）、`net_global` 0.148（权重崩到 0.27）。H3 不支持 → 扩网络线停止 |
| 阶段 5 P5 | **已完成（v0.20.0，负结果）**：PD 读出（τ_pred=50 ms）对行为无影响：`local_pd` 0.220 ≡ `local_no_hs` 0.220（p=0.998），`static_pd` 0.210 vs 0.204（p=0.722）；impact corr 仅 +0.01。H1/H2 不支持 → 接口/PD 线停止 |
| 阶段 6a | **已完成（v0.21.0，Gate 不通过）**：帧式延迟编码（100 ms 帧、0–100 ms 延迟）的 `corr(Δt, ball_y)` 均值 0.442（<0.5），Δt P95 仅 4.0 ms；符号 5/5 一致、率 20.8 Hz 正常。按硬停止，A 线关闭，B/C 不再启动 |
| 阶段 7a | **已完成（v0.22.0，用户授权覆盖 §6S 硬停止；Gate 不通过）**：22 细胞递归 E-I（4S+8E+8I+2M）。`w_ee ∈ {0,5,10,20}` nS × 3 seeds × 60 s：E 率 3.67 / 4.07 / 158.0 / 253.2 Hz——网格内无 5–25 Hz 点；`w_ee=10` 起点火并同步化（两两相关 0.90、漂移 30%）。按 §6T 硬停止，**B 线永久关闭**，不再调参/改拓扑 |
| 依赖安装 | 已完成：`.venv`（Python 3.12）+ brian2 + numpy + matplotlib + pandas + pyyaml + numba |
| 仿真运行 | Phase 0/1/2/3/4/5P0–5P5/6a/7a 均已运行；结果在 `results/phase0/`…`results/phase4/`；敏感性/长会话/抑制版/慢球/归一化/噪声/局部信用/动态带/STP/10 细胞/PD/延迟编码/递归 E-I 在 `results/phase4_gain030/`、`phase4_gain060/`、`phase4_const_rate/`、`phase4_600/`、`phase4_const_rate_600/`、`phase4_inhibition_600/`、`phase4_cross_inhibition_600/`、`phase4_tuned_inhibition_600/`、`phase4_slow_ball_600/`、`phase4_norm_readout_600/`、`phase5_bg_noise_600/`、`phase5_local_credit_600/`、`phase5_dynamic_homeostasis_600/`、`phase5_stp_600/`、`phase5_ten_cell_600/`、`phase5_pd_readout_600/`、`phase6a_latency/`、`phase7_7a/`；汇总见 `results/phase4_gain_sensitivity.md`、`phase4_long_session.md`、`phase4_inhibition_report.md`、`phase4_cross_inhibition_report.md`、`phase4_tuned_inhibition_report.md`、`phase4_slow_ball_report.md`、`phase4_norm_readout_report.md`、`phase5_bg_noise_report.md`、`phase5_local_credit_report.md`、`phase5_dynamic_homeostasis_report.md`、`phase5_stp_report.md`、`phase5_ten_cell_report.md`、`phase5_pd_readout_report.md`、`phase6a_latency_validation_report.md`、`phase7a_rec_ei_gate_report.md` |
| 代码 | Phase 0/1/2/3/4 脚本 + `src/cell/hh_numba.py` + `src/plasticity/` + `src/loop/phase1/3/4_*.py` |

**一句话**：修复了一个让 Phase 1/3 永久锁在 rest 的协议 bug；Phase 4 的 push-pull 差分读出在 600 s 长会话中显示小而稳定的行为优势，但绝对命中率仍低（0.17–0.19）；Phase 5 依次关闭了背景噪声、局部信用（梯度成立但行为仅持平 static）、动态稳态带、STP（时间形状与信息改善但命令减半）、10 细胞 E/I（静态等价、学习更差）、PD 读出（无影响）；Phase 6a 的帧式延迟编码也未通过开环 Gate（corr 0.442 < 0.5）；Phase 7a 的 22 细胞递归 E-I 同样未过 Gate（允许的 `w_ee` 网格内没有 5–25 Hz 工作点，只有 4 Hz 与 158 Hz 两个状态）。**八条线合起来说明：在 2–22 细胞极小网络中，行为上限由读出结构、信息到达时刻与执行器增益决定；改可塑性、稳态、动力学、规模、接口、输入编码或递归拓扑都无法突破。**

**当前状态（2026-10-23）**：Phase 0–5、Phase 6a 与 Phase 7a 全部完成，按预注册全部停止；
项目结束，材料转 negative-results 论文。最终报告：`results/final_report.md`。

---

## 2. 已拍板的决定（不要再反复讨论）

| # | 决定 | 具体值 | 理由 |
|---|---|---|---|
| 1 | 平台 | Brian 2 2.10.1 + Python 3.12 venv | Python 3.14 无 NEURON wheel；Brian 2 纯 Python、易改方程 |
| 2 | 基础细胞 | Pospischil et al. 2008 RS，单房室 HH，ModelDB 123623 | 已发表、参数固定、能复现规则放电与适应 |
| 3 | 参数边界 | Tier 0 身份固定；Tier 1 校准后冻结；Tier 2 可塑状态变化 | 保证不是 ML 调参，同时保留学习自由度 |
| 4 | 单细胞读出 | 100 ms 窗口放电率，相对 20 Hz 参考 → 球拍速度 | DishBrain 两个 motor region + 20 Hz gain 的最小退化 |
| 5 | 单细胞主实验 | 三因子资格迹（STDP + 可预测性调制）为主；纯 STDP 为消融 | 全通道反馈会抹掉位置编码，单细胞需要信用分配 |
| 6 | 网络规模 | 先 2–5 个细胞；稳定后再考虑扩到 ~12 个 | 先回答“最小网络是否更好” |
| 7 | 断点续跑 | trial 级 checkpoint + run manifest + `--resume` | 支持 24 h 运行与关机恢复 |
| 8 | 统计 | 多种子、预注册指标、配对/混合效应、效应量、对照 | 防止挑 seed / 挑时间窗 |
| 9 | 成功标准 | 可复现、可解释、对照完整；不要求打赢 Pong | 探索性项目，负结果合法 |
| 10 | 平台优先级 | Brian 2 主；Arbor/Plastic Arbor 仅作阶段 5 形态扩展的可选分支 | 本项目需要自定义三因子规则与闭环；Plastic Arbor 的异突触优势依赖树突钙扩散，单房室用不上 |

---

## 3. 不能做的事（硬约束）

1. **禁止反向传播、全局损失、梯度下降调参、用 ML 模型拟合学习曲线。**
2. **禁止为了改善 Pong 成绩去改 Tier 0 身份参数。**
3. **禁止在看完结果后回头改 Tier 1 校准参数**；如必须改，记录原因并重跑所有条件。
4. **禁止用网格搜索“凑”出一条学习曲线**；参数变化必须有机制解释或作为预注册实验变量。
5. **禁止挑 seed、挑时间窗、挑指标**；预注册指标和排除标准。
6. **禁止把“可塑性规则是注入的”说成“从生物物理中涌现的”**；报告必须诚实说明。
7. **禁止用“sentience/意识”做过度声称**；论文里的 sentience 是“对感觉印象作出适应性反应”的形式定义。
8. **禁止在单细胞阶段没跑完时并行铺开网络阶段。**

---

## 4. 当前参数状态

> 实际运行参数在 `config/phase1.yaml`、`phase2.yaml`、`phase3.yaml`、`phase4.yaml` 中；
> `experiment_default.yaml` 仅保留最初的骨架/字段说明，不再作为运行入口。

| 层级 | 代表参数 | 当前状态 |
|---|---|---|
| Tier 0 身份 | \(C_m\)、门控方程、\(E_{Na/K/Ca}\)、基础 \(g_{\max}\) | 已填：Pospischil 2008 RS（ModelDB 123623），Phase 0 全部 PASS |
| Tier 1 接口 | 感觉突触电导、反馈增益、噪声、读出增益、目标放电率 | 已校准并冻结（Phase 1/3/4 使用同一组值）；增益/恒常率敏感性作为 v0.7.1/v0.8.0 独立版本记录 |
| Tier 2 可塑 | \(w_{ij}\)、\(e_{ij}\)、\(g_{\max}\) 缩放、\(V_{1/2}\)、受体池 | STDP / 资格迹 / 三因子 / 稳态已实现并验证；通道密度/受体池未实现 |
| Tier 3 实验 | 条件、种子、会话长度、T1/T2 | 已固定：7 条件 × 15 seeds；120 s 主版本 + 600 s 长会话（v0.9.0） |

**冻结规则**：Tier 1 一旦校准，写入 config 并记录来源/日期；阶段 3 开始后不再改。若必须改，视为新版本，所有条件重跑。

---

## 5. 目录与文件职责

```text
bbn/
├─ README.md                  # 项目概况、设计决策、路线图
├─ HANDOFF.md                 # 本文：状态、下一步、交接
├─ config/
│  └─ experiment_default.yaml # 唯一参数入口（Tier 0/1/2/3）
├─ docs/
│  ├─ protocol_and_biology.md # 协议参数、模型映射、生物对应、简化说明
│  ├─ parameter_policy.md     # 参数分层、更新规则、边界、反 ML 规则
│  ├─ experiment_plan.md      # 阶段任务、对照、指标、统计、checkpoint
│  └─ literature_notes.md     # 文献笔记与待补文献
├─ src/
│  ├─ cell/                   # 待实现：HH 细胞、通道、突触
│  ├─ plasticity/             # 待实现：STDP、资格迹、稳态、内在可塑性、受体池
│  ├─ env/                    # 待实现：Pong 环境
│  ├─ loop/                   # 待实现：闭环控制器、刺激调度
│  ├─ io/                     # 待实现：config、manifest、checkpoint、日志
│  └─ metrics/                # 待实现：指标计算与导出
├─ experiments/               # 待实现：phase0_baseline.py 等
├─ tests/                     # 待实现：STDP 窗口、f-I、稳态收敛的验证
├─ runs/                      # 运行产物：<run_id>/manifest.json、run.log、checkpoint.npz
├─ checkpoints/               # 可选：集中式断点
├─ results/                   # 汇总图、表、报告
└─ reference/                 # 已有文献，不要改动
```

---

## 6. 阶段 0：基线细胞（已完成）

> 阶段 0 只做基线电生理，不训练、不涉及 Pong、不涉及可塑性。

### 6.1 环境（已完成）

1. 项目下已有 `.venv`（Python 3.12），并已安装：
   ```powershell
   brian2==2.10.1 numpy matplotlib pandas pyyaml
   ```
   如果换机器，重建命令：
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install brian2 numpy matplotlib pandas pyyaml --index-url https://pypi.tuna.tsinghua.edu.cn/simple
   ```
2. 已做 smoke test（`config/cell_pospischil_rs_smoke.yaml`），确认 import、run、monitor、绘图正常。
3. `codegen_target` 目前是 `numpy`；不需要 C 编译器。若以后要提速，再装 MSVC Build Tools 启用 Cython。

### 6.2 基础细胞（已实现）

1. 参数来源：Pospischil et al. 2008 Fig.1 caption + ModelDB 123623 `sPY_template`。
2. 实现：`experiments/phase0_baseline.py`（单文件，Phase 0 先不拆 `src/cell/`；Phase 1 再重构）。
3. 验证项：静息膜电位、输入电阻、f-I、单 spike 波形、ISI 适应、rheobase、速度基准。
4. 输出：`results/phase0/`。

### 6.3 阶段 0 验收标准

- 静息电位 −75…−65 mV；
- 输入电阻 25…45 MΩ；
- rheobase 0.1…0.8 nA；
- spike 幅度 > 50 mV；
- spike 半宽 0.3…3.0 ms；
- ISI ratio > 1（有适应）；
- 0.8 nA 放电率 1…100 Hz；
- 无数值爆炸。

### 6.4 阶段 0 交付物

- `experiments/phase0_baseline.py`
- `config/cell_pospischil_rs.yaml`
- `config/cell_pospischil_rs_smoke.yaml`
- `experiments/README.md`（运行说明）
- `results/phase0/phase0_report.md` + `phase0_summary.json` + 4 张图

### 6.5 Phase 0 结果摘要（正式运行）

| 指标 | 结果 | 判定 |
|---|---:|---|
| 静息电位 | −70.57 mV | PASS |
| 输入电阻 | 32.35 MΩ（论文 34.5） | PASS |
| Rheobase | 0.675 nA | PASS（偏高） |
| Spike 峰值 / 幅度 | +47.6 / 118.1 mV | PASS |
| Spike 半宽 | 0.65 ms | PASS |
| ISI ratio | 4.03（23.8 → 96.1 ms） | PASS |
| 0.8 nA 放电率 | 10 Hz | PASS |
| 1.0 nA 放电率 | 26.7 Hz | PASS |
| 速度 | 25.2 s 墙钟 / s 仿真 | 需优化 |

**判定**：模型是稳定的规则放电 RS 细胞，V_rest、Rin、spike 形状、适应都在合理范围。  
**已知偏差**：rheobase 0.675 nA 比论文 Fig.1D 的约 0.2 nA 高；可能来自 E_K=−100（论文正文 −90）、V_T=−55（拟合均值约 −61.5）、gM/τmax 选择。当前先冻结，Phase 1 若感觉输入校准困难再做对照。  
**工程问题**：numpy target 约 25× 慢于实时；Phase 1 之前需要优化（MSVC+Cython、查找表、或降低 dt）。

### 6.6 当前下一步

1. 决定是否先做 Phase 0b：E_K=−90 / V_T=−61.5 对照（可选，不阻塞）。
2. 解决速度：已用 Numba 引擎解决（见 §6A）。
3. 进入阶段 1：已完成（见 §6A）。

---

## 6A. 阶段 1：Pong + 静态闭环（已完成）

### 6A.1 实现

- `src/cell/hh_numba.py`：Numba 加速的同一组 HH 方程；Brian 2 版本保留为参考。
- `src/env/pong.py`：简化 Pong 环境。
- `src/loop/phase1_loop.py`：8 通道感觉编码、运动读出、四种反馈。
- `experiments/phase1_static_loop.py`：6 种条件 × 3 seeds × 120 s。
- `experiments/phase1_diagnostic.py`：检查单细胞率是否携带 ball_y 信息。
- `config/phase1.yaml`：Tier 0 + Phase 1 Tier 1 参数。

### 6A.2 静态基线结果（协议修复后重跑，120 s × 3 seeds）

| 条件 | 平均 rally | hits | misses | 平均放电率 |
|---|---:|---:|---:|---:|
| full_feedback | 0.19 | 2.3 | 12.0 | 18.0 Hz |
| no_feedback | 0.09 | 4.7 | 55.3 | 21.3 Hz |
| silent | 0.19 | 3.7 | 19.3 | 8.2 Hz |
| random_paddle | 0.19 | 9.7 | 50.3 | 20.5 Hz |
| always_up | 0.05 | 3.0 | 57.0 | 21.3 Hz |
| always_down | 0.06 | 3.3 | 56.7 | 21.3 Hz |

> 带 timeout 的条件（full_feedback / silent）只有 ~12–19 个 rally；no_feedback/random/always_* 没有 rest，约 60 个。跨条件比较 rally 时注意采样差异。

**判定**：闭环工作，但静态单细胞与随机球拍持平（0.19 vs 0.19），没有优于随机。  
**诊断**：43 个 rally，`mean_rate ~ ball_y` 的 R² = 0.007，斜率 −0.22 Hz/bin（r = −0.086）；单细胞率几乎不携带可用的 ball_y 信息，且方向相反。  
**结论**：这是单细胞标量率读出的结构性限制。率主要被 ball_x（距离）和反馈刺激驱动。阶段 3 把它作为负结果的一部分；阶段 4 用两池差分读出消除共同驱动。旧 60 s 数值（full 0.245、R²=0.002）来自 rest 锁死 bug，已作废。

### 6A.3 速度

Numba 引擎：800 ms 仿真约 0.3 s（含首次编译）；比 Brian 2 numpy target 快约 60–80 倍。Phase 1 的 18 个 120 s run 在分钟级完成。

### 6A.4 当前下一步

1. 阶段 2：已完成（见 §6B）。
2. 阶段 3：已完成（见 §6C）。
3. 阶段 4：已完成（见 §6D）。

---

## 6B. 阶段 2：可塑性规则验证（已完成）

### 6B.1 实现

- `src/plasticity/stdp.py`：pair-based STDP + 资格迹/三因子。
- `src/plasticity/homeostasis.py`：Turrigiano 乘性缩放。
- `experiments/phase2_stdp_window.py`：Δt ∈ [−50, 50] ms 窗口。
- `experiments/phase2_eligibility.py`：0–5 s 延迟奖励。
- `experiments/phase2_homeostasis.py`：高/低驱动收敛到 20 Hz。
- `config/phase2.yaml`：规则参数。

### 6B.2 结果

| 验证 | 结果 | 判定 |
|---|---|---|
| STDP 窗口 | 峰值 LTP 0.00951，峰值 LTD −0.01141；与理论误差 5.5e−17 | PASS |
| 资格迹延迟奖励 | D=+1 正、D=−1 负；0→5 s 单调衰减；未配对通道 0 | PASS |
| 稳态缩放 | 高/低起始都收敛到 20.0 Hz；驱动稳定在 ~39.8 nS | PASS |

输出：`results/phase2/stdp_report.md`、`eligibility_report.md`、`homeostasis_report.md` + 图。

### 6B.3 关键限制

- 这些是**规则层验证**，还没有和 HH 细胞/闭环整合。Phase 3 需要把 pre/post 脉冲的精确时间接入细胞引擎；当前 Phase 1 的突触事件是按 10 ms tick 汇总的。
- η=1.0 仅为让验证曲线可见；Phase 3 要重新设定生物合理的学习率。
- 单细胞读出在 Phase 1 诊断中几乎不携带 ball_y；Phase 3 的负结果应在预期之内。

### 6B.4 当前下一步

阶段 3：已完成（见 §6C）。

---

## 6C. 阶段 3：单细胞闭环学习（已完成，负结果）

### 6C.1 实现

- `src/cell/hh_numba.py`：新增 `run_events`，支持 10 ms block 内的精确突触事件时间与 post spike 时间。
- `src/loop/phase3_loop.py`：STDP / 资格迹 / 三因子 / 稳态接入闭环。
- `experiments/phase3_single_cell.py`：11 条件 × 15 seeds × 120 s。
- `config/phase3.yaml`：可塑参数（η=1.0 的强学习率，给机制公平机会）。

### 6C.2 关键结果（协议修复后重跑，15 seeds × 120 s）

> 带 timeout 的条件（3a/3b full、no_hs、silent、static、always_*）每 120 s 只有 ~12–13 个 rally；
> no_feedback / shuffled 没有 rest，60 个 rally。跨条件比较 rally 时必须注意采样差异。

| 条件 | 平均 rally | 平均率 | w init→final | |Δw| | y corr init→final |
|---|---:|---:|---:|---:|---:|
| phase3a_full | 0.089 | 21.5 Hz | 1.00→1.465 | 0.462 | −0.038→−0.018 |
| phase3a_full_no_hs | 0.094 | 20.3 Hz | 1.00→1.416 | 0.414 | −0.038→+0.074 |
| phase3b_full | 0.089 | 21.3 Hz | 1.00→1.444 | 0.442 | −0.038→+0.083 |
| phase3b_full_no_hs | 0.167 | 17.3 Hz | 1.00→0.766 | 0.241 | −0.038→−0.343 |
| phase3b_no_feedback | 0.171 | 18.1 Hz | 1.00→0.875 | 0.129 | −0.038→−0.038 |
| phase3b_shuffled | 0.179 | 18.5 Hz | 1.00→0.886 | 0.126 | −0.038→−0.065 |
| phase3b_silent | 0.050 | 13.6 Hz | 1.00→1.486 | 0.484 | −0.038→0.000 |
| static_full | 0.178 | 18.0 Hz | 1.00→1.00 | 0.000 | −0.038→−0.038 |
| random_paddle | 0.161 | 21.7 Hz | 1.00→1.00 | 0.000 | −0.038→−0.038 |

### 6C.3 判定

- **没有学习效应**：3a/3b full 的 rally（0.089）低于 static_full（0.178），不是“接近”；但两者都只有 ~12 个 rally，不能用它证明损伤，只能说明没有改善。
- **稳态主导权重变化**：3a/3b full 的 |Δw| ~0.44–0.46，权重顶到 w_max 附近（1.44–1.47）。机制：rest 期细胞沉默 → 稳态每秒上调 ~1.16× → 饱和；与 Phase 4 完全一致。关闭稳态后 |Δw| 降到 0.24，但 STDP 学到的 y 梯度方向是**错的**（−0.343：高 y 通道被削弱）。
- **没有可用的 y 梯度**：full 条件下通道-权重相关接近 0（−0.02…+0.08）；no_hs 变成 −0.343，方向错误。
- **结论**：可塑性规则本身工作（Phase 2 PASS），但单细胞标量率不携带可用的 ball_y 信息（Phase 1 诊断 R² = 0.007，斜率 −0.22 Hz/bin）；单一全局标量 D(t) 无法给不同通道分配信用；稳态在 rest 切换中主导权重。负结果成立，不通过调参美化。

### 6C.4 当前下一步

阶段 4 已完成，见 §6D。旧 §6C 的数值（0.16–0.18、R²=0.002）来自 rest 锁死 bug，已作废。

---

## 6D. 阶段 4：两池差分读出（已完成，2 细胞）

### 6D.1 实现

- `src/loop/phase4_loop.py`：up/down 两个 Pospischil RS 细胞。两池接收**同一组**感觉事件时间与同一套反馈刺激，各自持有独立的 STDP/资格迹权重和稳态缩放器。
- 读出：`v = clip(velocity_gain · (rate_up − rate_down), ±max_velocity)`；共同的距离/反馈驱动在差分中抵消。
- `experiments/phase4_network.py`：7 条件 × 15 seeds × 120 s；支持 `--jobs` 多进程；输出 traces/impacts/weights CSV + 汇总 + 图 + 报告。
  > 注意：重跑会覆盖 `phase4_report.md` 中的人工解释；若只想重算数据，请用新的 `--outdir`。
- `config/phase4.yaml`：Tier 0/1 与 Phase 1/3 一致；Tier 2 与 Phase 3 一致；新增 `pushpull_span=0.2`、`random_init_jitter=0.2`。
- 条件：
  - `phase4_pushpull_3b`：反对称初始权重 + 三因子 + 稳态（全程，含 rest）
  - `phase4_pushpull_3b_no_hs`：同上，关闭稳态
  - `phase4_pushpull_3b_play_hs`：同上，仅在对局期施加稳态（机制对照）
  - `phase4_pushpull_static`：反对称初始权重，无可塑性（**学习效应的主对照**）
  - `phase4_random_3b`：独立随机初始权重 + 三因子 + 稳态
  - `phase4_symmetric_static`：两池权重完全相同（差分恒 0 对照）
  - `phase4_random_paddle`：忽略细胞输出

### 6D.2 关键结果（15 seeds × 120 s，机制筛查）

> **行为结论以 §6G.1 的 600 s 长会话为准**；本表用于读出/权重机制的筛查，不作为最终行为证据。

| 条件 | avg rally | hits | misses | impact corr(diff, y) | 读出斜率 | 有效 K | w_diff corr init→final |
|---|---:|---:|---:|---:|---:|---:|---:|
| pushpull_static | 0.214 ± 0.130 | 2.5 | 11.9 | +0.926 ± 0.038 | +4.76 Hz/bin | 0.20 /s | +1.00→+1.00 |
| pushpull_3b_no_hs | 0.280 ± 0.138 | 3.3 | 11.7 | +0.919 ± 0.038 | +4.39 Hz/bin | 0.20 /s | +1.00→+0.977 |
| pushpull_3b_play_hs | 0.244 ± 0.150 | 2.9 | 11.8 | +0.586 ± 0.150 | +1.94 Hz/bin | 0.12 /s | +1.00→+0.030 |
| pushpull_3b | 0.200 ± 0.117 | 2.4 | 11.9 | +0.395 ± 0.100 | +0.77 Hz/bin | 0.07 /s | +1.00→0.000 |
| random_3b | 0.169 ± 0.120 | 2.0 | 11.9 | +0.011 ± 0.254 | +0.01 Hz/bin | 0.00 /s | −0.13→0.000 |
| random_paddle | 0.141 ± 0.155 | 1.7 | 11.9 | −0.237 ± 0.428（采样噪声） | — | — | — |
| symmetric_static | 0.106 ± 0.097 | 1.3 | 12.0 | 0（差分恒 0） | 0 | 0 | 0 |

两组置换检验（条件不共享 RNG 流，不能按 seed 配对；n=15/组，2 万次标签打乱）：
- static − symmetric：+0.108，p = 0.018
- static − random paddle：+0.072，p = 0.181
- no_hs − static：+0.066，p = 0.202
- play_hs − static：+0.031，p = 0.559
- 3b − static：−0.014，p = 0.771
- random_3b − random paddle：+0.028，p = 0.627

### 6D.3 判定

1. **差分读出成立（正结果）**：push-pull static 的冲击前差分率与 ball_y 的 r = 0.919，斜率 4.76 Hz/bin；up/down 池分别对 ball_y 呈 +0.46 / −0.50 的相反调谐。单细胞只有 R² = 0.007 且符号错误。**Position information 已从“没有”变成“可读”。**
2. **行为瓶颈不是简单的标量增益**：预注册的 gain 敏感性（0.15/0.30/0.60）显示 rally 0.214→0.201→0.246（非单调），hit 0.168→0.151→0.180；impact error 虽单调下降（1.84→1.64→1.32），但 K_eff 始终 ≈0.20/s。机制是感觉率随 ball_x 从 4 Hz 升到 40 Hz，控制信息集中在回合末端；提高 gain 只放大末端响应。详见 `results/phase4_gain_sensitivity.md` 与 §6E.1。
3. **可塑性没有可靠增益**：120 s 下 3b/play_hs/no_hs 相对 static 的差异都不显著；但 600 s 长会话中 3b 显著更差（−0.053/−0.083，p=0.013/0.002），no_hs 在 const 显著更差（−0.057，p=0.027），且 T1→T2 从 0.19 降到 0.11（p=0.0001）。**长会话里可塑性是有害的，不只是无效。** random_3b 始终没有学到位置映射（r≈0.01）。全局标量 D(t) 对两个池是同一个信号，信用分配问题未解决。
4. **稳态抹掉差分结构**：完整稳态下两池权重最终逐通道完全相同（mean |w_up−w_down| = 0.000，17% 权重在 w_max），读出斜率从 4.76 降到 0.77。机制是 rest 期细胞沉默 → 1 s 一次的稳态缩放以约 1.16×/s 上调 → 两池同时饱和；对局期的独立归一化进一步压缩增益差。`play_hs` 只是部分缓解（corr 0.030）。
5. **协议 bug（已修复）**：旧循环在 rest 期间只冻结球拍、球继续前进，导致第一次 miss 后每次 2 s 的 miss 都重置 rest，永久锁死。Phase 1/3 已全部重跑；旧数值作废。
6. **与单细胞对比**：Phase 3 `static_full` 是 0.178（~12 rallies/seed），Phase 4 600 s `pushpull_static` 是 0.204（~60 rallies/seed）；数值略高，但协议/读出不同，不能直接归因于“多细胞”。真正的结构证据是同协议内 600 s 的 static vs symmetric（+0.042，p=0.016）。两池仍几乎完全共活动（排他率 ≤ 2.2%，率相关 ≥ 0.977），没有 motor 分化。

### 6D.4 下一步（截至 2026-10-21：已停止新实验）

1. **Tier 1 增益敏感性：已完成（负结果）**，见 §6E.1。不再追加 gain 剂量点。
2. **恒常率（时间形状）：已完成（无额外行为收益）**，见 §6F.1；600 s 长会话进一步确认，见 §6G.1。按预注册停止规则，放弃感觉率门控这条线。
3. **600 s 长会话：已完成（结构优势显著但小；可塑性有害）**，见 §6G.1。
4. **背景噪声 1–5 Hz**：候选，未开始（可缓解 rest 期稳态饱和）。
5. **3–5 细胞 + 抑制性中间神经元**：候选，未开始（测 motor 分化/排他性）。
6. **不要动 Tier 0**；不要用网格搜索找“能学会”的增益或率值。

---

## 6E. Tier 1 增益敏感性（预注册，2026-10-21）

**动机**：Phase 4 的闭环比增益只有 K ≈ 0.20 /s，2 s 回合只能修正约 1/3 的初始误差。
若行为上限确实由执行器决定，则提高 `velocity_gain` 应产生单调的行为改善；若仍无改善，
说明还有读出/时序/策略层面的限制。

**唯一改动**：Tier 1 `velocity_gain` 0.15 → 0.30 与 0.60 bins/s/Hz（两个预注册剂量点）。
其余 Tier 0/1/2 参数、7 个条件、15 seeds、120 s、协议全部冻结。作为新版本
（v0.7.1-phase4-gain-sensitivity），不与 v0.7.0 主结果混比。

**预注册假设**：
- H1：`pushpull_static` 的平均 rally 与命中率随 gain 单调上升。
- H2：`symmetric_static` 在所有 gain 下保持 ~0.1（差分恒 0，乘以任何 gain 都是 0）。
- H3：若可塑性的收益被执行器瓶颈掩盖，`3b`/`no_hs` 在 0.30/0.60 下应超过同 gain 的 static；
  若仍无差异，则“无可塑性学习”不是增益不足造成的。
- H4：稳态仍会使两池权重饱和趋同（w 顶到 w_max），与 gain 无关。

**分析**：每个 gain 单独出报告；同 gain 内按 seed 配对检验；跨 gain 只做描述性比较。
不因结果改 gain、不加第三个剂量点、不挑 seed。

### 6E.1 结果（已完成：H1/H3 被否定，H2/H4 成立）

完整报告：`results/phase4_gain_sensitivity.md`；数据目录 `results/phase4_gain030/`、`results/phase4_gain060/`。

| condition | gain | avg rally | hit rate | impact error | play |v| | K_eff (/s) |
|---|---:|---:|---:|---:|---:|---:|
| pushpull_static | 0.15 | 0.214 | 0.168 | 1.844 | 0.179 | 0.197 |
| pushpull_static | 0.30 | 0.201 | 0.151 | 1.636 | 0.349 | 0.196 |
| pushpull_static | 0.60 | 0.246 | 0.180 | 1.319 | 0.595 | 0.199 |
| pushpull_3b_no_hs | 0.15 | 0.280 | 0.212 | 1.789 | 0.175 | 0.198 |
| pushpull_3b_no_hs | 0.30 | 0.204 | 0.157 | 1.606 | 0.329 | 0.204 |
| pushpull_3b_no_hs | 0.60 | 0.237 | 0.175 | 1.401 | 0.518 | 0.154 |
| pushpull_3b | 0.15 | 0.200 | 0.160 | 2.280 | 0.035 | 0.067 |
| pushpull_3b | 0.30 | 0.154 | 0.120 | 2.471 | 0.059 | 0.095 |
| pushpull_3b | 0.60 | 0.094 | 0.082 | 2.525 | 0.078 | 0.114 |
| random_paddle | 0.15 | 0.141 | 0.111 | 2.843 | 0.092 | −0.039 |
| random_paddle | 0.30 | 0.106 | 0.090 | 3.037 | 0.158 | −0.055 |
| random_paddle | 0.60 | 0.094 | 0.080 | 3.096 | 0.282 | −0.126 |
| symmetric_static | 0.15/0.30/0.60 | 0.106 | 0.089 | 1.915 | 0 | 0 |

- **H1 不支持**：static 的 rally 0.214→0.201→0.246（非单调）；hit rate 0.168→0.151→0.180。impact error 单调下降（1.84→1.64→1.32），但没有转成命中率。
- **H2 支持**：symmetric 在三个 gain 下完全相同的 0.1056。
- **H3 不支持**：no_hs 与 static 持平（0.30：+0.003，p=0.974；0.60：−0.010，p=0.897）；3b 在 0.60 下显著更差（−0.152，p=0.010）。
- **H4 支持**：3b 的 `frac at w_max` 0.175→0.275→0.325，`mean|w_up−w_down|`=0.000，读出斜率约 0.77；play_hs 梯度相关 −0.056/−0.077。
- 机制：K_eff 不随 gain 缩放（≈0.20/s），因为差分率被 ball_x 门控（4→40 Hz），控制信息集中在回合末端；提高增益只放大末端响应（play |v| 0.18→0.60），不能把信息提前。高 gain 还放大随机策略的伤害（random 0.141→0.094），所以 static−random 的对比在 0.60 下才显著（+0.152，p=0.009）。
- **结论**：行为瓶颈不是可调标量增益，而是读出信号的时间形状（距离门控 + 300 ms 窗口 + 2 s 回合 + 0.5 bins 容差）。不再追加 gain 剂量点；可塑性在三个 gain 下都无收益。

---

## 6F. 恒常感觉率实验（预注册，2026-10-21）

**动机**：v0.7.1 证明提高 `velocity_gain` 不改善行为；机制指向“位置信息到达太晚”。
当前感觉率因子随球接近从 4 Hz 升到 40 Hz，差分段在回合早期很弱、末端最强。
若时间形状假设成立，去掉距离门控（整段回合都用恒定率）应让差分读出在早期就可用，
从而提高闭环增益与命中率。

**唯一改动**：Tier 1 感觉率范围 `rate_min_hz = rate_max_hz = 20.0` Hz（恒定率）。
其余全部冻结：`velocity_gain=0.15`、7 个条件、15 seeds、120 s、rest 协议、Tier 0/2 参数。
新版本 v0.8.0-phase4-constant-rate，不与 v0.7.0/v0.7.1 混比。

**预注册假设**：
- H1：`pushpull_static` 的 hit rate / rally 高于 v0.7.0（0.168 / 0.214）；impact error 下降；
  K_eff 从 ≈0.20/s 上升（位置信息在早期可用）。
- H2：`symmetric_static` 仍为 ~0.1（差分恒 0）。
- H3：若时间形状是唯一被掩盖的瓶颈，可塑性的收益应出现；具体检验 `no_hs`/`3b` > static。
  若仍无差异，则信用分配的负结果与时间形状无关。
- H4：稳态仍会把两池权重饱和趋同，与感觉率是否恒定无关。

**次要观察**：恒定 20 Hz 会提高回合早期的总感觉驱动（原为 4 Hz），可能改变平均率、
适应与稳态负担；报告 mean rate、w at max、readout slope，不据此调参。
**分析**：与 v0.7.0 只做描述性比较（不同协议）；同协议内使用两组置换检验（各条件 RNG 流不共享）；不因结果改率值。

### 6F.1 结果（已完成：信号层面部分支持，行为层面不确定）

完整报告：`results/phase4_const_rate/phase4_report.md`。

| condition | avg rally | hit rate | impact error | K_eff (/s) | impact corr |
|---|---:|---:|---:|---:|---:|
| pushpull_static | 0.244 | 0.180 | 1.726 | 0.251 | +0.857 |
| pushpull_3b_no_hs | 0.249 | 0.185 | 1.896 | 0.232 | +0.844 |
| pushpull_3b | 0.217 | 0.165 | 2.028 | 0.082 | +0.389 |
| pushpull_3b_play_hs | 0.278 | 0.209 | 2.094 | 0.124 | +0.565 |
| random_3b | 0.172 | 0.133 | 2.082 | — | −0.093 |
| random_paddle | 0.119 | 0.094 | 2.720 | −0.029 | −0.175 |
| symmetric_static | 0.219 | 0.171 | 1.697 | 0 | 0 |

- **信号层面（部分支持 H1）**：early（ball_x>0.5）差分率–ball_y 相关 0.659→0.769，mean |diff| 3.09→4.90 Hz；K_eff 0.197→0.251；impact error 1.844→1.726。但末端率因子从 40 降到 20 Hz，冲击前斜率 4.76→2.75 Hz/bin，late |diff| 6.82→5.53——这是用末端信噪比换早期信噪比。
- **行为层面（H1 不成立）**：static 0.214→0.244、hit 0.168→0.180；但 frozen-paddle 对照 0.106→0.219、hit 0.089→0.171（理论 1/7≈0.143）。static−symmetric = +0.025（p=0.696）；对照漂移 ~0.11 大于 static 的变化 ~0.03。
- **H2 不成立**：symmetric 没有保持 ~0.1，而是 0.219；这是有限样本噪声的量化，不是机制变化。
- **H3 不支持**：no_hs 0.249 ≈ static 0.244（p=0.954）；3b 0.217（p=0.686）；play_hs 0.278（p=0.566）；random_3b 的 impact corr = −0.093，没有学到映射。
- **H4 支持**：3b 的 `frac at w_max` = 0.308，`mean|w_up−w_down|` = 0.000，读出斜率约 0.77；play_hs 梯度相关 ≈ 0.000。
- **结论**：20/20 Hz 恒定率不是足够的修复；它把信号从末端搬到早期，但没有同时保住末端增益，行为效应被噪声淹没。跨版本行为差异 <0.1 不可解释。不因结果改率值。

---

## 6G. 长会话（600 s）行为功效实验（预注册，2026-10-21）

**动机**：v0.8.0 的行为比较被 ~14 rallies/seed 的噪声主导（frozen-paddle 对照的 hit rate
在不同协议间从 0.089 漂到 0.171）。在继续改读出之前，先把行为功效提上来。

**唯一改动**：Tier 3 会话时长 120 → 600 s。两个臂：
1. 主协议（距离门控 4–40 Hz，gain 0.15）；
2. 恒常率（20/20 Hz，gain 0.15）。
其余全部冻结：7 条件、15 seeds、Tier 0/1/2 参数、rest 协议。
trace CSV 10× 降采样（100 ms），metrics 仍用全量 10 ms tick。新版本 v0.9.0-phase4-long-session。

**预注册假设**：
- H1（功效 sanity）：~60 rallies/seed 后，frozen-paddle 对照的 hit rate 应收敛到理论值
  1/7 ≈ 0.143；两臂之间 symmetric 的差异应显著小于 v0.8.0 的 0.11。
- H2：若恒定率的信号优势能转化为行为，`const static` 的 rally/hit 应高于 `dist static`，
  且差异大于新的噪声地板；K_eff 的差异（0.197 vs 0.251）应保持。
- H3：可塑性仍无收益——`no_hs` ≈ `static`，`3b` ≤ `static`，`random_3b` 仍无位置映射。
- H4：稳态饱和持续/加重（更长会话 → 更多 rest 期上调，w 顶到 w_max）。

**分析**：每个臂内用两组置换检验；跨臂仍只做描述性比较（RNG 流不共享）。
额外报告 symmetric 的 hit rate 95% 区间，作为行为噪声的校准。
**停止规则**：若 const 与 dist 的差异小于噪声地板或方向不一致，放弃“感觉率门控”这条线，
不再调率值；转向背景噪声或更长回合/更慢球。

### 6G.1 结果（已完成：结构优势成立，恒定率放弃，可塑性有害）

完整报告：`results/phase4_long_session.md`；两臂数据：`results/phase4_600/`、`results/phase4_const_rate_600/`。

| condition | dist rally | const rally | dist hit | const hit |
|---|---:|---:|---:|---:|
| pushpull_static | **0.204** | **0.236** | **0.169** | **0.188** |
| pushpull_3b_no_hs | 0.178 | 0.179 | 0.150 | 0.150 |
| pushpull_3b_play_hs | 0.165 | 0.176 | 0.139 | 0.147 |
| pushpull_3b | 0.151 | 0.153 | 0.129 | 0.131 |
| random_3b | 0.168 | 0.150 | 0.142 | 0.129 |
| random_paddle | 0.125 | 0.125 | 0.109 | 0.109 |
| symmetric_static | 0.162 | 0.180 | 0.138 | 0.152 |

- **H1 支持（功效 sanity）**：symmetric 的 hit 为 0.138/0.152（理论 1/7≈0.143，n≈1019/1031）；
  600 s 把行为噪声地板从 ~0.1 降到 ~0.02。
- **H2 不支持（恒定率）**：const static 仅比 dist static 高 +0.031（p=0.183）；两臂的
  static−symmetric 优势相近（+0.042/0.056，p=0.016/0.018）。按预注册停止规则，放弃感觉率门控这条线。
- **H3 支持且更强（可塑性有害）**：3b 两臂都显著低于 static（−0.053/−0.083，p=0.013/0.002）；
  no_hs 在 const 显著更低（−0.057，p=0.027），dist 方向相同但不显著（−0.026，p=0.125）；
  play_hs 也更低（−0.040/−0.059，p=0.052/0.037）。
  T1→T2：static 稳定（0.164→0.175 / 0.197→0.183），而 **no_hs 显著下降**
  （0.190→0.109，p=0.0001；0.186→0.114，p=0.0009）——STDP 在无稳态约束下把 push-pull 读出漂移坏。
- **H4 支持（稳态饱和）**：3b 的 `w_diff corr = 0.000`，`at w_max` 0.34/0.33，impact corr 只剩 0.18。
- **结构正结果**：600 s 下 static 比 symmetric 高 0.042–0.056（p=0.016/0.018）、
  比 random paddle 高 0.079–0.111（p=0.0002/0.0001）。这是目前最强的行为层证据，
  但绝对水平仍低（hit 0.17–0.19，rally 0.20–0.24）。
- **结论**：push-pull 读出结构真实有效但增益很小；恒定率不是修复；可塑性在长会话中有害而非无效；
  下一步应改任务/执行器时间尺度或引入早期预测，不再调 gain/率值。

**当前决定（2026-10-21）**：先到此为止，不再跑新实验。保留的候选方向见 §9。
不做的事：不再调 gain/率值，不用网格搜索找“能学会”的参数，不动 Tier 0。
（2026-10-22 已继续 3 细胞抑制版，见 §6H。）

---

## 6H. 3 细胞抑制版（预注册，2026-10-22）

**动机**：2 细胞 push-pull 在 600 s 下结构优势显著，但两池几乎完全共活动
（排他率 ≤ 2.2%，率相关 ≥ 0.977），没有 motor 分化。加入抑制性中间神经元是
计划中的下一步（experiment_plan 阶段 4 任务 1）。

**架构改动（v0.10.0-phase4-inhibition）**：
- 新增 1 个抑制性中间神经元 I（同一 Pospischil RS Tier 0 细胞）。
- I 接收与 motor 池**相同**的 8 通道感觉事件（均匀权重 \(1.0\times 40\) nS）与同一套反馈刺激；
  其权重**静态**（本版本不做 STDP/稳态）。
- I 的每个 spike 向 up/down 两池各投递一次抑制性电导 \(\bar g_{\text{inh}}\)，
  \(E_{\text{inh}}=-80\) mV、\(\tau_{\text{inh}}=10\) ms。
- 读出、运动池可塑性、稳态、条件、seeds、600 s 全部不变。
- 引擎改动：`FastHH` 新增标量 `g_inh`（默认 0）、`E_inh`、`tau_inh`。
  **关闭抑制时（g_inh=0）必须与现有 Phase 1/3/4 结果逐位一致**；主运行前做回归验证。

**Tier 归类**：\(E_{inh}\) 为 Tier 0（固定）；\(\bar g_{inh}\)、\(\tau_{inh}\) 为 Tier 1（校准后冻结）。
已写入 `docs/parameter_policy.md` 的参数总表与变更日志。

**校准规则（只看放电率，不看行为）**：
- \(\bar g_{inh}\in\{5,10,20\}\) nS，1 seed × 60 s；
- 选择使 motor 平均率与 I 平均率都落在 5–40 Hz 的中间值；
- 校准结果写入 HANDOFF，冻结后再跑主实验；若没有值满足，则取最接近区间的值并记录。

**条件与设计**：7 条件 × 15 seeds × 600 s，trace 10× 降采样；
对照为 v0.9.0 的 2 细胞 `results/phase4_600/`（跨臂只做描述性比较，RNG 流不共享）。

**预注册假设**：
- H1：抑制降低 both-spike fraction、提高 exclusive fraction（相对 2 细胞）。若没有，
  说明共享前馈抑制不足以产生分化，需要交叉抑制（2 个 I 细胞）才能形成 winner-take-all。
- H2：3 细胞 static 的行为不差于 2 细胞 static（rally/hit 在噪声地板内）。
- H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static）。
- H4：稳态饱和仍存在（3b 的 w_diff→0，权重顶到 w_max）。

**附加指标**：I 放电率、I–motor 率相关、motor 两池排他率、平均抑制电导、
I 对 motor 率的抑制幅度；行为指标不变。

**停止规则**：若 H1 不成立，不通过调 \(\bar g_{inh}\) 或加细胞来“凑”分化；
报告共享抑制不足，交叉抑制留作新的预注册版本。

### 6H.1 校准结果（2026-10-22，只看率）

1 seed × 60 s，`phase4_pushpull_static`：

| \(\bar g_{inh}\) (nS) | motor 平均率 (Hz) | I 平均率 (Hz) | exclusive | both spike |
|---:|---:|---:|---:|---:|
| 5 | 17.4 | 18.6 | 0.0275 | 0.1465 |
| **10（选中）** | **16.5** | **18.6** | **0.0272** | **0.1428** |
| 20 | 14.4 | 18.6 | 0.0257 | 0.1267 |

全部落在 5–40 Hz；按规则选中间值 **10 nS**，冻结。
校准已显示：共享前馈抑制降低了 motor 率（17.4→14.4 Hz），但 exclusive fraction
基本不变（2.6–2.8%）——H1 的主实验很可能为负；仍按预注册跑完 600 s 再判定。

### 6H.1 结果（已完成：共享抑制不产生分化；可塑性仍有害）

完整报告：`results/phase4_inhibition_report.md`；数据：`results/phase4_inhibition_600/`。

**回退验证**：关闭抑制时，static seed 0 / 120 s 的全部共享 trace 列与 v0.9.0 逐位一致。

| condition | 3-cell rally | 2-cell rally | 3-cell hit | exclusive | I rate (Hz) | corr(I, motor) |
|---|---:|---:|---:|---:|---:|---:|
| pushpull_static | **0.222** | 0.204 | **0.181** | 0.022 | 18.8 | +0.985 |
| pushpull_3b_no_hs | 0.161 | 0.178 | 0.150 | 0.013 | 18.7 | +0.633 |
| pushpull_3b_play_hs | 0.161 | 0.165 | 0.139 | 0.002 | 18.5 | +0.921 |
| pushpull_3b | 0.163 | 0.151 | 0.129 | 0.001 | 18.7 | +0.927 |
| random_3b | 0.149 | 0.168 | 0.129 | 0.000 | 18.7 | +0.930 |
| random_paddle | 0.107 | 0.125 | 0.096 | 0.015 | 18.4 | +0.979 |
| symmetric_static | 0.162 | 0.162 | 0.138 | 0.000 | 18.7 | +0.984 |

- **H1 不支持**：3-cell static 的 exclusive = 0.0220，2-cell = 0.0217；both-spike 0.142 vs 0.150；
  两池率相关仍 0.970。I 细胞与 motor 共同活动相关 0.985——它只跟踪共同驱动，没有选择性。
  共享前馈抑制把 motor 率降低约 8%，但没有产生排他放电。
- **H2 弱支持**：3-cell static 0.222 vs 2-cell 0.204（+0.018，跨臂描述性，未达显著）。
  结构优势仍显著：static − symmetric +0.059（p=0.0025）；static − random +0.115（p<0.0001）。
  symmetric 在两臂完全相同（0.1622），是干净的零对照。
- **H3 支持且更强**：3b −0.059（p=0.020）、no_hs −0.061（p=0.006）、play_hs −0.061（p=0.017），
  三个可塑条件都显著低于 static。
- **H4 支持**：3b 的 `w_diff corr = 0.000`，`at w_max` 0.40，impact corr 0.177；
  no_hs 权重均值 0.445、梯度相关 0.835。
- **结论**：共享前馈抑制不足以产生 motor 分化；行为上无收益；可塑性仍有害。
  下一步若继续，需要交叉抑制（2 个 I 细胞）或 motor 池间的递归竞争，
  这是新的预注册版本，不再通过调 \(g_{inh}\) 或加共享抑制来“凑”分化。

---

## 6I. 交叉抑制 4 细胞版（预注册，2026-10-22）

**动机**：v0.10.0 的共享前馈抑制只提供 common-mode，exclusive 与 2-cell 相同。
交叉抑制是形成 winner-take-all 的最小 motif。

**架构（v0.11.0-phase4-cross-inhibition）**：
- 2 个 motor 池（up/down，push-pull，可塑）不变。
- 新增 I_up、I_down 两个抑制性中间神经元（同一 RS Tier 0）。
- **连接**：
  - up 池的 spike → I_up（兴奋性，\(g_{rec}=40\) nS/spike，\(\tau=5\) ms，单通道）；
    down 池的 spike → I_down（同样）。
  - I_up 的 spike → **down 池**抑制（\(g_{inh}\)，\(E_{inh}=-80\) mV，\(\tau_{inh}=10\) ms）；
    I_down 的 spike → **up 池**抑制。
  - I 细胞**不接收感觉输入**（纯递归驱动），权重静态。
- **时序**：tick k 的 motor spike 驱动 I，I 的 spike 在 tick k+1 抑制对侧 motor
  （10 ms 环路延迟，显式记录）。
- 读出、motor 可塑性、稳态、条件、seeds、600 s 不变。
- 引擎复用 v0.10.0 的 `g_inh`；关闭交叉抑制时仍与 v0.9.0 逐位一致。

**Tier 归类**：\(g_{rec}\) 与 \(g_{inh}\) 为 Tier 1（校准后冻结）；I 细胞身份为 Tier 0。
预注册写入 `docs/parameter_policy.md`。

**校准规则（只看率）**：
- 固定 \(g_{rec}=40\) nS；\(g_{inh}\in\{5,10,20\}\) nS，1 seed × 60 s；
- 选择使 motor 平均率与 I_up/I_down 平均率都落在 5–40 Hz 的中间值；
- 若 \(g_{rec}=40\) 不能让 I 细胞放电，允许先把 \(g_{rec}\) 提到 80 nS 并记录；
- 校准结果写入 HANDOFF，冻结后跑主实验；不根据 exclusive/行为选值。

**条件与设计**：7 条件 × 15 seeds × 600 s，trace 10× 降采样；
对照为 2-cell（`results/phase4_600`）与 shared-inhibition（`results/phase4_inhibition_600`），
跨臂只做描述性比较。

**预注册假设**：
- H1：交叉抑制提高 exclusive fraction、降低 both-spike fraction（相对 2-cell 与 shared）；
  若没有，说明该递归强度/时序不足以形成 winner-take-all。
- H2：4-cell static 的行为不差于 2-cell static。
- H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static）；同时观察交叉抑制是否让 3b 产生分化。
- H4：稳态饱和仍存在（3b 的 w_diff→0，权重顶到 w_max）。

**附加指标**：I_up/I_down 放电率、两者互相关、I_up 与 down 池率的相关、
motor 两池排他率、平均抑制电导。

**停止规则**：若 H1 不成立，不调 \(g_{rec}/g_{inh}\)、不继续加细胞；
报告该交叉抑制 motif 不足，下一步才考虑 motor 池间递归兴奋或不同细胞类型。

### 6I.1 校准结果（2026-10-22，只看率）

1 seed × 60 s，`phase4_pushpull_static`，\(g_{rec}=40\) nS：

| \(g_{inh}\) (nS) | motor 平均率 (Hz) | I_up/I_down 合计率 (Hz) | exclusive | both spike |
|---:|---:|---:|---:|---:|
| 5 | 17.5 | 7.0 | 0.0297 | 0.1463 |
| **10（选中）** | **17.3** | **6.6** | **0.0268** | **0.1455** |
| 20 | 17.2 | 7.0 | 0.0298 | 0.1410 |

全部落在 5–40 Hz；按规则选中间值 **10 nS**，\(g_{rec}=40\) nS 冻结。
I 细胞在 60 s 内约 350–390 spikes/细胞（~6–7 Hz），两 I 的 spike 数接近，
提示当前驱动下交叉抑制可能仍不足；按预注册跑完 600 s 再判定。

### 6I.1 结果（已完成：速率层交叉抑制不产生分化）

完整报告：`results/phase4_cross_inhibition_report.md`；数据：`results/phase4_cross_inhibition_600/`。

**回退验证**：关闭抑制时 trace 与 v0.9.0 逐位一致；shared 模式保持不变。

| condition | 2-cell rally | shared rally | cross rally | cross exclusive | I_up/I_down spikes |
|---|---:|---:|---:|---:|---:|
| pushpull_static | 0.204 | 0.222 | **0.194** | 0.0221 | 3721 / 3712 |
| pushpull_3b_no_hs | 0.178 | 0.161 | 0.146 | 0.0144 | 3030 / 3035 |
| pushpull_3b_play_hs | 0.165 | 0.161 | 0.163 | 0.0025 | 4681 / 4684 |
| pushpull_3b | 0.151 | 0.163 | 0.170 | 0.0009 | 4717 / 4716 |
| random_3b | 0.168 | 0.149 | 0.188 | 0.0004 | 4738 / 4738 |
| random_paddle | 0.125 | 0.107 | 0.123 | 0.0155 | 3704 / 3720 |
| symmetric_static | 0.162 | 0.162 | 0.162 | 0.000 | 3688 / 3688 |

- **H1 不支持**：cross static 的 exclusive = 0.0221，2-cell 0.0217，shared 0.0220；
  I_up/I_down 的 spike 数差异 **<0.5%**。两个 I 只读取各自 motor 池的**总率**，
  而 push-pull 两池总率本来相近（17.13 vs 17.11 Hz），交叉抑制被平衡抵消。
- **H2 弱/不支持**：cross static 0.194 < 2-cell 0.204 < shared 0.222（差异未显著）；
  cross 臂内 static−symmetric +0.031（p=0.152，不显著），结构优势未能保持。
- **H3 部分支持**：no_hs −0.048（p=0.020）；3b −0.023（p=0.387）、play_hs −0.031（p=0.260）
  方向更差但不显著；可塑性仍无收益。
- **H4 支持**：3b `w_diff=0`，`at w_max` 0.467，impact corr 0.170；no_hs 权重 0.359、梯度相关 0.777。
- **结论**：速率层交叉抑制对这个 push-pull 网络是“盲”的——两池总率相近，
  I_up/I_down 等量放电，不能形成 winner-take-all。下一步需要让抑制环路读取**差分/位置特异性**
  （I 接收 8 通道感觉并按 push-pull 调谐），或 motor 池之间直接相互抑制；这是新预注册版本，
  不再调 \(g_{rec}/g_{inh}\) 或加同质 I 细胞。

---

## 6J. 差分调谐抑制 4 细胞版（预注册，2026-10-22）

**动机**：v0.11.0 的交叉抑制只读取 motor 池总率，而两池总率相近，I_up/I_down 被平衡。
本版本让 I 细胞直接读取**位置差分**：I_up 调谐到高 y，I_down 调谐到低 y，
再交叉抑制对侧 motor 池。

**架构（v0.12.0-phase4-tuned-inhibition）**：
- 2 个 motor 池不变；I_up/I_down 各接收与 motor **相同**的 8 通道感觉事件，
  但使用 push-pull 权重：
  - I_up: \(w_i = 1 + 0.2x_i\)
  - I_down: \(w_i = 1 - 0.2x_i\)
  - \(x_i=(i-4.5)/3.5\)（与 motor 初始权重一致）；乘以 `tuned_inh_gain=1.0`。
- I 细胞**不接收反馈、不接收 motor 递归输入**；权重静态。
- I_up spike → down 池抑制；I_down spike → up 池抑制；同 tick、按精确 spike 时间投递
  （无 10 ms 延迟）。
- \(g_{inh}\) 为 Tier 1，校准后冻结；\(E_{inh}=-80\) mV，\(\tau_{inh}=10\) ms。
- 读出、motor 可塑性、稳态、条件、seeds、600 s 不变。
- 关闭时与 v0.9.0 逐位一致。

**校准规则（只看率）**：\(g_{inh}\in\{5,10,20\}\) nS，1 seed × 60 s；
选择使 motor 与 I_up/I_down 平均率都落在 5–40 Hz 的中间值；不根据 exclusive/行为选值。

**条件与设计**：7 条件 × 15 seeds × 600 s，trace 10× 降采样；
对照为 2-cell、shared、cross 三臂，跨臂描述性比较。

**预注册假设**：
- H1（核心）：I_up 与 I_down 的每 tick 放电计数差与 ball_y 正相关（r > 0.5）；
  exclusive fraction 高于 2-cell/shared/cross，both-spike 下降。
- H2：4-cell static 的行为不差于 2-cell static；若抑制锐化了差分，rally/hit 可能略升。
- H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static）。
- H4：稳态饱和仍存在（3b 的 w_diff→0，权重顶到 w_max）。

**附加指标**：I_up/I_down 总 spike、两者计数互相关、`corr(I_up−I_down, ball_y)`、
motor 两池排他率、平均抑制电导。

**停止规则**：若 H1 不成立，停止抑制网络这条线（不再调 \(g_{inh}\)/gain/加细胞），
报告“差分调谐抑制仍不足”，转向背景噪声/任务时间尺度。

### 6J.1 校准结果（2026-10-22，只看率）

1 seed × 60 s，`phase4_pushpull_static`，`tuned_inh_gain=1.0`：

| \(g_{inh}\) (nS) | motor 率 (Hz) | I 合计率 (Hz) | exclusive | corr(I_up−I_down, y) |
|---:|---:|---:|---:|---:|
| 5 | 17.3 | 18.4 | 0.0230 | +0.210 |
| **10（选中）** | **17.0** | **19.0** | **0.0303** | **+0.194** |
| 20 | 16.6 | 19.4 | 0.0313 | +0.217 |

全部落在 5–40 Hz；按规则选中间值 **10 nS** 并冻结。
60 s 单 seed 的差分相关只有 ~0.19–0.22（H1 要求 >0.5），
但样本很小；按预注册跑完 600 s（15 seeds）再判定。

### 6J.1 结果（已完成：差分调谐仍不足，抑制线停止）

完整报告：`results/phase4_tuned_inhibition_report.md`；数据：`results/phase4_tuned_inhibition_600/`。

| condition | 2-cell | shared | cross | tuned | tuned hit |
|---|---:|---:|---:|---:|---:|
| pushpull_static | 0.204 | 0.222 | 0.194 | **0.228** | 0.185 |
| pushpull_3b_no_hs | 0.178 | 0.161 | 0.146 | 0.173 | 0.151 |
| pushpull_3b_play_hs | 0.165 | 0.161 | 0.163 | 0.193 | 0.166 |
| pushpull_3b | 0.151 | 0.163 | 0.170 | 0.172 | 0.146 |
| random_3b | 0.168 | 0.149 | 0.188 | 0.173 | 0.147 |
| random_paddle | 0.125 | 0.107 | 0.123 | 0.095 | 0.086 |
| symmetric_static | 0.162 | 0.162 | 0.162 | 0.180 | 0.152 |

- **H1 不支持**：`corr(I_up−I_down, y)` = **0.196**（要求 >0.5）；
  I_up/I_down 总 spike 差异 <1%（static 3127/3140）；exclusive 0.0236
  （2-cell 0.0217，shared 0.0220，cross 0.0221）。
- **重要缺陷**：tuned 臂的 symmetric **不再是冻结球拍**——调谐 I 注入差分，
  `mean_abs_rate_diff=0.46`，symmetric rally 0.162→0.180。因此 tuned 臂内
  static−symmetric（+0.048，p=0.033）不能当作干净的结构对照。
- **H2 弱支持**：tuned static 0.228 为四臂最高，但仅比 2-cell 0.204 高 +0.024（跨臂描述性）；
  比 shared 0.222 高 +0.006。绝对增益很小。
- **H3 支持**：no_hs −0.055（p=0.024）、3b −0.057（p=0.012）；play_hs −0.035（p=0.126）。
- **H4 部分支持**：3b `w_diff corr=0.036`（接近 0），`at w_max` 0.20；稳态仍基本抹平差分。
- **机制**：±26% 的 push-pull 权重差只产生 <1% 的 I 总率差；共同感觉驱动（18–19 Hz）
  远大于差分分量，每 tick 计数只有 0–1 个 spike，量化噪声大。交叉抑制仍近似平衡。
- **结论**：按预注册停止规则，**抑制网络这条线到此为止**；不再调 \(g_{inh}\)/gain/加同质 I 细胞。
  若继续，转向背景噪声（rest 期沉默/稳态饱和）或任务时间尺度（放慢球/更长回合）。

---

## 6K. 放慢球 / 延长回合（预注册，2026-10-22）

**动机**：Phase 4 的绝对命中率一直停在 0.17–0.19；剩余假设是 2 s 回合太短，
读出窗口/突触延迟吃掉了大部分修正时间。放慢球直接检验这一点。

**唯一改动**：Tier 1 `ball_speed` 0.5 → **0.25** bins/s（回合 2 s → 4 s）。
其余全部冻结：2 细胞 push-pull、`velocity_gain=0.15`、感觉率 4–40 Hz、
7 条件、15 seeds、600 s、rest 协议、可塑性/稳态参数。
新版本 v0.13.0-phase4-slow-ball，不与 v0.9.0 混比。

**预注册假设**：
- H1：`pushpull_static` 的 hit rate / rally 明显高于 v0.9.0（0.169 / 0.204）；
  impact error 下降（从 1.87 起步）。
- H2：static 相对 symmetric / random 的结构优势保持或扩大；
  symmetric（冻结球拍）的 hit 应回到 ~1/7 ≈ 0.143。
- H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static）。
- H4：稳态饱和仍存在（3b 的 w_diff→0，权重顶到 w_max）。

**分析**：与 v0.9.0 只做描述性比较（不同任务）；同臂内两组置换检验；
同时报告 T1/T2 命中率与 K_eff。
**停止规则**：若 hit/rally 没有明显改善，说明瓶颈不是时间窗，而是读出质量/延迟；
不再调球速或回合长度，转向背景噪声/预测读出或停止。

### 6K.1 结果（已完成：放慢球不是修复，K 反而减半）

完整报告：`results/phase4_slow_ball_report.md`；数据：`results/phase4_slow_ball_600/`。

| condition | 2 s rally | 4 s rally | 2 s hit | 4 s hit | K_eff 2 s | K_eff 4 s |
|---|---:|---:|---:|---:|---:|---:|
| pushpull_static | **0.204** | **0.178** | **0.169** | **0.150** | 0.141 | **0.094** |
| pushpull_3b_no_hs | 0.178 | 0.181 | 0.150 | 0.151 | 0.120 | 0.068 |
| pushpull_3b_play_hs | 0.165 | 0.204 | 0.147 | 0.166 | 0.122 | 0.112 |
| pushpull_3b | 0.151 | 0.132 | 0.129 | 0.125 | 0.017 | 0.018 |
| random_3b | 0.168 | 0.143 | 0.142 | 0.129 | — | — |
| random_paddle | 0.125 | 0.118 | 0.109 | 0.108 | — | — |
| symmetric_static | 0.162 | 0.148 | 0.138 | 0.128 | 0 | 0 |

- **H1 不支持**：static hit 0.169→0.150，rally 0.204→0.178；放慢球反而略差。
- **H2 不支持**：static−symmetric +0.030（p=0.171，不显著）；symmetric hit 0.128 ≈1/7（sanity 成立）。
- **H3 部分支持**：no_hs +0.003（p=0.881）；3b −0.046（p=0.068）；play_hs +0.026（p=0.252）。无学习。
- **H4 支持**：3b w_diff=0，at w_max 0.20；no_hs 权重 0.345、梯度相关 0.874。
- **机制**：感觉率因子 `4+36*(1-ball_x)`；放慢球让更多时间花在低率因子段，
  差分信号平均幅度下降，K_eff 从 0.141 降到 0.094。时间窗不是唯一瓶颈，
  读出幅度/形状与延迟共同决定上限。
- **结论**：按预注册停止规则，任务时间尺度这条线到此为止；不再调球速/回合长度。
  若继续改任务，应同时提高低 `ball_x` 段的信号幅度（如读出归一化），而不是单纯延长回合。

---

## 6L. 归一化读出（预注册，2026-10-22）

**动机**：v0.8.0 的恒常率与 v0.13.0 的放慢球都表明，瓶颈是差分信号的**幅度/形状**：
距离门控让早期差分很小、末端最大。归一化可以直接去掉这个尺度因子。

**唯一改动**：读出从
\[
v = k\,(r_{up}-r_{down})
\]
改为
\[
v = k_{norm}\,\frac{r_{up}-r_{down}}{r_{up}+r_{down}+\epsilon}
\]
并 clip 到 \(\pm4\) bins/s。\(k_{norm}=5.0\) bins/s（预注册，见下），\(\epsilon=10^{-3}\) Hz。
其余全部冻结：2 细胞 push-pull、`ball_speed=0.5`、感觉率 4–40 Hz、
7 条件 × 15 seeds × 600 s、可塑性/稳态参数。新版本 v0.14.0-phase4-normalized-readout。

**\(k_{norm}\) 的预注册推导（不看行为）**：
static 冲击前差分约 5 Hz、两池和约 36 Hz → 归一化差分 ≈0.139；
旧读出 \(0.15\times5=0.75\) bins/s；\(k_{norm}\approx0.75/0.139\approx5.4\)，
取保守整数 **5.0**。不做行为调参。

**预注册假设**：
- H1：归一化读出提高早期（ball_x>0.5）的差分–ball_y 相关与有效 K，
  static 的 hit/rally 高于 v0.9.0（0.169 / 0.204）；impact error 下降。
- H2：static 相对 symmetric / random 的结构优势保持或扩大；symmetric hit ≈1/7。
- H3：可塑性仍无收益（3b ≤ static；no_hs 不优于 static）。
- H4：稳态饱和仍存在（3b 的 w_diff→0，权重顶到 w_max）。

**分析**：与 v0.9.0 描述性比较；同臂内两组置换检验；报告 T1/T2、K_eff、
`corr(norm_diff, ball_y)` 与 early/late 相关。
**停止规则**：若 H1 不成立，停止读出这条线；转向背景噪声或最终报告。
不再调 \(k_{norm}\) 或增加归一化形式。

### 6L.1 结果（已完成：归一化提高 K，但不改善行为；读出线停止）

完整报告：`results/phase4_norm_readout_report.md`；数据：`results/phase4_norm_readout_600/`。

| condition | diff rally | norm rally | diff hit | norm hit | K_eff diff | K_eff norm |
|---|---:|---:|---:|---:|---:|---:|
| pushpull_static | 0.204 | 0.202 | 0.169 | **0.167** | 0.141 | **0.177** |
| pushpull_3b_no_hs | 0.178 | 0.181 | 0.150 | 0.151 | 0.120 | — |
| pushpull_3b_play_hs | 0.165 | 0.134 | 0.147 | 0.134 | 0.122 | — |
| pushpull_3b | 0.151 | 0.173 | 0.129 | 0.144 | 0.017 | — |
| random_3b | 0.168 | 0.159 | 0.142 | 0.142 | — | — |
| random_paddle | 0.125 | 0.128 | 0.109 | 0.109 | — | — |
| symmetric_static | 0.162 | 0.162 | 0.138 | 0.138 | 0 | 0 |

- **H1 不支持**：K_eff 0.141→0.177（+26%），但 hit 0.169→0.167、rally 0.204→0.202；
  归一化信号的 early/late 相关（0.652/0.887）与旧差分（0.659/0.862）几乎相同。
- **H2 部分支持**：static−random +0.074（p=0.008）；static−symmetric +0.040（p=0.099）；
  symmetric hit 0.138≈1/7。
- **H3 部分支持**：no_hs −0.021（p=0.403）、3b −0.029（p=0.328）；play_hs 显著更差（−0.068，p=0.018）。
- **H4 支持**：3b w_diff=0，at w_max 0.333；no_hs 权重 0.367、梯度相关 0.865。
- **结论**：读出增益/归一化不是限制因素；按预注册停止规则，**读出线到此为止**。
  剩余唯一未做的 Tier 1 机制是背景噪声；若也不改善，应停在当前结论并整理最终报告。

---

## 6M. 背景自发活动（v0.15.0-phase5-spontaneous-activity，预注册，2026-10-22）

**动机**：此前所有版本的 rest 期都是绝对静默，稳态缩放因此以 ~1.16×/s 把权重推向
`w_max`，抹平 push-pull 差分。真实培养物有 1–5 Hz 自发活动；本版本补上这一 Tier 1 机制，
检验稳态饱和与梯度保持是否改善。

**唯一改动**：给每个 motor 池加入独立 Poisson 背景事件：
- `bg_noise_hz = 3.0`（1–5 Hz 区间的中点，预注册）；
- 事件权重 `bg_noise_weight_nS` 由校准决定，使**无感觉输入时**自发率落在 1–5 Hz；
- 事件在 play 与 rest 期间**都存在**；使用独立 RNG（`seed + 10^7`），
  不改变感觉/环境随机流；
- 其余全部冻结：2 细胞 push-pull、`ball_speed=0.5`、`velocity_gain=0.15`、
  感觉率 4–40 Hz、可塑性/稳态参数、600 s。
- P0 筛查只跑 4 条件：`pushpull_static`、`pushpull_3b`、`pushpull_3b_no_hs`、`symmetric_static`；
  15 seeds × 600 s。

**校准规则（只看自发率）**：权重 ∈ {10, 20, 40, 80} nS；1 个孤立细胞、10 s、仅背景事件；
选最小且自发率落在 1–5 Hz 的权重；不根据行为/权重饱和选值。结果写入 HANDOFF 后冻结。

**预注册假设**：
- H1：rest 期自发率 1–5 Hz；600 s 后 3b 的 `at w_max` 明显低于 v0.9 的 0.333，
  且 `w_diff corr > 0.3`（差分结构不再被完全抹平）。
- H2：3b 的行为不低于 static；static 不差于无噪声 v0.9（0.204 / 0.169）超过噪声地板 ~0.04。
- H3：no_hs 仍保留梯度；可塑性仍无可靠的行为收益。
- H4：若 3b 仍饱和（`at w_max >0.3` 且 `w_diff <0.1`），说明 3 Hz 背景不足以阻止稳态饱和；
  停止背景噪声这条线，不再调噪声率/权重。

**分析**：与 v0.9 无噪声结果描述性比较；同臂内两组置换检验；
报告 rest 期自发率、3b 权重饱和、w_diff、行为与 T1/T2。
**停止规则**：若 H1 不成立，不调 `bg_noise_hz/weight`；下一步转向局部信用分配（P1）
或动态稳态目标，而不是继续加噪声。

### 6M.1 结果（已完成：1–5 Hz 背景不足，噪声线停止）

完整报告：`results/phase5_bg_noise_report.md`；数据：`results/phase5_bg_noise_600/`。

**校准**：孤立细胞 3 Hz 背景、80 nS → 3.1 Hz；完整闭环安静 rest 实测 **4.6 Hz**（1–5 Hz 上沿）。

| condition | 无噪声 rally | 有噪声 rally | 无噪声 hit | 有噪声 hit | quiet-rest rate | w_diff corr final | at w_max (up/down) |
|---|---:|---:|---:|---:|---:|---:|---:|
| pushpull_static | 0.204 | **0.189** | 0.169 | **0.158** | 4.61 | +1.000 | 0 / 0 |
| pushpull_3b | 0.151 | 0.155 | 0.129 | 0.134 | 4.63 | **−0.027** | **0.40 / 0.40** |
| pushpull_3b_no_hs | 0.178 | 0.162 | 0.150 | 0.140 | 4.60 | +0.809 | 0 / 0 |
| symmetric_static | 0.162 | 0.146 | 0.138 | 0.122 | 4.60 | 0 | 0 / 0 |

- **H1 不支持**：quiet rest 4.6 Hz 达标，但 3b 仍饱和（at w_max 0.40，w_diff −0.027）。
  机制：20 Hz 目标下 `(20/4.6)^0.05 ≈ 1.078/s`，8 s timeout ≈1.8×，多轮 rest 仍饱和。
  **绝对静默不是唯一原因；目标率/rest 时长的失配才是。**
- **H2 不支持**：static 0.189 < 0.204；3b 0.155 < 0.189；噪声增加抖动。
  symmetric 在噪声下不再冻结（率差 3.56 Hz），不能作零动作对照。
- **H3 支持**：no_hs 梯度 0.809；但行为 0.162，无收益。
- **H4 触发**：3b 仍饱和 → **背景噪声线停止**，不再调噪声率/权重。
- **下一步**：P1 局部/通路特异信用分配（Miss 时按球侧给 Up/Down 不同调制），
  或动态稳态目标（只在 play 期归一化到任务相关 setpoint）。

---

## 6N. 局部信用分配（v0.16.0-phase5-local-credit，预注册，2026-10-22）

**动机**：此前三因子使用全局标量 D(t)，Up/Down 两池收到同一个信号，无法告诉
“哪一侧该负责”。本版本把 D 变成**池特异**的局部误差信号。

**唯一改动**：
- 命中：D_up = D_down = +1（强化当前模式）。
- 未命中：令 error = ball_y − paddle_y（impact 前一刻）：
  - error > 0（球在上方漏掉）→ D_up = +1，D_down = −1；
  - error < 0（球在下方漏掉）→ D_up = −1，D_down = +1。
- 幅度沿用 `reward_plus/reward_minus=±1`；资格迹、STDP、稳态参数不变。
- 条件：`local_3b`、`local_3b_no_hs`、`local_3b_play_hs`、`static`、`global_3b`
  （5 条件 × 15 seeds × 600 s，2 细胞，ball 0.5，3 Hz 背景关闭）。

**预注册假设**：
- H1：local_no_hs / local_play_hs 的最终 `w_diff corr > 0.3`（形成正确 y 梯度），
  而 global_3b 仍 ≈0。
- H2：local 条件的行为高于 static；no_hs/play_hs 不因稳态饱和而退化。
- H3：global_3b 仍无学习收益（对照）。
- H4：若 local_no_hs 仍无行为增益（尽管梯度存在），说明信用分配不是唯一瓶颈；
  停止局部信用线，转向动态稳态/更大网络。

**分析**：同臂两组置换检验；报告最终 y 梯度、Δw、行为、T1/T2。
**停止规则**：不调 D 的幅度、不增加新的局部规则；若 H1 或 H2 不成立即停止。

### 6N.1 结果（已完成：梯度形成，但行为未超过 static；局部信用线停止）

**先说明一次对照污染**：首跑用全局开关 `--local-credit`，把 `3b` 对照臂也变成了
局部信用，`local_3b` 与 `3b` 逐位相同，对照失效。已改为**由条件名选择**
（含 `local` 才启用），删除该开关，并新增 local 相关置换检验。首跑目录存档为
`results/phase5_local_credit_600_bug_globalflag/`，不参与推断。

干净批次（5 条件 × 15 seeds × 600 s）：

| condition | rally | hit | impact corr | w_diff corr (末) | at w_max | 备注 |
|---|---:|---:|---:|---:|---:|---|
| 3b（全局 D） | 0.151 | 8.8 | +0.179 | **0.000** | 0.34/0.34 | 对照，梯度归零 |
| local_3b | 0.151 | 8.8 | +0.173 | **0.364** | 0.40/0.42 | 稳态仍抹平结构 |
| **local_3b_no_hs** | **0.220** | **12.7** | **+0.735** | **0.780** | 0.07/0.04 | 梯度最强，未饱和 |
| local_3b_play_hs | 0.164 | 9.5 | +0.266 | **0.426** | 0.35/0.40 | 仍部分饱和 |
| static | 0.204 | 11.9 | +0.920 | 1.000 | 0/0 | 手工结构上限 |

置换检验：`local_no_hs − static` +0.015（p=0.512）；`local_no_hs − 3b` +0.069（p=0.014）；
`local_play_hs − static` −0.040（p=0.054）；`local_3b − static` −0.054（p=0.006）。

- **H1 支持**：局部信用首次在干净对照下形成正确符号的 y 梯度（0.780/0.426 vs 0.000）。
- **H2 不支持**：no_hs 仅与 static 持平（p=0.512），play_hs 反而更低。
- **H3 支持**：全局 D 臂无学习收益（0.151，p=0.013）。
- **H4 触发**：梯度存在但无行为增益 → 信用分配不是唯一瓶颈，**停止局部信用线**。
- **结论句**：局部信用解决了梯度符号问题，但行为上限由读出结构（static 先验）
  与固定 20 Hz 稳态目标共同决定；2 细胞网络不足以让可塑性“超过”结构先验。
- 报告：`results/phase5_local_credit_report.md`。

**下一步（未开始）**：动态稳态目标（仅 play 期/任务相关 setpoint）、10 细胞 E/I 网络、
或写最终报告。三者均需新版本号与预注册。

---

## 6O. 动态稳态目标带（v0.17.0-phase5-dynamic-homeostasis，预注册，2026-10-23）

**动机**：P1 表明信用分配只解决了梯度符号；固定 20 Hz 点目标仍会在 play 期
（每池 ≈17 Hz < 20 Hz）持续乘性上调，把 35–42% 权重推到 `w_max`。
生理上稳态维持的是**功能范围**，不是一个精确点（Turrigiano & Nelson 2004）。

**唯一改动**：稳态目标由点变为**带** `[5, 30] Hz`，且只在 play 期应用。
- `r < 5 Hz`：`w ← w·(5/r)^α`
- `5 ≤ r ≤ 30 Hz`：不缩放（factor = 1）
- `r > 30 Hz`：`w ← w·(30/r)^α`
- α=0.05、每秒一次、`w_min/w_max`、窗口 300 ms 全部冻结；`use_band=False` 时与旧版逐位一致。
- 不再新增任何局部规则或读出改动。

**条件**（5 条件 × 15 seeds × 600 s，2 细胞，ball 0.5，gain 0.15，4–40 Hz，背景噪声关闭）：
- `phase4_pushpull_local_3b_dyn`（主臂：局部 D + 动态带）
- `phase4_pushpull_dyn_3b`（全局 D + 动态带）
- `phase4_pushpull_local_3b_no_hs`（无稳态参照）
- `phase4_pushpull_static`（手工结构上限）
- `phase4_pushpull_3b`（固定 20 Hz 点目标基线）

**预注册假设**：
- H1：`local_3b_dyn` 的 `at w_max ≤ 0.10`、`w_diff corr > 0.5`，
  且 play 期每池率保持在 10–25 Hz（不因取消缩放而漂移）。
- H2：`local_3b_dyn` 行为 ≥ `no_hs` 且 ≥ `static`（点估计 ≥ +0.02 且 p<0.05 为强支持）。
- H3：若 dyn ≈ no_hs 且两者都不超过 static，说明**饱和不是剩余瓶颈**，
  下一步转向时间编码/短时程可塑性或更大网络。
- H4：若 dyn 显著低于 no_hs（带内仍被稳态干扰），停止动态带线，不再调边界。

**分析**：同臂两组置换检验；报告 `at w_max`、`w_diff corr`、play 期率分布、行为。
**停止规则**：不调 5/30 Hz 边界、不调 α；H1 或 H4 不成立即停止。

### 6O.1 结果（已完成：饱和减半，但没有梯度、没有行为增益；动态带线停止）

| condition | rally | hit | impact corr | w_diff corr | at w_max |
|---|---:|---:|---:|---:|---:|
| 3b（固定点目标） | 0.151 | 8.8 | +0.179 | 0.000 | 0.34 |
| dyn_3b（动态带，全局 D） | 0.183 | 10.7 | **+0.381** | **0.000** | **0.14** |
| local_3b_dyn（动态带，局部 D） | 0.196 | 11.4 | +0.353 | **0.498** | 0.25 / 0.29 |
| local_3b_no_hs | 0.220 | 12.7 | +0.735 | 0.780 | 0.07 / 0.04 |
| static | 0.204 | 11.9 | +0.920 | 1.000 | 0.00 / 0.00 |

置换检验：`local_dyn − static` −0.008（p=0.643）；`local_dyn − no_hs` −0.023（p=0.334）；
`dyn_3b − 3b` +0.033（p=0.153）；`no_hs − static` +0.015（p=0.516）。

- **H1 不支持**：at w_max 0.25（要求 ≤0.10）；`w_diff corr` 0.498（要求 >0.5）；play 每池 ≈16.9 Hz 在带内。
- **H2 不支持**：local_dyn 0.196 < no_hs 0.220（p=0.334）且 < static 0.204（p=0.643）。
- **H3 支持**：dyn ≈ no_hs 且都未超过 static → 饱和不是剩余瓶颈。
- **H4 未触发**（未显著低于 no_hs）。
- **机制**：稳态速率来自 300 ms 窗口；每池 17 Hz 时窗口内仅 ≈5 spike，
  Poisson 波动使不少秒率 <5 Hz，仍触发 `(5/3.3)^0.05≈1.026/s` 上调。
  边界没错，是**短窗口估计方差 × 乘性控制**的结构问题。
- **结论句**：降低饱和 ≠ 产生梯度；全局 D 仍 0 梯度；即使完全不饱和，行为也不超过 static。
- 报告：`results/phase5_dynamic_homeostasis_report.md`。

**下一步（未开始）**：时间维度（STP/预测性前馈读出）或 10 细胞 E/I 网络；需新版本号与预注册。
按停止规则，不再调稳态边界，也不再用稳态参数解释行为上限。

---

## 6P. 短时程突触可塑性（v0.18.0-phase5-stp，预注册，2026-10-23）

**动机**：P0–P2 依次排除了背景噪声、信用符号、稳态饱和；`no_hs` 已能形成
正确梯度（0.78）却仍不越过 static，且 early/late 信息差仍在（0.569 vs 0.740）。
剩余候选瓶颈是**时间维度**：2 细胞网络没有短时程动力学，无法把“球接近”的
率斜坡转成对时序敏感的响应。

**唯一改动**：在感觉→motor 突触上加入 Tsodyks–Markram 短时程可塑性（STP）。
- `u ← U + (u−U)·exp(−Δt/τ_fac)`，`R ← 1 + (R−1)·exp(−Δt/τ_rec)`（Δt 为同通道事件间隔）
- 单事件有效电导 `g_eff = w · (u·R)/U`（除以 U 归一化，使低频效力等于基线，避免输入强度混杂）
- 释放后 `R ← R(1−u)`，`u ← u + U(1−u)`
- 参数冻结：`U=0.4`、`τ_rec=200 ms`、`τ_fac=1000 ms`（TM 常用中值，不做网格搜索）
- 仅作用于**感觉事件**；反馈、背景事件权重不变；STDP/资格迹/稳态/读出全部冻结
- 关闭（无条件名含 `stp`）时与 v0.17.0 逐位一致

**条件**（5 条件 × 15 seeds × 600 s，2 细胞，ball 0.5，gain 0.15，4–40 Hz，背景噪声关闭，
稳态沿用 P1 的 `no_hs` 设置以隔离时间维度）：
- `phase4_pushpull_local_3b_no_hs_stp`（主臂：局部 D + STP）
- `phase4_pushpull_3b_no_hs_stp`（全局 D + STP，信用对照）
- `phase4_pushpull_static_stp`（固定 push-pull 权重 + STP，结构对照）
- `phase4_pushpull_static`（固定权重，无 STP）
- `phase4_pushpull_local_3b_no_hs`（局部 D，无 STP；同批参照）

**预注册假设**：
- H1（时间形状）：`local_stp` 的 `late_norm − early_norm` 差从 0.171 收窄到 <0.10，
  或 `early_norm_corr > 0.65`（STP 让早期高率段不再被末端淹没）。
- H2（行为）：`local_stp` 的 rally 高于 `local_no_hs`，且高于 `static_stp`
  （两者共享同一 STP 输入，是干净的“有无可塑性”对照），点估计 ≥ +0.02 且 p<0.05 为强支持。
- H3（解释性诊断，不作为停止条件）：`static_stp` 与 `static` 的差用于量化 STP 本身
  对输入强度的影响；不要求 ≤0.03，因为 U 归一化在 20 Hz 下把净释放降到 ≈0.54×基线
  （解析：u_ss≈0.96、R_ss≈0.016；4 Hz≈1.44×、40 Hz≈0.29×）。行为推断以
  `local_stp vs static_stp` 为主。
- H4：H1 不成立 → STP 未改变时间形状，停止 STP 线；H1 成立但 H2 不成立 →
  时间形状也不是瓶颈，转更大网络或收尾。

**分析**：同臂两组置换检验；报告 early/late 相关、impact corr、`w_diff`、行为。
**停止规则**：不调 U/τ；不叠加 PD 读出（PD 作为独立版本另行预注册）；H1 不成立即停止。

### 6P.1 结果（已完成：时间形状被改变，行为未升；时间维度线停止）

| condition | rally | hit | early | late | impact corr | w_diff corr | mean \|w_diff\| | at w_max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| local_3b_no_hs | 0.220 | 12.7 | 0.569 | 0.740 | 0.735 | 0.780 | 0.327 | 0.07/0.04 |
| local_3b_no_hs_stp | 0.187 | 10.9 | **0.699** | 0.817 | **0.809** | **0.880** | 0.391 | 0.03/0.01 |
| 3b_no_hs_stp | 0.200 | 11.6 | 0.645 | 0.728 | 0.759 | 0.946 | 0.147 | 0/0 |
| static | 0.204 | 11.9 | 0.656 | 0.886 | 0.920 | 1.000 | 0.229 | 0/0 |
| static_stp | 0.177 | 10.3 | 0.704 | 0.784 | 0.802 | 1.000 | 0.229 | 0/0 |

置换检验：`local_stp − local_no_hs` −0.032（p=0.243）；`local_stp − static_stp` +0.011（p=0.638）；
`static_stp − static` −0.028（p=0.158）。

- **H1 支持（early 路径）**：early 相关 0.569→0.699（>0.65）；gap 0.171→0.118（未达 <0.10）。
- **H2 不支持**：0.187 < 0.220（p=0.243），与 static_stp 0.177 无差异（p=0.638）。
- **H3 诊断**：STP 本身使率 17.8→15.3 Hz、static 行为 −0.028（p=0.158），输入强度影响温和。
- **H4 触发**：时间形状不是行为瓶颈 → 时间维度线停止（STP 与 PD 均不再尝试）。
- **机制分离**：`local_stp` 的 impact corr 0.809、梯度 0.880 都是 2 细胞最好水平，
  但 mean |diff| 2.25→1.36 Hz，固定增益 0.15 下令球拍速度减半 → 信息更准、动作更弱。
  再次说明行为上限不是信息质量：static 已有 0.920，hit 仍 0.169。
- 校准披露：冻结的 TM 参数在 20 Hz 的净释放为 0.54×基线（4 Hz 1.44×、40 Hz 0.29×）。
- 报告：`results/phase5_stp_report.md`。

**下一步（未开始）**：10 细胞 E/I 网络，或写最终报告。二者需新版本号与预注册。

---

## 6Q. 10 细胞 E/I 前馈网络（v0.19.0-phase5-ten-cell，预注册，2026-10-23）

**动机**：P0–P3 分别处理过噪声、信用符号、稳态、时间动力学，行为都不越过 static。
唯一没动过的维度是**群体动力学**：2 细胞网络没有真正的 E/I 群体与延迟链。

**结构（10 细胞）**：
```
S1–S4（4 个感觉中继，8 通道高斯调谐，中心 1.5/3.5/5.5/7.5 bins，σ=1.5）
   ├─固定 push-pull 权重→ E_up / E_down（2 个兴奋性中间细胞）
   └─固定反向权重────→ I_up / I_down（2 个抑制性中间细胞）
E_up/E_down ─可塑 2×2 权重（push-pull 初值 1.2/0.8）→ Motor up / Motor down
I_up→Motor down，I_down→Motor up（g_inh=10 nS，E_inh=−80 mV）
Motor 仍接收与旧版完全相同的反馈事件；**不再直接接收感觉事件**
```
- 感觉事件→S：`g=40 nS/event × 高斯调谐`（Tier 1 校准值，复用 `syn_weight_nS`）
- S spike→E/I：固定 `g=10 nS × push-pull 权重`（E 与 I 的调谐方向相反）
- E spike→Motor：可塑权重（STDP + 资格迹 + 三因子；局部/全局 D 由条件名决定）
- I spike→Motor：固定抑制电导 10 nS
- 稳态：沿用 `no_hs`（关闭）；STP 关闭；读出与 Pong 协议不变

**Tier 1 校准（唯一允许的搜索，按生理存活准则，不看行为）**：
1. `g_S→E/I ∈ {10, 20, 40} nS`：在 `net_static` 上跑 30 s × 3 seeds，
   选使 E 细胞率落在 10–25 Hz 的最小值。
2. `g_E→M ∈ {10, 20, 40} nS`：在选定的 `g_S→E` 上，选使 play 期 motor 率
   最接近 17.5 Hz（2 细胞 static 基线）且落在 12–25 Hz 的值，冻结。
两者只按上述准则各选一次，不因行为结果回改。

**条件**（5 条件 × 15 seeds × 600 s）：
- `phase5_net_static`（固定 2×2 权重，无可塑性）
- `phase5_net_local_no_hs_3b`（局部 D + STDP，无稳态）
- `phase5_net_global_no_hs_3b`（全局 D，信用对照）
- `phase4_pushpull_static`（2 细胞结构参照）
- `phase4_pushpull_local_3b_no_hs`（2 细胞可塑参照）

**预注册假设**：
- H1（存活/群体动力学）：`net_static` 的 play 期 motor 率 12–25 Hz；E 细胞均 >2 Hz；
  I 细胞有放电；无癫痫（任一细胞 >60 Hz）；报告 E/I 率比与 motor 共活动。
- H2（结构不退化）：`net_static` 与 2 细胞 static 的 rally 差 ≤0.03。
- H3（学习）：`net_local` 的 `w_diff corr > 0.3`，且 rally 高于 `net_static`
  至少 +0.02（p<0.05 为强支持）。
- H4：H3 不成立 → 网络规模本身不足以产生行为增益；停止扩网络，写最终报告。

**分析**：同臂两组置换检验；报告 E/I 率、共活动、梯度、行为。
**停止规则**：不增加 E→I 递归、不加第三层、不调 push-pull span；
`g_E→M` 只按上述校准规则选一次。

### 6Q.1 结果（已完成：网络存活且静态等价，但学习更差；扩网络线停止）

| condition | rally | hit | impact corr | play corr | play motor | E_up/E_down | I_up/I_down |
|---|---:|---:|---:|---:|---:|---:|---:|
| **net_static** | **0.203** | 11.7 | +0.479 | +0.266 | 12.5 | 14.4/14.4 | 14.4/14.4 |
| net_local_no_hs_3b | 0.127 | 7.5 | −0.017 | −0.025 | 13.4 | 14.5/14.6 | 14.6/14.5 |
| net_global_no_hs_3b | 0.148 | 8.7 | +0.116 | +0.072 | 1.9 | 14.6/14.4 | 14.4/14.6 |
| 2-cell static | 0.204 | 11.9 | +0.920 | +0.751 | 19.0 | — | — |

置换检验：`net_local − net_static` −0.076（p=0.005）；`net_global − net_static` −0.055（p=0.039）；
`net_static − 2-cell static` −0.001（p=0.990）；`net_local − 2-cell local` −0.092（p=0.0009）。

- **H1 支持**：S 7.6 Hz、E/I 14.4 Hz、play motor 12.5 Hz，无癫痫。
- **H2 支持**：静态网络与 2 细胞 static 等价（p=0.990）。
- **H3 不支持**：net_local 显著更差；全局 D 把 2×2 权重压到 0.27。
- **H4 触发**：网络规模本身不足以产生行为增益；扩网络线停止。
- **信息瓶颈**：impact corr 0.920→0.479，play corr 0.751→0.266（4 个 S 把 8 通道压成 2 个 E 通道）。
- **注意（指标偏差）**：预注册的 `w_diff corr` 在 2 个可塑通道下被 `_corr` 的 ≥3 点保护
  置为 0，对 2×2 权重不可用；本结论以行为与 impact corr 为准。
- 报告：`results/phase5_ten_cell_report.md`。

**最终状态**：五条机制线（噪声、信用、稳态、时间、规模）全部关闭。
剩余工作只有最终报告。

---

## 6R. PD 读出（v0.20.0-phase5-pd-readout，预注册，2026-10-23）

**动机**：P0–P4 关闭后，唯一未单独检验的接口变量是读出端的**微分前馈**。
行为上限的一个已确认成分是环路延迟/信息晚到；PD 的微分项提供有限提前量
（时间尺度 ≈ τ_pred），但它**不能**补偿 2 s 量级的距离门控延迟。本版本是
“低成本、可证伪”的接口检验，不改变细胞、突触与可塑性规则。

**唯一改动**：`_action` 由比例控制改为 PD 控制
- `v = clip(Kp·Δr + Kp·τ_pred·(dΔr/dt), ±v_max)`
- `Kp=0.15` bins/s/Hz（冻结）；`τ_pred=50 ms`（皮层环路延迟量级，预注册单一值，不搜索）
- 微分用平滑率差的 tick 差分再经同一 `rate_smoothing`（α=0.2）低通
- 静止期照常更新微分状态（避免 rest 结束后出现假脉冲）；不改变动作裁剪
- 关闭（条件名不含 `pd`）时与 v0.19.0 逐位一致

**条件**（4 条件 × 15 seeds × 600 s，2 细胞，ball 0.5，gain 0.15，4–40 Hz，
稳态关闭，STP 关闭，网络关闭）：
- `phase4_pushpull_local_3b_no_hs_pd`（主臂：局部信用 + PD）
- `phase4_pushpull_local_3b_no_hs`（无 PD 参照）
- `phase4_pushpull_static_pd`（手工权重 + PD，控制器对照）
- `phase4_pushpull_static`（手工权重，无 PD）

**预注册假设**：
- H1（主）：`local_pd` 的 rally 高于 `local_no_hs` ≥+0.02 且 p<0.05。
- H2（控制器）：`static_pd` 高于 `static` ≥+0.02 且 p<0.05。
- H3（结构）：`local_pd` 高于 `static` ≥+0.02。
- H4：H1 与 H2 都不成立 → PD 不是杠杆，停止接口线；转递归 E-I 或收尾。

**分析**：同臂两组置换检验；报告 rally、hit、mean |v|、impact corr、K_eff 代理。
**停止规则**：不调 τ_pred（不试 20/100 ms）、不调 Kd 幅度；H1/H2 均失败即停止。

### 6R.1 结果（已完成：PD 对行为无影响；接口线停止）

| condition | rally | hit | mean \|v\| | impact corr | play corr |
|---|---:|---:|---:|---:|---:|
| local_no_hs | 0.220 | 12.7 | 0.28 | +0.735 | +0.636 |
| local_no_hs_pd | 0.220 | 12.7 | 0.28 | +0.747 | +0.632 |
| static | 0.204 | 11.9 | 0.18 | +0.920 | +0.751 |
| static_pd | 0.210 | 12.1 | 0.19 | +0.924 | +0.751 |

置换检验：`local_pd − local_no_hs` −0.000（p=0.998）；`static_pd − static` +0.005（p=0.722）；
`local_pd − static` +0.015（p=0.501）。

- **H1/H2/H3 全部不支持**；**H4 触发** → 接口/PD 线停止。
- **机制**：τ_pred=50 ms 只能补偿几十 ms 环路延迟，无法补偿 2 s 量级的距离门控延迟；
  率差已由 α=0.2 低通，微分幅度极小（mean |v| 不变）。
- **对建议的校正**：PD 是诚实的阴性检验，不是行为杠杆。
- 报告：`results/phase5_pd_readout_report.md`。

**最终状态**：六条线（噪声、信用、稳态、时间、规模、接口）全部关闭。

---

## 6S. 帧式延迟编码（v0.21.0-phase6-temporal-coding，预注册，2026-10-23）

**动机**：PD 证明接口层补偿无效；已确认瓶颈是“率编码被 ball_x 距离门控，信息在回合末端才可用”。
本版本改**信息编码**，不改细胞、突触与可塑性规则。

**唯一改动（一个编码包）**：
- 感觉输入改为**帧式 volley**：每 100 ms 一帧，8 通道各发 1 个事件（等效 10 Hz），
  通道延迟 `d_ch = 100 ms · |ch − ball_y| / 7.5`（最近通道 0 ms，最远 100 ms），
  事件可在帧内/跨 tick 到达（连续时间，不进 tick 量化）。
- 单事件幅度沿用 `syn_weight_nS=40 nS`；反馈协议不变；rest 期不发 volley。
- 读出改为**帧内首脉冲延迟差**：
  `Δt = t_down_first − t_up_first`（ms，相对帧起点；某池无 spike 记 100 ms），
  `v = clip(K_lat·Δt, ±4 bins/s)`，帧间保持。
- `K_lat` 由 6a 校准：冻结球拍，取 |Δt| 的 P95，`K_lat = 4.0 / P95`（单一值，不看行为）。
- 关闭（条件名不含 `lat`）时与 v0.20.0 逐位一致。

**6a 开环验证（先跑，不过则永久停止 A）**：
- 条件 `phase4_pushpull_static_lat_frozen`（push-pull 权重，动作冻结），60 s × 5 seeds。
- Gate：`corr(Δt, ball_y) > 0.5` 且 5/5 seeds 符号一致；motor 率 5–30 Hz；否则停止。
- 通过后用 P95 校准并冻结 `K_lat`。

**6b 闭环（仅 6a 通过后）**：`static_lat`、`local_no_hs_lat`、`static`（率编码参照），
600 s × 15 seeds。

**预注册假设**：
- H1（主）：`static_lat` 的 rally 高于率编码 `static` ≥+0.02 且 p<0.05。
- H2：`local_no_hs_lat` 高于 `static_lat` ≥+0.02。
- H3：`Δt` 与 ball_y 的相关在闭环中仍 >0.5。
- **硬停止**：H1 不成立 → 项目永久结束，转 negative-results 论文；不再开 B/C。

**停止规则**：不调帧长/延迟上限/K_lat 公式；不与 STP、稳态、10 细胞网络组合。

### 6S.1 结果（已完成：Gate 不通过；A 线关闭，项目结束）

| seed | corr(Δt, ball_y) | \|Δt\| P95 (ms) | rate up/down (Hz) |
|---|---:|---:|---:|
| 0 | +0.320 | 2.42 | 19.2 / 19.6 |
| 1 | +0.364 | 4.30 | 22.3 / 22.1 |
| 2 | +0.798 | 4.46 | 19.5 / 19.4 |
| 3 | +0.342 | 2.69 | 20.6 / 20.3 |
| 4 | +0.386 | 6.18 | 22.5 / 21.6 |
| **均值** | **+0.442** | **4.01** | 20.8 / 20.6 |

- Gate `corr > 0.5`：**不通过**（0.442；仅 1/5 seed 超过）。
- 符号一致性 5/5 通过；速率存活通过。
- **机制**：±20% 权重不对称只产生 2–6 ms 首脉冲差（编码范围 0–100 ms）；
  单房室细胞的发放起点被共同输入主导，通道间时间差在突触整合（τ=5 ms）中被压缩。
- 按硬停止：**A 线关闭，不进入 6b；B/C 不再启动；项目转 negative-results 论文。**
- 报告：`results/phase6a_latency_validation_report.md`（数据：`results/phase6a_latency/`）。

**项目最终状态（2026-10-23）**：Phase 0–5 与 Phase 6a 全部完成；七条线全部关闭
（噪声、信用、稳态、时间动力学、规模、接口 PD、输入编码）。

---

## 6T. 递归 E-I 网络（v0.22.0-phase7-recurrent-ei，预注册，2026-10-23）

**预注册覆盖记录**：§6S 曾写“A 不通过 → 项目永久结束，不再开 B/C”。
2026-10-23 用户**明确要求再尝试方案 B**，该要求覆盖上述硬停止条款；
按纪律开新版本号，并先只做存活/动力学 Gate，不直接跑闭环。

**结构（22 细胞）**：
```
S1–S4（感觉中继，8 通道高斯调谐）
   └─固定权重→ E1–E8（兴奋性，8 个位置调谐）
E1–E8 ──固定递归 w_ee（全连接、无自连，上一 tick 的 E spike）──→ E1–E8
E1–E8 ──固定 w_ei──→ I1–I8（抑制性）
I1–I8 ──抑制电导 g_ie（上一 tick）──→ E1–E8
E1–E8 ──可塑 8 通道 push-pull 权重──→ Motor up / down
Motor 仍接收反馈事件；不直接接收感觉事件
E/I/S 均叠加独立背景 Poisson（3 Hz，80 nS/event）
```
- 感觉输入保持率编码（4–40 Hz，与主协议一致），未采用 6a 的延迟编码。
- 7a 只跑**静态权重**（无可塑性、无稳态），目的是检验网络是否进入异步不规则（AI）状态。

**参数与校准（7a 唯一允许的搜索）**：
- 固定：`w_se=20 nS`、`w_ei=20 nS`、`g_ie=10 nS`、背景 3 Hz/80 nS。
- 待校准：`w_ee ∈ {0, 5, 10, 20} nS`（60 s × 3 seeds），
  选使 E 率落在 5–25 Hz 的最大值；冻结后不再改。

**7a Gate（全部满足才进入闭环）**：
- G1 存活：8 个 E 细胞的平均率 5–25 Hz；I 率 >0；无任何细胞 >60 Hz。
- G2 不规则：E 细胞 ISI 的 CV 均值 >0.5。
- G3 不同步化：E 细胞两两 10 ms 计数的平均相关 <0.8。
- G4 稳定：后半段 E 群体率与前半段差 <30%（无漂移/癫痫）。

**硬停止**：Gate 任一项不通过 → B 线永久关闭，不再调 w_ee/背景/拓扑，项目转论文。
通过则另行预注册 7b 闭环（`rec_static`、`rec_local_no_hs`、2 细胞 static 参照）。

### 6T.1 结果（2026-10-23，已完成：Gate 不通过，B 线永久关闭）

**实现**：`Phase4Loop.rec_mode`（条件名含 `rec`）；4 S + 8 E + 8 I + 2 motor。
S→E 固定 `rec_w_se`（20 nS × 高斯调谐），E→E 固定 `w_ee`（上一 tick、全连接、无自连），
E→I 固定 20 nS（一一对应），I→E 上一 tick 抑制 10 nS，E→motor 为 8 通道可塑权重
`rec_w_em_nS=5 × pool.syn.w[ch]`（不直接接感觉），E/I/S 独立 3 Hz 背景。

**校准结果（play 期统计，3 seeds × 60 s）**：

| w_ee (nS) | E 率 (Hz) | I 率 (Hz) | 最大单细胞 (Hz) | CV(ISI) | 两两相关 | 漂移 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3.67 | 3.15 | 4.73 | 0.970 | 0.035 | 0.023 |
| 5 | 4.07 | 3.19 | 5.33 | 1.039 | 0.060 | 0.052 |
| 10 | 158.04 | 18.00 | 158.64 | 2.100 | 0.898 | 0.302 |
| 20 | 253.22 | 55.02 | 254.04 | 0.820 | 0.818 | 0.069 |

- G1 存活（E 率 5–25 Hz）：4 个点全部不通过（3.67 / 4.07 / 158.0 / 253.2）。
- G1 单细胞上限 <60 Hz：w_ee=10/20 不通过。
- G2 CV>0.5：全部通过；G3 两两相关<0.8：w_ee=10(0.898)/20(0.818) 不通过；
  G4 漂移<0.3：w_ee=10(0.302) 不通过。
- **校准本身失败**：允许网格内不存在 5–25 Hz 的 `w_ee`。网络是双稳态的
  （背景主导的 ~4 Hz 下态 vs 点火后的 >150 Hz 上态），没有异步不规则中间态。

**根因**：`w_se=20 nS` 下 S 细胞 7.5 Hz 只给 E 提供约 1 nS 平均电导，E 的工作点由
3 Hz 背景决定（`w_ee=0` 时 E 3.67 Hz ≈ 背景 3 Hz）；再增大递归会直接越过点火点。
按 §6T 硬停止，**不得**回调 `w_se`/背景/拓扑，也不扩大 `w_ee` 网格。

**归档（不计入推断）**：`results/phase7_7a_bug_zerodelay/`（E→E 零延迟 bug）、
`results/phase7_7a_metric_overall/`（含 rest 的率/CV/漂移）、
`results/phase7_7a_bug_i_rate_unfiltered/`（I 率分子含 rest）。
最终数据：`results/phase7_7a/`；报告：`results/phase7a_rec_ei_gate_report.md`；
图：`results/figures/fig_phase7a_rec_ei.png`。

---

## 7. 断点续跑（checkpoint/resume）设计

> 阶段 0/1 实现；原则是“trial 级保存 + 原子写入 + 可恢复”。

### 7.1 run 的粒度

- 一个 **run** = 一个 `(condition, seed)` 组合。
- 一个 run 包含若干 **session**（默认 1 个 session = 5–20 min）。
- 一个 session 包含若干 **trial**（默认一个 rally 或固定 10 s 块）。

### 7.2 checkpoint 内容（`runs/<run_id>/checkpoint.npz`）

| 类别 | 内容 |
|---|---|
| 时间 | `t_sim_s`、`trial_index`、`session_index` |
| 游戏 | 球 x/y、球拍 y、球速度、rally 统计、当前条件 |
| 细胞 | `V`、门控变量 `m/h/n`、`Ca`、适应变量（可选） |
| 可塑性 | `w`、`e`、`gmax_scale`、`v12_shift`、受体池 `S/I`、STP 变量 |
| 随机 | NumPy `Generator` 状态（pickle 字节） |
| 指标 | 运行中的累计量（hits、misses、rally lengths、spike counts） |
| 校验 | `config_hash`、`code_version`、`seed` |

### 7.3 写入策略

- 每 N 秒仿真（默认 30 s）或每个 trial 结束保存一次。
- 先写 `checkpoint.tmp.npz`，再 `os.replace` 为 `checkpoint.npz`，避免半写文件。
- 同时更新 `manifest.json`：
  ```json
  {
    "run_id": "three_factor_s0",
    "status": "running|paused|completed|failed",
    "condition": "three_factor",
    "seed": 0,
    "config_hash": "...",
    "t_sim_s": 123.4,
    "trial_index": 57,
    "started_at": "...",
    "last_checkpoint_at": "...",
    "metrics_summary": {...}
  }
  ```
- 捕获 `KeyboardInterrupt` / `SIGTERM`：保存后退出，状态置 `paused`。
- `--max-wall-hours N`：到点优雅停止，状态置 `paused`。
- **最坏情况**（直接断电/强制关机）最多丢失一个 checkpoint 间隔，默认 30 s；这是可接受的代价。

### 7.4 恢复

```powershell
python experiments\phase3_single_cell.py --run-id three_factor_s0 --resume
```

- 读取 `config` 和 `manifest.json`；
- 校验 `config_hash`；
- 重建网络（同一 seed）；
- `set_states()` 恢复细胞/可塑变量；
- 恢复游戏状态与 RNG；
- 从 `t_sim_s` 继续。

### 7.5 简化策略（推荐先做）

如果完整状态序列化太脆弱，先做 **trial 级独立存档**：

- 每个 trial 结束后保存 `w`、`e`、`gmax_scale`、`v12_shift`、受体池、游戏状态、RNG；
- 恢复时允许重置 `V` 和门控变量（因为 trial 之间有 rest/reset，生物学上可接受）；
- 在报告中说明这一简化。

---

## 8. 24 h 运行管理

- **并行**：24 核，建议同时跑 8–12 个单线程进程（每个 run 一个进程），留出内存和系统余量。
- **队列**：`runs/queue.json` 列出所有 `(condition, seed)`；runner 逐个领取，已完成则跳过。
- **日志**：`runs/<run_id>/run.log`，记录开始、checkpoint、异常、结束。
- **汇总**：`results/summary.csv`，每个 run 一行：condition、seed、T1/T2 指标、状态。
- **中断**：关机前运行 `python experiments/stop_all.py`（或 Ctrl+C），确保所有 run 保存 checkpoint。

---

## 9. 开放问题 / 候选方向

| # | 事项 | 状态 |
|---|---|---|
| 1 | 文献与 ModelDB 归档 | 已完成：`reference/` 下核心 PDF + ModelDB 代码 |
| 2 | 网络规模（2–5 vs ~12） | 暂定停在 4 细胞；抑制、时间尺度、读出、背景噪声四条线均已停止 |
| 3 | 共享前馈抑制性中间神经元 | **已完成（v0.10.0，负结果）**：exclusive 0.022 vs 2-cell 0.0217 |
| 4 | 交叉抑制（2 个 I 细胞） | **已完成（v0.11.0，负结果）**：I_up/I_down 差异 <0.5%，exclusive 0.0221 |
| 5 | 差分调谐抑制（I 接收 8 通道感觉） | **已完成（v0.12.0，负结果）**：corr(I_up−I_down, y)=0.196；symmetric 对照被污染 |
| 6 | 放慢球 / 更长回合（v0.13.0） | **已完成（负结果）**：K_eff 0.141→0.094，hit 0.169→0.150 |
| 7 | 归一化读出（v0.14.0） | **已完成（负结果）**：K_eff 0.141→0.177，hit 0.169→0.167 |
| 8 | 背景噪声 1–5 Hz（v0.15.0 P0） | **已完成（负结果）**：quiet-rest 4.6 Hz，但 3b 仍饱和（at w_max 0.40，w_diff −0.027） |
| 9 | P1 局部/通路特异信用分配（v0.16.0） | **已完成（梯度正结果 / 行为负结果）**：`w_diff corr` 0.000→0.780（no_hs）/0.426（play_hs），但 no_hs 行为仅与 static 持平（p=0.512）；线停止 |
| 10 | 动态稳态目标（仅 play 期/任务相关 setpoint）（v0.17.0） | **已完成（弱正结果 / 行为负结果）**：at w_max 0.34→0.14、impact corr 0.179→0.381；但全局 D 仍 0 梯度，local_dyn 行为 0.196 ≈ static 0.204（p=0.643）；线停止 |
| 11 | 扩到 10 细胞 E/I 网络（v0.19.0） | **已完成（存活/结构正结果、学习负结果）**：net_static 0.203 ≈ 2 细胞 static 0.204（p=0.990），impact corr 0.920→0.479；net_local 0.127（p=0.005）、net_global 0.148；H3 不支持，线停止 |
| 12 | MSVC / Cython | 不需要：Numba 引擎已足够快（600 s run ~30–50 s） |
| 13 | 其他文献/数据需求 | 暂无 |
| 14 | 时间维度：STP（v0.18.0） | **已完成（机制正结果 / 行为负结果）**：early 0.569→0.699、gap 0.171→0.118、impact 0.735→0.809、梯度 0.780→0.880；但命令减半，行为 0.187 < 0.220（p=0.243）；线停止 |
| 15 | 接口维度：PD 读出（v0.20.0） | **已完成（负结果）**：τ_pred=50 ms 对行为无影响（p=0.998/0.722），impact corr 仅 +0.01；线停止 |
| 16 | 输入编码：帧式延迟编码（v0.21.0） | **已完成（Gate 不通过）**：corr(Δt, ball_y)=0.442 <0.5，Δt P95 仅 4.0 ms；A 线停止，未进入闭环 |

> 用户已明确：需要任何文献/模型数据都可以直接向他索取。

---

## 10. 交接检查清单

每次会话结束前：

- [ ] README 的“状态/变更记录”已更新
- [ ] 本 HANDOFF 的“当前状态快照”和“下一步”已更新
- [ ] `config/experiment_default.yaml` 的 `config_hash` 已更新
- [ ] 新增/修改的参数记录在 `docs/parameter_policy.md` 的变更日志
- [ ] 运行结果写入 `results/`，checkpoint 写入 `runs/`
- [ ] 没有引入反向传播/全局优化器
- [ ] 负结果、异常、失败尝试已记录（不要只留成功路径）
- [ ] 下一步命令可直接复制执行

---

## 11. 术语表

| 术语 | 含义 |
|---|---|
| Tier 0 | 身份参数：膜电容、门控方程、反转电位、基础电导、形态；固定 |
| Tier 1 | 接口/校准参数：刺激增益、反馈增益、噪声、读出增益；校准后冻结 |
| Tier 2 | 可塑状态变量：权重、资格迹、gmax 缩放、V1/2、受体池；随活动变化 |
| Tier 3 | 实验变量：条件、种子、会话长度、T1/T2；由实验设计决定 |
| STDP | Spike-Timing-Dependent Plasticity，脉冲时序依赖可塑性 |
| Eligibility trace | 资格迹：把“前后脉冲相关性”记在突触上，供延迟奖励使用 |
| Three-factor rule | 三因子规则：前活动 × 后活动 × 全局调制信号 |
| gmax | 通道最大电导，对应膜上通道密度 |
| V1/2 | 通道半激活电压，对应电压依赖性 |
| Homeostatic scaling | 稳态突触缩放：把平均放电率拉回目标值 |
| DishBrain | Kagan et al. 2022 的体外神经元闭环 Pong 系统 |
| T1 / T2 | DishBrain 的学习窗口：0–5 min / 6–20 min |
