# 实验计划：阶段 0–5

> 本文是执行层计划：每个阶段做什么、交付什么、什么算通过、失败怎么办。
> 参数边界见 [parameter_policy.md](parameter_policy.md)；协议细节见 [protocol_and_biology.md](protocol_and_biology.md)。

---

## 0. 总原则

1. **先单细胞，后网络。** 阶段 3 没有报告，不进入阶段 4。
2. **先验证规则，再做闭环。** 每条可塑性规则先用配对脉冲/阶跃刺激验证，再放进游戏。
3. **先对照，再结论。** 任何“学习”声明必须有 no-feedback / silent / shuffled / static / random paddle 对照。
4. **预注册指标。** T1/T2、rally length、aces、long rallies 在看结果前固定；不挑 seed、不挑时间窗。
5. **负结果合法。** 失败要记录机制归因，不调参凑曲线。
6. **24 h 运行以 trial 级 checkpoint 为基础。** 随时可中断、可恢复。

---

## 阶段 0：环境与基线细胞

**目标**：拿到一个能稳定放电的单房室 HH 细胞，确认基线电生理与仿真速度。

### 任务

1. 建立 Python 3.12 venv（`uv`），安装 `brian2`、`numpy`、`matplotlib`、`pandas`、`pyyaml`。
2. 从 ModelDB 123623 取 Pospischil RS 参数，在 `src/cell/` 实现膜方程与门控。
3. 参数写入 `config/experiment_default.yaml` 的 Tier 0，计算 `config_hash`。
4. 验证：
   - 静息膜电位；
   - 输入电阻；
   - f-I 曲线（0–300 pA）；
   - 单动作电位波形；
   - ISI 适应；
   - rheobase。
5. 基准测试：1 个细胞、dt=0.1 ms、1000 ms 仿真耗时；记录 numpy / Cython 两种模式（若可用）。

### 交付物

- `experiments/phase0_baseline.py`
- `tests/test_cell_baseline.py`
- `results/phase0/baseline_report.md`
- `results/phase0/fig_*.png`

### 通过标准

- 4–40 Hz 稳定规则放电；
- 无数值爆炸；
- 单次 5 min 会话在可接受时间内完成（记录实际耗时）；
- Tier 0 参数全部有来源。

### 失败/停止条件

- 若模型无法稳定放电：检查门控方程/单位/初始条件，不要改参数去“凑”；
- 若速度不可接受：先尝试 dt=0.1 ms、简化监测；再考虑 MSVC Build Tools/Cython；最后才考虑 NEURON 3.12 对照。

---

## 阶段 1：Pong 环境 + 静态闭环

**目标**：在没有可塑性的情况下，把“感觉编码 → 细胞 → 运动解码 → 环境”跑通，建立基线。

### 任务

1. `src/env/`：Pong 环境（球 x/y、8 个 y 分箱、球拍、碰撞、命中/未命中、reset）。
2. `src/cell/`：8 个感觉突触（Poisson 输入 + AMPA 电导）。
3. `src/loop/`：10 ms tick；读取 spike；100 ms 窗口放电率；更新球拍；调度反馈。
4. 四种反馈：predictable / unpredictable / silent / no-feedback。
5. 固定随机权重，跑 5 min；统计基线 rally length、aces、long rallies。
6. 对照：always-up、always-down、random paddle、static cell。

### 校准（Tier 1）

| 参数 | 目标 |
|---|---|
| 感觉突触电导 | 4–40 Hz 编码驱动细胞产生 4–40 Hz 放电 |
| 反馈增益 | 可预测反馈引起可测的短时放电增加；不可预测反馈引起持续扰动 |
| 背景噪声 | 自发放电率 1–5 Hz，不完全静默 |
| 读出增益 | 球拍速度范围合理，不饱和卡死 |
| 目标放电率 | 默认 20 Hz，与 DishBrain gain 一致 |

校准完成后冻结，写入 config，记录 `config_hash`。

### 交付物

- `src/env/pong.py`、`src/loop/closed_loop.py`
- `experiments/phase1_static_loop.py`
- `results/phase1/baseline_performance.csv` + 轨迹图

### 通过标准

- 无崩溃；
- 静态细胞不优于 always-up/down 对照；
- 反馈刺激不会因为实现泄漏成“额外感觉输入”而破坏对照；
- 5 min 会话可重复（同 seed 同结果）。

### 失败/停止条件

- 若 always-up/down 也表现很好：说明任务太简单或读出有偏；先修任务/读出，不要进入阶段 2。

---

## 阶段 2：可塑性模块 + 规则验证

**目标**：让细胞“可学习”，并先证明每条规则单独正确。

### 任务

1. **STDP**：pair-based，\(A_+,A_-,\tau_+,\tau_-\)；验证 \(\Delta w\) vs \(\Delta t\) 的非对称窗口（−50…+50 ms）；权重 clip。
2. **资格迹**：指数衰减 + STDP 事件；验证延迟奖励能作用到正确的突触。
3. **稳态缩放**：目标 20 Hz，时间常数 10–60 s；验证阶跃刺激后放电率收敛。
4. **内在可塑性**：O'Leary 简化规则；\(s_i\in[0.8,1.2]\)，\(\delta_i\in[-5,5]\) mV；验证参数不越界。
5. **受体池（可选）**：表面/胞内池，活动依赖内吞/外排；验证池守恒。
6. 单元测试/规则测试：`tests/test_stdp_window.py`、`test_homeostasis.py`、`test_intrinsic.py`。

### 交付物

- `src/plasticity/*.py`
- `tests/test_*.py`
- `results/phase2/fig_stdp_window.png`、`fig_rate_convergence.png`、`fig_gmax_trajectory.png`

### 通过标准

- STDP 窗口形状正确（pre-before-post → LTP，post-before-pre → LTD）；
- 阶跃刺激后放电率收敛到目标 ± 合理误差；
- 无持续振荡；
- 所有 Tier 2 变量在边界内；
- 关闭可塑性时行为与阶段 1 一致。

### 失败/停止条件

- 若 STDP 窗口不对称或符号反了：先修实现，不要进入闭环；
- 若稳态缩放导致振荡：降低增益/延长 τ，记录依据；
- 若内在可塑性把细胞变成另一类细胞：缩小边界，报告。

---

## 阶段 3：单细胞闭环学习（核心）

**目标**：回答“一个细胞在闭环反馈下能否产生有方向性的适应”。

### 3.1 两个条件

| 条件 | 可塑性 | 反馈的作用 | 预期 |
|---|---|---|---|
| **3a 字面 DishBrain** | STDP + 稳态 | 只作为刺激，不作为奖励信号 | 弱/无位置特异性；可能整体兴奋性漂移 |
| **3b 三因子** | STDP + 资格迹 + 三因子 + 稳态 | 可预测 → \(D>0\)；不可预测 → \(D<0\) | 主实验；可能出现方向性权重梯度 |

### 3.2 对照

| 对照 | 目的 |
|---|---|
| no-feedback | 排除“感觉刺激本身”导致的变化 |
| silent | 排除“只要有中断就学习” |
| shuffled feedback | 排除“反馈与动作无关”也能学习 |
| static cell | 排除“固定细胞也会漂移” |
| random paddle | 排除“球拍随机也会碰巧得分” |
| always-up / always-down | 排除“固定策略” |

### 3.3 规模

- 10–20 个随机种子/条件；
- 每个 session 5–20 min；
- T1 = 0–5 min，T2 = 6–20 min；
- 每个 run 独立进程；24 核并行 8–12 个。

### 3.4 指标

**主指标**

- average rally length（T1 vs T2）；
- aces（0 hit 的 rally 数）；
- long rallies（>3 consecutive hits）。

**次指标**

- 球拍-球对齐误差（impact 时刻）；
- 球拍覆盖率（避免卡在一边）；
- 动作熵 / 放电率分布；
- 权重单调性（8 个感觉通道的权重是否形成梯度）；
- \(s_i,\delta_i\) 轨迹；
- spike-triggered average of sensory input；
- 信息熵（100 ms bin，参考 DishBrain）。

### 3.5 交付物

- `experiments/phase3_single_cell.py`
- `results/phase3/learning_curves.png`
- `results/phase3/summary.csv`
- `results/phase3/report.md`（含负结果）

### 通过标准

- 3b 的 T2−T1 显著优于对照，效应量可报告；
- 权重/参数变化方向与“提高命中率”一致（例如权重梯度单调化）；
- 结果在多种子上可重复（至少方向一致）。

### 失败/停止条件

- 若 3b 无效应：不要网格搜索；先做机制归因（见下）；
- 若 3a 有效、3b 无效：检查 \(D(t)\) 的符号/时间对齐；
- 若两者都无效：考虑进入阶段 4（两细胞）之前，先确认读出基准与任务可学性。

### 3.6 失败归因清单

1. 感觉驱动是否足以产生 4–40 Hz？  
2. 20 Hz 参考是否与细胞基线匹配？  
3. 反馈是否在动作之后足够近（资格迹窗口内）？  
4. 稳态是否把权重拉平？  
5. 权重边界是否过早饱和？  
6. 任务是否本身不可学（单细胞只有一维输出）？  
7. 是否存在平凡解（always-up）？  

---

## 阶段 4：极小网络

**目标**：探索“涌现”的最低门槛；比较单细胞 vs 2–5 细胞；稳定后再决定是否扩到 ~12。

### 任务

1. 2 个 motor 细胞（up/down）+ 可选 1 个抑制性中间神经元；感觉输入到所有细胞。
2. 保留阶段 2 的 STDP、稳态、内在可塑性。
3. 同一套 Pong 协议；同一套对照。
4. 指标：rally length、排他性运动事件、两 motor 细胞相关性的时间演化、权重矩阵、同步性。
5. 若 2–5 细胞稳定且有趣，再扩到 ~12；否则停在 2–5，报告。

### 交付物

- `src/` 网络扩展
- `experiments/phase4_network.py`
- `results/phase4/phase4_report.md`（行为、读出信息量、权重演化、配对统计、机制解释）
- 权重演化图、差分率–位置散点、各条件行为对比图

### 通过标准

- 网络不差于单细胞；
- 若出现 motor 分化/排他性事件增加，记录为“最小涌现”证据；
- 若网络更差，分析原因（过度同步、抑制不足、权重失控）。

### 失败/停止条件

- 若网络只产生全局同步、无分化：先检查抑制连接与稳态；不要盲目加细胞数。

---

## 阶段 5：可选扩展与最终报告

**可选扩展**（按兴趣和时间）：

- 受体转运池（AMPA 表面/胞内）；
- 胶质样慢调制；
- 结构可塑性（突触生成/修剪）；
- 不同细胞类型（FS/IB）作为对照；
- 不同反馈统计（概率、延迟、幅度）。

**最终报告结构**：

1. 问题与动机；
2. 模型与参数政策；
3. 协议与对照；
4. 结果（含负结果）；
5. 机制解释；
6. 局限与诚实声明；
7. 复现步骤与配置哈希；
8. 附录：所有图、表、参数变更日志。

---

## 4. 指标与统计

### 4.1 预注册

在看结果前写入 `config/experiment_default.yaml`：

- 主指标：average rally length、aces、long rallies；
- T1/T2 定义；
- 排除标准：前 10 s 初始化噪声；异常 run（如崩溃、NaN）；
- 对照列表；
- 统计方法。

### 4.2 统计方法

- 每个种子内：配对 t 检验 / Wilcoxon（T1 vs T2）；
- 跨种子：线性混合效应模型（condition × time，随机截距 seed）；
- 效应量：Cohen's d / Cliff's delta；
- 置信区间：bootstrap 10,000 次；
- 多重比较：Bonferroni 或 FDR；
- 报告：均值 ± 95% CI，不只报 p 值。

### 4.3 反自欺检查

- 是否只报了“好看”的 seed？
- 是否换了时间窗？
- 是否在看完结果后改了指标？
- 是否把“整体放电率漂移”误当成“位置特异性学习”？
- 是否把“球拍卡在一边”误当成“策略”？
- 是否把“模型参数漂移”误当成“学习”？

---

## 5. 断点续跑与 24 h 运行

### 5.1 run 结构

```text
runs/
└─ <run_id>/
   ├─ manifest.json       # 状态、config_hash、seed、进度、指标摘要
   ├─ checkpoint.npz      # trial 级断点
   ├─ run.log             # 日志
   └─ metrics.csv         # 每个 trial/session 的指标
```

### 5.2 checkpoint 内容

见 [HANDOFF.md](../HANDOFF.md) §7。核心：时间、游戏状态、细胞状态、可塑变量、RNG、指标、config_hash。

### 5.3 保存策略

- 每 30 s 仿真或每个 trial 结束；
- 先写 `.tmp.npz`，再 `os.replace`；
- 捕获 `KeyboardInterrupt` / `SIGTERM`，保存后退出；
- `--max-wall-hours` 到点优雅停止；
- 直接断电最坏丢失一个 checkpoint 间隔（默认 30 s）。

### 5.4 恢复

```powershell
python experiments\phase3_single_cell.py --run-id <run_id> --resume
```

- 校验 `config_hash`；
- 重建网络（同 seed）；
- 恢复状态与 RNG；
- 从 `t_sim_s` 继续。

### 5.5 并行

- 24 核：8–12 个单线程进程；
- 每个 run 独立目录，避免文件竞争；
- `runs/queue.json` 管理待跑/已完成；
- 关机前运行停止脚本，确保所有 run 保存。

---

## 6. 报告模板

```markdown
# Phase X Report

## 1. 目的
## 2. 配置（config_hash, seed, condition）
## 3. 结果
- 主指标表
- 图
## 4. 对照
## 5. 机制解释
## 6. 负结果/异常
## 7. 下一步
```

---

## 7. 预注册检查清单（阶段 3 开始前）

- [ ] 主指标、次指标已写入 config
- [ ] T1/T2 定义已固定
- [ ] 对照条件已固定
- [ ] 种子数已固定
- [ ] 排除标准已固定
- [ ] 统计方法已固定
- [ ] Tier 1 已冻结，config_hash 已记录
- [ ] 没有“看完结果再改”的入口
