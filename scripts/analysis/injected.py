"""Jet liquid injected between two saves, from the injectors' own state (massInjected), per case.

The freestream injectors (inflow, upper) are left out. Values are per 2 mm of depth.
Usage: python scripts/analysis/injected.py <case at t0> <t0> <case at t1> <t1>   (the two cases are segments of one restart chain)
"""
import os, re, sys

FREESTREAM = ("inflow", "upper")


def injected(case, t):
    path = os.path.join(case, "processor0", t, "uniform", "lagrangian", "sprayCloud", "sprayCloudOutputProperties")
    return {n: float(m) for n, m in re.findall(r"\n\s*(\w+)\s*\n\s*\{\s*\n\s*massInjected\s+([0-9.eE+-]+);", open(path).read())}


c0, t0, c1, t1 = sys.argv[1:5]
a, b = injected(c0, t0), injected(c1, t1)
jets = {n: b[n] - a.get(n, 0.0) for n in b if n not in FREESTREAM and b[n] - a.get(n, 0.0) > 0}
m, dt = sum(jets.values()), float(t1) - float(t0)
print(f"{os.path.basename(c1.rstrip('/'))}: jet liquid {m * 1e6:.3f} mg over {float(t0) * 1e6:g}-{float(t1) * 1e6:g} us"
      f" = {m / dt * 1e3:.2f} g/s mean, from {sorted(jets)}")
