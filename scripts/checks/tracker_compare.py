"""Front base per height with the old tracker (largest pressure rise) against the current one, for every save from 70 us.

Usage: python scripts/checks/tracker_compare.py <case> [<case> ...]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pulswave import foam, wave  # noqa: E402

HEIGHTS = (1, 2, 3, 4, 6, 9)


def largest_rise(rows, dx=0.2e-3):
    rows_y = wave._by_row(rows, "y", dx)
    out = {}
    for h in HEIGHTS:
        line = sorted((r for r in rows_y[int(h * 1e-3 / dx + 1e-6)] if 0.035 < r["x"] < 0.14), key=lambda r: r["x"])
        j = max(range(2, len(line)), key=lambda i: line[i]["p"] - line[i - 2]["p"])
        out[h] = line[j]["x"] * 1e3
    return out


for case in sys.argv[1:]:
    times = sorted((t for t in os.listdir(os.path.join(case, "processor0")) if t[0].isdigit() and float(t) >= 7e-5), key=float)
    for t in times:
        rows = foam.load(case, t, ("p", "CO2", "T"))
        new = {h: x for h, x, *_ in wave.structure(rows, heights_mm=HEIGHTS)}
        old = largest_rise(rows)
        changed = [f"{h} mm {old[h]:.1f}->{new[h]:.1f}" for h in HEIGHTS if abs(old[h] - new[h]) > 0.25]
        print(os.path.basename(case.rstrip("/")), f"{float(t) * 1e6:.0f} us", "current:", " ".join(f"{new[h]:.1f}" for h in HEIGHTS),
              "| changed:", ", ".join(changed) or "none", flush=True)
