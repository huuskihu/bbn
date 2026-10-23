import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cell.hh_numba import HHParams
from src.env.pong import PongConfig
from src.loop.phase1_loop import Phase1Config, Phase1Loop

cell = HHParams()
pong = PongConfig()

print("wp   wu   hits misses avg_rally mean_rate paddle_range")
for wp in [2.0, 5.0, 10.0]:
    for wu in [30.0, 60.0, 100.0, 150.0]:
        cfg = Phase1Config(
            duration_s=10.0,
            predictable_weight_nS=wp,
            unpredictable_weight_nS=wu,
        )
        loop = Phase1Loop("full_feedback", cfg=cfg, cell_params=cell, pong_cfg=pong, seed=0)
        m, _ = loop.run()
        print(
            f"{wp:4.1f} {wu:5.1f} {m['hits']:4d} {m['misses']:6d} "
            f"{m['average_rally_length']:8.2f} {m['mean_rate_hz']:9.1f} {m['paddle_range']:12.2f}"
        )
