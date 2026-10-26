"""Burnt and vapour fuel crossing the x = 100 mm plane per height band, mean over saves in [t0, t1].

Cells whose n-heptane mass fraction exceeds 1 (see scan_fuel.py) are left out, and the flux they carry is reported.

Usage: python scripts/analysis/plane_bands.py <t0> <t1> <case>...
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import figdata, foam, performance

BANDS = ((0, 1), (1, 3), (3, 6), (6, 10), (10, 15), (15, 25))
t0, t1 = float(sys.argv[1]), float(sys.argv[2])
for case in sys.argv[3:]:
    s = figdata._setup(case)
    times = [t for t in os.listdir(foam._parts(case)[0]) if t[0].isdigit() and t0 - 1e-9 <= float(t) <= t1 + 1e-9]
    acc = {b: [0.0, 0.0, 0.0] for b in BANDS}
    dropped = 0.0
    for t in times:
        _, plane = performance._boundary(foam.load(case, t, performance.FIELDS), s.dx, figdata.PLANE_X, figdata.PLANE_Y)
        for r, w in plane:
            if r["NXC7H16"] > 1.0:
                dropped += w / len(times)
                continue
            for lo, hi in BANDS:
                if lo <= r["y"] * 1e3 < hi:
                    a = acc[(lo, hi)]
                    a[0] += performance.burnt_fuel(r) * w / len(times)
                    a[1] += r["NXC7H16"] * w / len(times)
                    a[2] += w / len(times)
    print(os.path.basename(case.rstrip("/")), f"{len(times)} saves; y band mm: burnt g/s, vapour g/s, mass g/s")
    for (lo, hi), (b, v, m) in acc.items():
        print(f"  {lo:2d}-{hi:<2d}  {b * 1e3:6.3f}  {v * 1e3:6.3f}  {m * 1e3:6.2f}")
    print(f"  total  {sum(a[0] for a in acc.values()) * 1e3:6.3f}  {sum(a[1] for a in acc.values()) * 1e3:6.3f}"
          f"  (left out: {dropped * 1e3:.3f} g/s of mass flux in cells with NXC7H16 > 1)")
