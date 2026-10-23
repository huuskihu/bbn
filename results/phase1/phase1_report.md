# Phase 1 Static Baseline Report

- Config: `config\phase1.yaml`
- Duration per run: 120.0 s
- Seeds: [0, 1, 2]
- Conditions: ['full_feedback', 'no_feedback', 'silent', 'random_paddle', 'always_up', 'always_down']

## Summary by condition

| condition | hits | misses | avg rally | aces | long rallies | mean rate (Hz) | paddle range |
|---|---:|---:|---:|---:|---:|---:|---:|
| always_down | 3.3 | 56.7 | 0.06 ± 0.01 | 53.3 | 0.0 | 21.3 | 3.46 |
| always_up | 3.0 | 57.0 | 0.05 ± 0.03 | 54.3 | 0.0 | 21.3 | 3.46 |
| full_feedback | 2.3 | 12.0 | 0.19 ± 0.13 | 10.0 | 0.0 | 18.0 | 5.76 |
| no_feedback | 4.7 | 55.3 | 0.09 ± 0.06 | 51.0 | 0.0 | 21.3 | 6.03 |
| random_paddle | 9.7 | 50.3 | 0.19 ± 0.03 | 41.0 | 0.0 | 20.5 | 3.82 |
| silent | 3.7 | 19.3 | 0.19 ± 0.08 | 16.3 | 0.0 | 8.2 | 5.74 |

## Notes

- 本阶段没有可塑性；所有条件共用固定突触权重。
- `full_feedback` 命中给 100 Hz/100 ms 全通道可预测刺激；未命中给 5 Hz/4 s 随机不可预测刺激 + 4 s rest。
- `no_feedback` 不给任何反馈；`silent` 未命中只给 4 s rest；`random_paddle`/`always_up`/`always_down` 忽略细胞输出。
- 静态基线不应显示学习；它用来验证闭环、编码、读出和对照是否工作。
