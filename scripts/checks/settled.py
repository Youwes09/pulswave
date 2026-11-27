"""Exit 0 if a case's base has varied by at most `tol` mm over every save in [t0, t1] us, else 1.

The branching criterion for mapped runs (docs/experiments.md, revision runs). Used as a queue gate by queue_rev.py.
Usage: python3 scripts/checks/settled.py <case> <t0 us> <t1 us> [tol mm, default 0.2]
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import foam, wave

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
case, t0, t1 = os.path.join(B, sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
tol = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
saves = sorted((d for d in os.listdir(os.path.join(case, "processor0"))
                if d.replace(".", "").replace("e-", "").isdigit() and t0 - 1e-3 <= float(d) * 1e6 <= t1 + 1e-3), key=float)
if not saves or abs(float(saves[-1]) * 1e6 - t1) > 1e-3 or abs(float(saves[0]) * 1e6 - t0) > 1e-3:
    print(f"saves from {t0:g} to {t1:g} us not all written yet"); sys.exit(1)
bases = []
for t in saves:
    rows = foam.load(case, t, fields=("p", "CO2", "CO"))
    bases.append(wave.base(wave.structure(rows, dx=foam.cell_size(rows))))
spread = max(bases) - min(bases) if None not in bases else float("inf")
print(f"{sys.argv[1]} base over {t0:g}-{t1:g} us: " + " ".join(f"{b:.2f}" for b in bases) + f", spread {spread:.2f} mm")
sys.exit(0 if spread <= tol + 1e-9 else 1)
