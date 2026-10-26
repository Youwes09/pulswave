"""Frozen state and ignition delay behind the jet-induced shock, from the pressure ratios the front tracker measures.

Usage: python scripts/analysis/jet_shock.py <T1> <p1 atm> <C7H16> <O2> <ratio>...
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import theory

T1, p1, fuel, o2 = float(sys.argv[1]), float(sys.argv[2]) * 101325.0, float(sys.argv[3]), float(sys.argv[4])
Y = {"NXC7H16": fuel, "O2": o2, "N2": 1 - fuel - o2}
g = theory.gas()
for ratio in map(float, sys.argv[5:]):
    lo, hi = 100.0, 5000.0
    for _ in range(60):
        un = (lo + hi) / 2
        T2, p2, _ = theory.normal_shock(g, T1, p1, Y, un)
        lo, hi = (un, hi) if p2 / p1 < ratio else (lo, un)
    print(f"p2/p1 {ratio:4.1f}: T2 {T2:5.0f} K, p2 {p2 / 101325:5.1f} atm, ignition delay {theory.ignition_delay(T2, p2, Y, g=g) * 1e6:.2f} us")
