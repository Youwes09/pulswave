"""Bounds check of the n-heptane vapour mass fraction in every save: cells above 1 or below 0, and where.

Cells above 1 are counted in the regions the diagnostics use: the plug window (x 50-52 mm, y < 1 mm), near the jet
(x < 53 mm), the base heights (y = 3.5-6.5 mm) and the measurement plane (x 99-101 mm, y < 25 mm).
Usage: python scripts/analysis/scan_fuel.py <case>...   (one line per save with any violation, then one summary line per case)
"""
import glob, os, re, sys

NUM = re.compile(r"internalField\s+nonuniform\s+List<scalar>\s*\n\d+\s*\n\(\n(.*?)\n\)\s*;", re.S)


def values(path):
    m = NUM.search(open(path).read())
    return [float(v) for v in m.group(1).split("\n")] if m else []


def centres(part):
    m = re.search(r"\n\d+\s*\n\(\n(.*?)\n\)", open(os.path.join(part, "0", "C")).read(), re.S)
    return [tuple(float(v) for v in l.strip("() ").split()[:2]) for l in m.group(1).split("\n")]


REGIONS = {"plug": lambda x, y: 50 <= x <= 52 and y < 1, "near jet": lambda x, y: x < 53,
           "base heights": lambda x, y: 3.5 <= y <= 6.5, "plane": lambda x, y: 99 <= x <= 101 and y < 25}

for case in (c.rstrip("/") for c in sys.argv[1:]):
    parts = sorted(glob.glob(os.path.join(case, "processor*")))
    times = sorted({t for p in parts[:1] for t in os.listdir(p) if t[0].isdigit() and t != "0"}, key=float)
    C = {p: centres(p) for p in parts}
    bad_saves, worst, total = 0, (0.0, None, None), dict.fromkeys(REGIONS, 0)
    for t in times:
        hi = lo = 0
        top = (0.0, None)
        where = dict.fromkeys(REGIONS, 0)
        for p in parts:
            f = os.path.join(p, t, "NXC7H16")
            if not os.path.exists(f):
                continue
            for c, v in zip(C[p], values(f)):
                if v > 1.0 + 1e-6:
                    hi += 1
                    for k, inside in REGIONS.items():
                        where[k] += inside(c[0] * 1e3, c[1] * 1e3)
                    if v > top[0]:
                        top = (v, c)
                elif v < -1e-6:
                    lo += 1
        if hi or lo:
            bad_saves += 1
            xy = f"x {top[1][0] * 1e3:.1f} y {top[1][1] * 1e3:.2f} mm" if top[1] else "-"
            print(f"{os.path.basename(case)} {float(t) * 1e6:g} us: {hi} cells > 1 (max {top[0]:.3f} at {xy}), {lo} cells < 0; "
                  + ", ".join(f"{k} {n}" for k, n in where.items()), flush=True)
            for k in REGIONS:
                total[k] += where[k]
            if top[0] > worst[0]:
                worst = (top[0], t, xy)
    print(f"== {os.path.basename(case)}: {bad_saves}/{len(times)} saves out of bounds; worst {worst[0]:.3f}"
          + (f" at {float(worst[1]) * 1e6:g} us, {worst[2]}" if worst[1] else "") + "; cell-saves by region: "
          + ", ".join(f"{k} {n}" for k, n in total.items()), flush=True)
