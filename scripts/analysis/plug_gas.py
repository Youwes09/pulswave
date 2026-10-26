"""Plug-region gas speed and front per save for archived cases (same definitions as rule_extract2). Single process."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import foam, wave

ROOT, OUT = sys.argv[1], sys.argv[2]
X_JET = 0.05
os.makedirs(OUT, exist_ok=True)
for name in sys.argv[3:]:
    case, path = os.path.join(ROOT, name), os.path.join(OUT, name + ".json")
    done = json.load(open(path))["saves"] if os.path.exists(path) else {}
    part = foam._parts(case)[0]
    for t in sorted((d for d in os.listdir(part) if d[0].isdigit() and float(d) > 0), key=float):
        if t in done:
            continue
        rows = foam.load(case, t, ("T", "p", "U", "CO2", "CO"))
        front = wave.structure(rows, dx=foam.cell_size(rows))
        gas = [r["ux"] for r in rows if X_JET < r["x"] < X_JET + 2e-3 and r["y"] < 1e-3]
        done[t] = {"front": [[h, x] for h, x, *_ in front], "base": wave.base(front),
                   "gas_ux": sum(gas) / len(gas) if gas else None}
        json.dump({"case": name, "saves": done}, open(path, "w"))
        print(name, t, flush=True)
