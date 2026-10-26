"""Share of subsonic cells (local Mach < 1) on a 5 mm grid, to see whether a disturbance at the top boundary can travel upstream.

Usage: python scripts/analysis/subsonic_map.py <case> <t>
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import foam, performance, profiles

case, t = sys.argv[1], sys.argv[2]
rows = foam.load(case, t, performance.FIELDS)
grid = {}
for r in rows:
    k = (int(r["x"] * 200), int(r["y"] * 200))
    n, s = grid.get(k, (0, 0))
    grid[k] = (n + 1, s + (profiles.mach(r) < 1))
xs, ys = sorted({k[0] for k in grid}), sorted({k[1] for k in grid}, reverse=True)
print(f"{os.path.basename(case)} {float(t) * 1e6:.0f} us: subsonic share per 5 mm cell (. 0, 1-9 tenths, # all); x 0-120 mm across, y top down")
for j in ys:
    line = ""
    for i in xs:
        n, s = grid.get((i, j), (1, 0))
        f = s / n
        line += "." if f == 0 else "#" if f == 1 else str(min(9, max(1, int(f * 10))))
    print(f"  y {j * 5:2d}  {line}")
