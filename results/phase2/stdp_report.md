# Phase 2.1 STDP Window

- A+ = 0.01, A− = 0.012
- τ+ = 20.0 ms, τ− = 20.0 ms
- Peak LTP: 0.00951
- Peak LTD: -0.01141
- Max deviation from theory: 5.53e-17

## Checks

- ltp_positive: PASS
- ltd_negative: PASS
- ltp_at_short_dt: PASS
- matches_theory: PASS

## Note

本测试只验证 pair-based 规则本身；细胞膜动力学与闭环整合在阶段 3 验证。
