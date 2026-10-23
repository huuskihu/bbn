# Phase 2.3 Homeostatic Scaling

- target = 20.0 Hz; α = 0.1
- bounds = [2.0, 80.0] nS

| start | final rate (Hz) | final drive (nS) | |error| (Hz) | within bounds |
|---|---:|---:|---:|---|
| high | 20.0 | 39.84 | 0.0 | PASS |
| low | 20.0 | 39.79 | 0.0 | PASS |

## Checks

- high converges within 5 Hz: PASS
- low converges within 5 Hz: PASS

## Note

本测试把 8 个感觉通道等效成一个总驱动电导；Phase 3 会对 8 个权重做同样的乘性缩放。
