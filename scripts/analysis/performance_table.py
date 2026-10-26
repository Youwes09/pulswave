"""Mean recovery and burnt fuel per case against the reference, over the saves where the plane passes its check in both.

A save passes when at least 95% of the flux through the plane is clean (performance.plane_check):
liquid-cooled unburnt gas on the plane makes the frozen total pressure meaningless.

Usage: python scripts/analysis/performance_table.py <dir> <reference> <case>...
"""
import json, os, statistics as st, sys

d = sys.argv[1]
load = lambda c: json.load(open(os.path.join(d, c + ".json")))
ok = lambda v: v["check"]["clean_share"] >= 0.95
ref = load(sys.argv[2])


def row(name, r):
    common = sorted((t for t in set(r) & set(ref) if ok(r[t]) and ok(ref[t])), key=float)
    if len(common) < 2:
        print(f"{name:20s} passes {len(common)}/{len(r)} saves: no valid mean")
        return
    rec = [r[t]["recovery"] for t in common]
    drec = [r[t]["recovery"] - ref[t]["recovery"] for t in common]
    dfuel = [(r[t]["burnt_fuel"] - ref[t]["burnt_fuel"]) * 1e3 for t in common]
    print(f"{name:20s} passes {len(common):2d}/{len(r)}  recovery {st.mean(rec):.4f} (sd {st.stdev(rec):.4f})  d {st.mean(drec):+.4f}"
          f"  burnt {st.mean(r[t]['burnt_fuel'] for t in common) * 1e3:.3f} g/s  d {st.mean(dfuel):+.3f}"
          f"  saves {float(common[0]) * 1e6:.0f}-{float(common[-1]) * 1e6:.0f}")


row(sys.argv[2] + " (ref)", ref)
for c in sys.argv[3:]:
    row(c, load(c))
