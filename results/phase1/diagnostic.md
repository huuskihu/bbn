# Phase 1 Diagnostic: does the single-cell rate carry ball-y information?

- Duration per seed: 120.0 s
- Seeds: [0, 1, 2]
- Rallies with valid mid-approach: 43
- Mean rate: 14.3 ± 5.6 Hz

## Regression

| Predictor | slope | R² | Pearson r |
|---|---:|---:|---:|
| ball_y | -0.22 Hz/bin | 0.007 | -0.086 |

> ball_x 在中段窗口内方差很小，未做回归；Phase 1 基线已经显示率随球接近而升高（距离驱动）。

## Interpretation

细胞放电率对 ball_y 的依赖很弱（R² ≤ 0.2）。当前固定权重下，率读出主要被 ball_x（距离）和反馈刺激驱动，单细胞难以把“球在哪”转成“往哪动”。这不是 bug，而是单细胞率读出的结构性限制；阶段 3 应把它作为负结果的一部分，并在阶段 4 用两池差分读出（up/down）来消除共同驱动。

## Files

- `fig_diag_rate_vs_y.png`
- `fig_diag_weights.png`
