import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cell.hh_numba import HHParams, rates, run_spikes

p = HHParams()
m0, _, h0, _, n0, _, p0, _ = rates(-70.0, p.V_T, p.tau_max)
g = np.zeros(8, dtype=np.float64)
st = np.zeros(1000, dtype=np.float64)

print("start", flush=True)
t0 = time.perf_counter()
out = run_spikes(
    -70.0, m0, h0, n0, p0, g,
    0.0, 10, 0.01, 0.8 * 1000.0,
    p.C_m, p.g_L, p.E_L, p.g_Na, p.E_Na, p.g_K, p.E_K, p.g_M, p.V_T, p.tau_max,
    5.0, 0.0, st, 0, 200,
)
print("done", time.perf_counter() - t0, out[-1], flush=True)
