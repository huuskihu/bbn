# 工作交接：BBN 项目（交接给接任 AI / 协作者）

**交接时间**：2026-11-09
**项目版本**：v0.22.0-phase7-recurrent-ei
**仓库**：https://github.com/huuskihu/bbn
**本地路径**：`D:\desktopfiles\code\machine_learning\bbn`

> 面向接手的 AI：只写现在是什么状态、东西在哪、怎么跑、哪些坑不能踩。
> 方法学长文在 `README.md`；逐阶段预注册与结果在 `HANDOFF.md` §6M–§6T；
> 参数边界在 `docs/parameter_policy.md`；成稿在 `results/final_report.md`（PDF 同目录）。

---

## 0. 30 秒速览

- 计算神经科学的**负结果项目**：Pospischil 2008 RS 单房室 HH 细胞，按 DishBrain 协议玩简化 Pong，
  检验"纯局部可塑性能否产生闭环适应"。
- **八条机制线全部跑完并全部关闭**（P0–P5、6a、7a）。科学上已结束，没有待跑实验。
- **结论**：行为上限由读出结构、信息到达时刻与执行器增益决定；改可塑性、稳态、动力学、规模、接口、
  输入编码、递归拓扑都无法突破手工 push-pull 结构（2 细胞 static = 0.204 rally）。
- **剩下的只有写作与发布**：negative-results 论文、可选数据包（Zenodo/OSF）、可选新项目（>100 细胞）。
- 环境已在本机验证（5 s 冒烟跑通）；仓库与 GitHub 同步、工作区干净。

---

## 1. 项目是什么，以及不能违反的红线

### 1.1 科学问题

> 在 1–22 个细胞、只用局部可塑性规则的条件下，能否复现 DishBrain 式的闭环适应？如果不能，瓶颈在哪里？

### 1.2 红线（违反即失去项目合法性）

1. **不是 ML 项目**：禁止反向传播、禁止全局损失、禁止用梯度/搜索调参去拟合成绩。
2. **可塑性必须局部且生理可解释**：STDP、资格迹、稳态缩放、短时程可塑性（Tsodyks–Markram）。
3. **Tier 0 细胞身份参数固定**：`C_m`、门控方程、反转电位、基础电导，不许为了成绩改动。
4. **Tier 1 接口参数校准一次后冻结**：感觉突触电导、反馈增益、噪声、读出增益、目标率。
5. **任何机制改动必须先预注册**：写进 `HANDOFF.md` 新小节（机制、参数、网格、Gate、停止规则），然后才实现。
6. **负结果必须如实记录**：触发停止规则就停止，不许"再调一下试试"。
7. **实现 bug 不隐藏**：错误批次改名归档、在报告里写清楚，不参与推断。

### 1.3 参数分层

| 层级 | 内容 | 规则 |
|---|---|---|
| Tier 0 | 膜电容、门控、反转电位、基础电导 | 锁定 |
| Tier 1 | 感觉突触权重、反馈权重、背景噪声、读出增益、目标率 | 校准一次后冻结，各条件共用 |
| Tier 2 | 突触权重、资格迹、稳态缩放、STP 状态 | 随活动按局部规则变化 |
| Tier 3 | 条件、种子、会话长度、反馈类型 | 实验设计决定 |

---

## 2. 当前状态

### 2.1 已完成

| 阶段 | 内容 | 结果 | 状态 |
|---|---|---|---|
| 0 | 细胞基线（Brian 2） | f-I、Rin、rheobase、spike、适应全部 PASS | 完成 |
| 1 | 单细胞静态闭环 | 率→ball_y 回归 R²=0.007，slope −0.22 Hz/bin | 完成（负） |
| 2 | STDP / 资格迹 / 稳态验证 | 窗口、收敛、边界全部 PASS | 完成 |
| 3 | 单细胞三因子学习 | 3a/3b 与 static/random 无差异；修复 rest 锁死 bug 后重跑 | 完成（负） |
| 4 | 2 细胞 push-pull | static 0.204 vs symmetric 0.162 vs random 0.125（p=0.016 / 0.0002） | 完成（结构正结果） |
| 4a–4e | 增益敏感性、恒定率、三种抑制、慢球、归一化 | 均未改善行为 | 完成（负） |
| 5 P0 | 背景噪声 3 Hz / 80 nS | quiet-rest 4.6 Hz，但 3b 仍饱和（at_max 0.40） | 完成（负） |
| 5 P1 | 局部信用（Miss 按球侧 ±1） | 梯度 0.000→0.780（p=0.014），行为 0.220（p=0.512） | 完成（梯度正 / 行为负） |
| 5 P2 | 动态稳态带 [5,30] Hz | at_max 0.34→0.14、impact 0.179→0.381，行为 0.196（p=0.643） | 完成（负） |
| 5 P3 | Tsodyks–Markram STP | early 0.569→0.699、gap 0.171→0.118、impact→0.809，行为 0.187（p=0.243） | 完成（机制正 / 行为负） |
| 5 P4 | 10 细胞 E/I 前馈 | net_static 0.203（p=0.990）、impact 0.920→0.479、net_local 0.127（p=0.005） | 完成（负） |
| 5 P5 | PD 读出 τ_pred=50 ms | local_pd 0.220 ≡ local_no_hs（p=0.998） | 完成（负） |
| 6a | 帧式延迟编码（开环 Gate） | corr(Δt, ball_y)=0.442 < 0.5，Δt P95 4.0 ms | Gate 不通过 → A 线关闭 |
| 7a | 22 细胞递归 E-I（Gate） | E 率 3.67 / 4.07 / 158.0 / 253.2 Hz，网格内无 5–25 Hz | Gate 不通过 → B 线永久关闭 |

### 2.2 明确关闭、不要再开的线

背景噪声、局部信用、动态稳态带、STP 作为行为杠杆、10 细胞扩网络、PD 读出、帧式延迟编码、递归 E-I。
每条都有预注册与硬停止记录，见 `HANDOFF.md` §6P–§6T。

### 2.3 尚未完成（可选，不属于"补实验"）

1. **论文**：把八条负结果 + 两条正结果（结构、局部梯度）写成 negative-results 稿。
2. **数据发布（可选）**：把 2.9 GB 原始 traces/impacts/weights 打包到 Zenodo/OSF，拿 DOI，
   补进 `README.md` §10A（已留"若已发布，在此补充 DOI"的位置）。
3. **新项目（可选，超出本项目范围）**：>100 细胞、E/I 平衡可塑、临界动力学的群体模型，需重新预注册。

---

## 3. 关键数字（直接引用，不要重算）

> 来自 `results/*/summary_by_condition.csv`；行为指标为 600 s × 15 seeds 的平均 rally；
> Gate 阶段为 60 s × 3–5 seeds。

| 条件 / 对比 | 数字 | 含义 |
|---|---|---|
| 2 细胞 static | 0.204 ± 0.043 | 手工 push-pull 基线 |
| 2 细胞 symmetric | 0.162 | 零差分对照 |
| random paddle | 0.125 | 随机拍对照 |
| 单细胞率 → ball_y | R²=0.007 | 单细胞率几乎不含位置信息 |
| push-pull impact corr | ≈0.92 | 差分读出确实携带位置信息 |
| P1 `w_diff corr` | 0.000 → 0.780 | 局部信用形成正确梯度 |
| P1 行为 | 0.220（p=0.512） | 未超过 static |
| P2 `at w_max` | 0.34 → 0.14 | 饱和减半 |
| P3 early / late 差 | 0.171 → 0.118 | 时间形状被 STP 改变 |
| P3 impact corr | 0.735 → 0.809 | 2 细胞可塑臂最好信息水平 |
| P3 行为 | 0.187（p=0.243） | 命令幅度减半抵消 |
| P4 net_static | 0.203（p=0.990） | 规模不改变静态行为 |
| P4 impact corr | 0.920 → 0.479 | 8→2 压缩导致信息减半 |
| P4 net_local | 0.127（p=0.005） | 可塑性在更大网络里更差 |
| P5 PD | 0.220 ≡ 0.220（p=0.998） | 50 ms 微分补偿无效 |
| 6a corr(Δt, ball_y) | 0.442 | 未过 0.5 Gate |
| 7a E 率（w_ee=0/5/10/20） | 3.67 / 4.07 / 158.0 / 253.2 Hz | 双稳态，无中间工作点 |
| 7a w_ee=10 两两相关 / 漂移 | 0.898 / 0.302 | 同步化 + 漂移，非 AI 态 |

**一句话结论**：信息质量（impact corr 0.0–0.92）与行为（0.13–0.22）之间没有单调关系；
限制在"信息到达时刻 + 执行器增益 + 读出结构"。

---

## 4. 仓库、环境与运维

### 4.1 路径变更（重要）

项目原来在 `D:\desktop files\code\machine_learning\bbn`，**现在已移动到**：

```
D:\desktopfiles\code\machine_learning\bbn
```

旧文档里可能还有 `D:\desktop files\...` 的历史表述；以实际路径为准。移动后已做 5 s 冒烟验证，可正常运行。

### 4.2 环境

| 项 | 值 |
|---|---|
| Python | 3.12.14（`.venv`） |
| 关键包 | numpy 2.5.4、pandas 3.0.6、numba 0.68.0、brian2、matplotlib、pyyaml、markdown、pymupdf |
| 额外工具 | `git-filter-repo`（已装进 venv，历史改写用过） |
| PDF 导出 | 需要 Microsoft Edge 或 Chrome；可用 `EDGE_PATH` 指定可执行文件 |

```powershell
cd "D:\desktopfiles\code\machine_learning\bbn"
.\.venv\Scripts\Activate.ps1        # 或直接调用 .\.venv\Scripts\python.exe
```

若 `.venv` 丢失：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install brian2 numpy matplotlib pandas pyyaml numba markdown pymupdf
```

### 4.3 Git / GitHub

- 远程：`git@github.com:huuskihu/bbn.git`（**SSH**；本机访问 `https://github.com` 会超时）
- 分支：`main`；当前与 `origin/main` 同步，工作区干净
- 提交历史：`fe793fc`（干净初始提交）→ `aae1d5d` paper → `b69b4b4` papers → `ebfb0c0` aaa →
  `3ed1c8c` / `cddc6bf` / `78e9879` / `9a3b6d5`（自动 update，由 `03-更新云端.bat` 产生）
- 根目录的 `03-更新云端.bat`：`git add -A` → 有改动则 `commit -m "update <日期> <时间>"` → `git push`。
  **接任者提交时请写有意义的 message，不要继续用 `aaa` / `paper` / 自动时间戳。**

### 4.4 沙箱注意

本机执行工具对 `results/` 写入曾报 `PermissionError`。若命令行写结果失败，
需要以"关闭沙箱"的方式运行（本环境的历史事实，不是权限设计）。

---

## 5. 代码地图

```
src/cell/hh_numba.py          FastHH：Pospischil RS 单房室 HH，Numba RK4（dt=0.01 ms）
src/env/pong.py               Pong 环境、球速、命中/失球判定
src/plasticity/stdp.py        STDP 窗 + 资格迹 + 三因子
src/plasticity/homeostasis.py 稳态缩放（支持固定点与 [5,30] Hz 功能带）
src/loop/phase1_loop.py       单细胞静态闭环
src/loop/phase3_loop.py       单细胞三因子学习
src/loop/phase4_loop.py       主引擎：2/10/22 细胞、全部机制开关（70 KB，核心）
experiments/phase0_baseline.py      细胞基线
experiments/phase1_*.py             静态闭环 / 诊断
experiments/phase2_*.py             STDP / 资格迹 / 稳态验证
experiments/phase3_single_cell.py   单细胞学习
experiments/phase4_network.py       所有网络实验入口（--conditions / --outdir / --jobs）
experiments/final_summary_figures.py 汇总图（只读 summary CSV）
experiments/export_report_pdf.py     Markdown → HTML → PDF（Edge headless）
tests/calibrate_phase1.py, tests/debug_numba.py
config/*.yaml                 Tier 0/1 参数、条件列表、种子
```

### 5.1 `src/loop/phase4_loop.py` 结构（行号基于 v0.22.0）

| 位置 | 内容 |
|---|---|
| L45 | `Phase4Config(Phase3Config)`：所有机制参数（net/rec/lat/pd/stp/背景等） |
| L103 | `_Pool`：一个 motor 池（细胞 + 可塑突触 + 稳态 + STP 状态 + 率窗口） |
| L127 | `Phase4Loop`：条件解析、细胞/网络构建 |
| L147–L188 | 条件名驱动机制开关（见 §6） |
| L367 | `_make_pool()` |
| L387 | `_init_weights()`：push-pull / symmetric / random；`net` 与 `rec` 分支 |
| L415 | `_sensory_events()`：8 通道高斯位置编码 |
| L437 | `_rec_background()`：递归网络每细胞独立 3 Hz 背景 |
| L445 | `_queue_latency_volley()`：6a 帧式延迟事件 |
| L458 | `_feedback_events()`：命中/失球反馈调度 |
| L478 | `_background_events()`：2 细胞/10 细胞背景 |
| L492 | `_stp_sensory_weights()`：Tsodyks–Markram |
| L549 | `_action()`：random → latency → normalized → PD → 比例读出 |
| L568 | `_process_plasticity()`：STDP + 资格迹 + 三因子 |
| L589 | `_apply_homeostasis()`：稳态（可在 play 期、可功能带） |
| L606 | `run()`：主循环，返回 `(metrics, trace, impacts, weights)` |

### 5.2 输出

每次 run 写 `<outdir>/{traces,impacts,weights}/<condition>_seed<k>.csv`，
以及 `summary.csv`（每 seed 一行）、`summary_by_condition.csv`（条件均值/SD）、
`phase4_report.md`（自动报告）、三张自动图。

---

## 6. 条件命名系统（最容易踩坑的地方）

机制**由条件字符串里的关键字开启**，不是由 CLI 全局开关。解析在 `Phase4Loop.__init__`：

| 关键字 | 机制 |
|---|---|
| `pushpull` / `symmetric` / `random` | 初始权重结构 |
| `3b` | 三因子 STDP + 资格迹 + 稳态（全局 D） |
| `local` | 池特异信用（Miss 按球侧给 `D_up/D_down=±1`） |
| `no_hs` | 关闭稳态 |
| `play_hs` | 只在 play 期稳态 |
| `dyn` | 稳态目标改为功能带 `[5,30] Hz`（仅 play） |
| `stp` | 短时程可塑性 |
| `net` | 10 细胞前馈 S→E/I→M |
| `pd` | PD 读出（`τ_pred=50 ms`） |
| `lat` | 帧式延迟编码 |
| `frozen` | 冻结球拍（开环测量） |
| `rec` | 22 细胞递归 E-I |

### 6.1 历史坑（已发生，勿重犯）

1. **全局 CLI 开关污染对照臂**：早期用 `--local-credit` 全局开关，导致同批 `3b` 也变成局部信用，
   两臂逐位相同。已改为条件名驱动，污染批次归档在 `results/phase5_local_credit_600_bug_globalflag/`。
   **新增机制时，一律用条件名解析，不要加全局 flag。**
2. **`rec` 的"上一 tick"必须快照**：E 细胞按顺序运行，若直接读 `self.prev_rec_e`，
   已运行的 pre 细胞会被本 tick 覆盖，递归退化为零延迟。实现里已改为循环前快照
   （`prev_e_snap` / `prev_i_snap`）。改这段代码时不要破坏快照。
3. **指标口径必须 play-only**：rest 是人工超时，纳入统计会污染放电率、ISI 的 CV、前后半段漂移。
   `net_*_rate_hz`、`rec_*_rate_hz` 都只按 play 段统计；I 率的分母与分子都要过滤。
4. **`_corr` 要求 ≥3 个有限点**，否则返回 0。因此 2 通道网络的 `w_diff corr` 恒为 0，
   P4 的判据改用行为与 impact corr。
5. **`net` / `rec` 模式下 motor 不接原始感觉事件**：只接 E spike（可塑权重）+ 反馈事件。
   这是 Tier 1 接口定义，不要"顺手"把感觉事件加回去。

---

## 7. 怎么跑（复现）

所有网络实验都走同一个入口：

```powershell
.\.venv\Scripts\python.exe experiments\phase4_network.py `
  --config config\phase4.yaml --jobs 10 --duration 600 --trace-stride 10 `
  --conditions phase4_pushpull_static,phase4_pushpull_3b_no_hs `
  --outdir results\phase4_600
```

- `--jobs`：并行 `(condition, seed)` 进程数，不要超过物理核数。
- `--trace-stride 10`：trace 降采样 10 倍，体积/速度友好（metrics 仍用全量）。
- 6a 延迟编码：`--conditions ..._lat_frozen --lat-gain <值>`
- 7a 递归：`--conditions rec_static --rec-ee-weight {0,5,10,20}`
- 2 细胞主结果：`results/phase4_600`（600 s × 15 seeds）
- 汇总图：`python experiments/final_summary_figures.py`
- PDF：`python experiments/export_report_pdf.py`（生成 `results/final_report.pdf`；HTML 中间文件被 gitignore）

**冒烟（30 秒内）**：

```powershell
.\.venv\Scripts\python.exe experiments\phase4_network.py --outdir results\_smoke_check `
  --conditions phase4_pushpull_static,rec_static --seeds 0 --duration 5 --rec-ee-weight 5
```

期望：`phase4_pushpull_static` 命中 2 次左右；`rec_static` E 率约 5 Hz 量级，
`rec_e_cv_isi ≈ 0.98`、`rec_e_pair_corr ≈ 0.2`。跑完删掉 `results\_smoke_check`。

耗时参考：2 细胞 600 s 单 run 约 20–40 s；10 细胞约 2–3 倍；22 细胞递归约 4–6 倍。

---

## 8. 结果目录与文档

### 8.1 `results/`

| 目录 | 内容 |
|---|---|
| `phase0` … `phase4` | 各基础阶段 |
| `phase4_600` | 2 细胞 600 s 主结果 |
| `phase4_gain030/060`、`phase4_const_rate_600` | 4a/4b 敏感性 |
| `phase4_inhibition_600`、`phase4_cross_inhibition_600`、`phase4_tuned_inhibition_600` | 4c 三种抑制 |
| `phase4_slow_ball_600`、`phase4_norm_readout_600` | 4d/4e |
| `phase5_bg_noise_600` … `phase5_pd_readout_600` | P0–P5 |
| `phase6a_latency` | 6a |
| `phase7_7a/{w0,w5,w10,w20}` | 7a 最终数据 |
| `phase7_7a_bug_zerodelay`、`phase7_7a_metric_overall`、`phase7_7a_bug_i_rate_unfiltered` | **已作废批次，不参与推断** |
| `phase5_local_credit_600_bug_globalflag` | **已作废批次（全局开关污染）** |
| `figures/` | 7 张汇总图（protocol / rally / conditions / info / timing / saturation / rec_ei） |

### 8.2 报告

- `results/final_report.md` + `final_report.pdf`：成稿，含摘要、方法、逐阶段结果、7 张图、讨论、局限、复现、附录
- `results/phase*_report.md`：逐阶段细节
- `HANDOFF.md` §6M–§6T：每阶段的预注册（机制、参数、网格、Gate、停止规则）与结果
- `docs/parameter_policy.md`：Tier 0–3 与每次参数变更的原因、影响、是否重跑

---

## 9. 数据策略

- **已上传**：`summary.csv`（46 份，每 seed 一行）、`summary_by_condition.csv`（46 份）、
  报告、图、代码、配置、预注册。
- **未上传**（`.gitignore` 排除，约 2.9 GB）：`results/**/traces/`（1,920 个，2,691 MB）、
  `impacts/`（1,724 个，7.1 MB）、`weights/`（1,724 个，185 MB）。
  原因只有体积，不含个人信息；获取方式写在 `README.md` §10A。
- 若要发布数据包：优先 Zenodo/OSF（可给 DOI），不要塞进 Git 历史。

---

## 10. 已入库但需要知道的两件事

1. **`习题详解/`（3 个 PDF，约 15 MB）**：高等数学/线性代数习题解答，与项目无关。
   owner 明确选择保留在仓库里；**不要擅自删除**，也不要再往仓库加同类大文件。
2. **`papers` 提交里有一个 30 MB 的 DishBrain 论文 PDF**（"…when embodied in a simulated game-world"）。
   `reference/` 已在 `.gitignore` 中，但这个文件被单独提交了。若未来做仓库瘦身，需 owner 同意后处理历史。

---

## 11. 接手后的动作清单

### 11.1 先做（10 分钟）

1. 读 `README.md`（项目定位、设计决策、路线图）。
2. 读 `HANDOFF.md` §1 状态表 + §6M–§6T（预注册与硬停止）。
3. 读 `results/final_report.md`（结论与数字）。
4. 跑 §7 的冒烟命令，确认环境正常。
5. `git status` 应为干净；`git log --oneline -3` 看最新提交。

### 11.2 不要做

- 不要重跑已关闭的八条机制线，不要"换个参数再试一次"（违反预注册与停止规则）。
- 不要改 Tier 0，不要扩大 7a 的 `w_ee` 网格。
- 不要用全局 CLI 开关加机制（会污染对照臂）。
- 不要 `git push --force`，不要改写历史。
- 不要把 `results/**/traces|impacts|weights` 加回仓库。
- 不要把本机绝对路径、用户名、硬件配置写回 README/文档（已清理过一次，历史也清理过）。

### 11.3 可选的三条路线（按推荐顺序）

**A. 写论文（最推荐，零新实验）**
- 定位：negative results + 机制归因。八条线都有预注册与停止记录，方法学本身是贡献。
- 素材：`final_report.md` 的 7 张图 + 各阶段 summary CSV；两条正结果（结构 > 可塑性、局部信用梯度）。
- 需要补：相关工作（DishBrain、STDP/三因子、稳态、临界动力学）、LaTeX/Word 排版、
  Limitations 里明确"极小网络 + 纯局部规则"的边界。

**B. 数据/代码发布（低成本）**
- 把 2.9 GB 原始输出打包上传 Zenodo，拿 DOI，补进 `README.md` §10A。
- 加 `CITATION.cff`、`LICENSE`（需 owner 决定许可证）。

**C. 继续做科学（成本最高，需新预注册）**
- 直接跳到 >100 细胞群体模型（E/I 平衡、临界动力学、抑制可塑），不要继续在 2–22 细胞加机制。
- 或改任务层：显式速度/预测编码 + PD 控制，先把"信息到达时刻 + 执行器增益"这条控制链路做对。
- 无论哪条，都必须在 `HANDOFF.md` 开新小节预注册，并遵守 §1.2 的红线。

---

## 12. 验证清单（复制即用）

```powershell
cd "D:\desktopfiles\code\machine_learning\bbn"

# 1) 仓库状态
git status --short           # 期望：空
git log --oneline -3
git remote -v                # 期望：git@github.com:huuskihu/bbn.git

# 2) 环境
.\.venv\Scripts\python.exe -c "import sys,numpy,pandas,numba;print(sys.version.split()[0])"

# 3) 冒烟
.\.venv\Scripts\python.exe experiments\phase4_network.py --outdir results\_smoke_check `
  --conditions phase4_pushpull_static,rec_static --seeds 0 --duration 5 --rec-ee-weight 5
Remove-Item -Recurse -Force results\_smoke_check

# 4) 重生成汇总图与 PDF（只读结果，不重跑仿真）
.\.venv\Scripts\python.exe experiments\final_summary_figures.py
.\.venv\Scripts\python.exe experiments\export_report_pdf.py
```

---

## 13. 关键文件优先级

**必读（按顺序）**

1. `README.md` — 项目定位、硬约束、设计决策、路线图、复现命令、数据可用性
2. `HANDOFF.md` — §1 状态表、§2 已拍板决定、§6M–§6T 预注册与停止规则
3. `results/final_report.md` — 成稿结论、7 张图、逐阶段数字
4. `docs/parameter_policy.md` — Tier 0–3 与参数变更日志
5. `src/loop/phase4_loop.py` — 主引擎（先看条件解析与 `run()`）

**改动前必读**

- `docs/protocol_and_biology.md` — DishBrain 参数、生物映射、简化与局限
- `docs/experiment_plan.md` — 阶段任务、对照、指标、统计、checkpoint/resume
- `config/phase4.yaml` — 条件列表与种子

---

## 14. 联系与归属

- 仓库 owner：GitHub `huuskihu`
- 提交身份：`huuskihu <13426193+huuskihu_admin@user.noreply.gitee.com>`
- 所有结果由固定 seed 生成，可逐位复现；条件间 RNG 流不共享。
- 引用与许可尚未确定（无 `LICENSE`、无 `CITATION.cff`），发布前需 owner 决定。

---

## 附：一页式状态卡（可直接贴进新会话开头）

```
项目：BBN（DishBrain 式闭环学习，负结果）
版本：v0.22.0-phase7-recurrent-ei
路径：D:\desktopfiles\code\machine_learning\bbn
远程：git@github.com:huuskihu/bbn.git（SSH；HTTPS 超时）
状态：8 条机制线全部关闭；无待跑实验；剩写作/发布
结论：行为上限 = 读出结构 + 信息到达时刻 + 执行器增益
数字：static 0.204；P1 0.220(p=.512)；P3 0.187(p=.243)；P5 ≡(p=.998)；6a .442；7a 3.7/4.1/158/253 Hz
红线：无 BP/全局损失；Tier0 固定；先预注册；负结果如实记录；不改写历史
入口：experiments/phase4_network.py --conditions ... --outdir ...
文档：README → HANDOFF §6M–§6T → results/final_report.md → docs/parameter_policy.md
```
