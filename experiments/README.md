# 阶段 0 运行说明

> 这一步只做**基线细胞验证**，不训练、不涉及 Pong、不涉及可塑性。  
> 你运行完后，把 `results/phase0/` 整个目录（或其中的 `phase0_report.md` + `phase0_summary.json` + 三张 PNG）发回即可。

---

## 1. 环境

项目下已经创建了 `.venv`（Python 3.12）。如果它不存在，用：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install brian2 numpy matplotlib pandas pyyaml
```

---

## 2. 运行

在项目根目录 `d:\desktop files\code\machine_learning\bbn` 下：

```powershell
.\.venv\Scripts\python.exe experiments\phase0_baseline.py --config config\cell_pospischil_rs.yaml
```

可选参数：

```powershell
# 指定输出目录
.\.venv\Scripts\python.exe experiments\phase0_baseline.py --config config\cell_pospischil_rs.yaml --outdir results\phase0
```

---

## 3. 它会做什么

1. **静息电位**：I = 0，500 ms。
2. **输入电阻**：I = −0.05 nA，500 ms；用 ΔV/ΔI 算 Rin。
3. **f-I 曲线**：0–1.0 nA，步长 0.05 nA，每个电流 800 ms；统计最后 600 ms 的放电率。
4. **Rheobase**：在首次放电的电流附近用 0.005 nA 细化。
5. **单 spike 波形**：短脉冲诱发一个 spike，测峰值、幅度、半宽、AHP。
6. **Spike-frequency adaptation**：0.8 nA 持续 2 s，测首/末 ISI 与前后 300 ms 放电率。
7. **速度基准**：0.5 nA、1 s，记录墙钟耗时。

---

## 4. 输出

`results/phase0/`：

| 文件 | 内容 |
|---|---|
| `phase0_report.md` | 人类可读的指标表 + PASS/FAIL + 备注 |
| `phase0_summary.json` | 机器可读的全部数值 |
| `fi_curve.csv` | 每个电流的 spike 数与放电率 |
| `fig_fi_curve.png` | f-I 曲线 |
| `fig_spike_waveform.png` | 单 spike 波形 |
| `fig_adaptation.png` | 适应：V 轨迹 + 瞬时放电率 |
| `fig_rest_rin.png` | 静息与超极化轨迹 |

---

## 5. 预期判据

脚本会在报告里自动判 PASS/FAIL：

- 静息电位 −75…−65 mV；
- 输入电阻 25…45 MΩ（论文 34.5 MΩ）；
- rheobase 0.1…0.8 nA；
- spike 幅度 > 50 mV；
- spike 半宽 0.3…3.0 ms；
- ISI ratio > 1（有适应）；
- 0.8 nA 放电率 1…100 Hz。

**注意**：这些是“合理范围”，不是硬性通过线。即使某项 FAIL，也先把结果发回来，不要自己调参数去凑。

---

## 6. 常见问题

- **提示 Cython/编译器错误**：脚本已设置 `codegen_target: numpy`，不需要 C 编译器。若仍报错，把完整错误发回。
- **运行太慢**：先确认 `codegen_target` 是 `numpy`；阶段 0 的模拟量不大，通常几分钟量级。若明显更慢，把 `phase0_summary.json` 里的 `benchmark` 发回。
- **没有图**：确认 `results/phase0/` 目录存在；脚本会自动创建。
- **中文乱码**：图里的标签是英文，报告是 UTF-8；用 VS Code 打开即可。

---

## 7. 运行后请发回

优先发：

1. `results/phase0/phase0_report.md`
2. `results/phase0/phase0_summary.json`
3. `fig_fi_curve.png`、`fig_spike_waveform.png`、`fig_adaptation.png`

如果方便，直接压缩整个 `results/phase0/` 目录发回。
