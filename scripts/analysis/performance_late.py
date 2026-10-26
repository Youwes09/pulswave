"""Performance on the figdata plane (x = 100 mm, y < 25 mm) per save over a late window, with the plane check, one JSON per case.
Single process, resumable.

Usage: python scripts/analysis/performance_late.py <out> <t0> <t1> <case>...
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import figdata, foam, performance

out, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
os.makedirs(out, exist_ok=True)
for case in sys.argv[4:]:
    path = os.path.join(out, os.path.basename(case.rstrip("/")) + ".json")
    done = json.load(open(path)) if os.path.exists(path) else {}
    for t in os.listdir(foam._parts(case)[0]):
        if t[0].isdigit() and t0 - 1e-9 <= float(t) <= t1 + 1e-9 and t not in done:
            done[t] = figdata._perf(case, t)
            done[t]["check"] = performance.plane_check(foam.load(case, t, performance.FIELDS), figdata.PLANE_X, figdata.PLANE_Y,
                                                       dx=figdata._setup(case).dx)
            json.dump(dict(sorted(done.items(), key=lambda kv: float(kv[0]))), open(path, "w"))
            print(case, t, flush=True)
