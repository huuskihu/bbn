# Phase 0 Baseline Report

- Model: `pospischil2008_RS`
- Config: `config\cell_pospischil_rs.yaml`
- dt: 0.025 ms
- codegen target: `numpy`

## Metrics

| Metric | Value | Unit | Criterion | Pass |
|---|---:|---|---|---|
| v_rest_mV | -70.573 | mV | -75 to -65 | PASS |
| rin_mohm | 32.347 | MOhm | 25 to 45 (paper: 34.5) | PASS |
| rheobase_nA | 0.675 | nA | 0.1 to 0.8 | PASS |
| spike_amplitude_mV | 118.080 | mV | > 50 | PASS |
| spike_half_width_ms | 0.650 | ms | 0.3 to 3.0 | PASS |
| isi_ratio | 4.034 | last/first | > 1.0 (adaptation: ISI lengthens) | PASS |
| rate_at_0p8nA_hz | 10.000 | Hz | 1 to 100 | PASS |
| benchmark_wall_s_per_sim_s | 25.164 | s wall / s sim | report only | PASS |

## f-I curve

| current_nA | spikes | rate_hz |
|---:|---:|---:|
| 0.000 | 0 | 0.00 |
| 0.050 | 0 | 0.00 |
| 0.100 | 0 | 0.00 |
| 0.150 | 0 | 0.00 |
| 0.200 | 0 | 0.00 |
| 0.250 | 0 | 0.00 |
| 0.300 | 0 | 0.00 |
| 0.350 | 0 | 0.00 |
| 0.400 | 0 | 0.00 |
| 0.450 | 0 | 0.00 |
| 0.500 | 0 | 0.00 |
| 0.550 | 0 | 0.00 |
| 0.600 | 0 | 0.00 |
| 0.650 | 0 | 0.00 |
| 0.700 | 2 | 3.33 |
| 0.750 | 4 | 6.67 |
| 0.800 | 6 | 10.00 |
| 0.850 | 9 | 15.00 |
| 0.900 | 11 | 18.33 |
| 0.950 | 14 | 23.33 |
| 1.000 | 16 | 26.67 |

## Notes

- 参数来源：Pospischil et al. 2008, Fig. 1 caption; ModelDB 123623 `sPY_template`.
- 有效膜面积按论文的 0.29 nF / 34.5 MΩ 换算（2.9e-4 cm²），而非 ModelDB 注释里的 29000 µm²。
- E_K 采用 ModelDB 的 -100 mV；论文正文写 -90 mV。若 f-I 偏离，可在阶段 0 报告里对比。
- spike 计数使用 threshold=0 mV、reset v=-70 mV、refractory=2 ms；waveform 用无 threshold 的单独组。
- 本阶段不包含任何可塑性规则，不训练，不涉及 Pong。
