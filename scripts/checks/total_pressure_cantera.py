"""Cell total pressure from pulswave.performance against Cantera (isentropic, frozen composition).

Usage: python scripts/checks/total_pressure_cantera.py <case> <time> <x_mm>,<y_mm> [<x_mm>,<y_mm> ...]
"""
import os
import sys

import cantera as ct

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, ROOT)
from pulswave import foam, performance  # noqa: E402

gas = ct.Solution(os.path.join(ROOT, "mechanisms", "nHeptane.yaml"))
case, t = sys.argv[1], sys.argv[2]
rows = foam.load(case, t, performance.FIELDS)
for spec in sys.argv[3:]:
    x, y = (float(v) * 1e-3 for v in spec.split(","))
    r = min(rows, key=lambda r: (r["x"] - x) ** 2 + (r["y"] - y) ** 2)
    ours = performance.total_pressure(r)
    Y = {s: r[s] for s in performance.SPECIES if r[s] > 0}
    gas.TPY = r["T"], r["p"], Y
    s0, h0 = gas.entropy_mass, gas.enthalpy_mass + 0.5 * (r["ux"] ** 2 + r["uy"] ** 2)
    for _ in range(50):  # along the isentrope dh = dp / rho
        step = (h0 - gas.enthalpy_mass) * gas.density
        gas.SP = s0, gas.P + step
        if abs(step) < 1e-6 * gas.P:
            break
    print(f"x {r['x'] * 1e3:6.1f} y {r['y'] * 1e3:5.1f} mm  T {r['T']:5.0f} K  p0 ours {ours / foam.ATM:8.3f} atm,"
          f" Cantera {gas.P / foam.ATM:8.3f} atm, difference {(ours / gas.P - 1) * 100:+.4f}%")
