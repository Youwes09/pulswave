"""Position of the near-wall liquid layer behind the jet: total mass in x = 49.5-100 mm, y < 3 mm, the mass within
3 mm downstream of the jet, and the x below which 5, 25 and 50% of that mass lies.

Usage: python scripts/checks/liquid_edge.py <case> <time> [<time> ...]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pulswave import foam, wave  # noqa: E402

if __name__ == "__main__":
    case = sys.argv[1]
    for t in sys.argv[2:]:
        total, near, xs = wave.liquid_edge(foam.parcels(case, t))
        print(f"{t}: liquid {total * 1e9:.0f} ug, within 3 mm of the jet {near * 1e9:.0f} ug, x5/25/50% "
              + " ".join(f"{x * 1e3:.1f}" for x in xs) + " mm")
