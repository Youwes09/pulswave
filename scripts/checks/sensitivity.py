"""Sensitivity of the hold, retreat and outcome numbers to the analysis choices, from the tracked fronts in paper/data.

For each base definition (set of heights whose median is the base) it reports
  - each hold after switch-off as an interval bounded by consecutive saves, for thresholds of 1.25-2.5 cells,
  - the retreat speed over the 20 us after the hold, with its standard error,
  - for the long reduced-domain cases, the largest and final offset from the reference and the drift over
    150-200 us (least-squares slope of base minus reference, with standard error).
Usage: python scripts/checks/sensitivity.py [paper/data]
"""
import json, math, os, statistics as st, sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "paper", "data")
CELL = 0.2
BASES = {"y=3": (3,), "y=2-4": (2, 3, 4), "y=4-6 (paper)": (4, 5, 6), "y=5-6": (5, 6), "y=4-6,9": (4, 5, 6, 9)}
KS = (1.25, 1.5, 2.0, 2.5)


def _load(path):
    d = json.load(open(path))
    saves, scale = (d["saves"], 1e6) if "saves" in d else (d, 1.0)
    return {round(float(t) * scale, 2): {h: x for h, x, *_ in fr} for t, fr in
            ((t, v["front"] if isinstance(v, dict) else v) for t, v in saves.items())}


def run(*names):
    out = {}
    for n in names:
        sub = "fronts" if n.startswith("old:") else "campaign/front"
        out.update(_load(os.path.join(D, sub, n.removeprefix("old:") + ".json")))
    return dict(sorted(out.items()))


def basef(hs):
    def f(fr):
        xs = sorted(fr[h] for h in hs if fr.get(h) is not None)
        return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else None
    return f


def fit(pts):
    """Least-squares slope and its standard error."""
    n = len(pts)
    if n < 3:
        return None, None
    tm, bm = st.mean(t for t, _ in pts), st.mean(b for _, b in pts)
    sxx = sum((t - tm) ** 2 for t, _ in pts)
    v = sum((t - tm) * (b - bm) for t, b in pts) / sxx
    res = sum((b - bm - v * (t - tm)) ** 2 for t, b in pts)
    return v, math.sqrt(res / (n - 2) / sxx)


def hold(r, cut, f, k, ref=None, span=20.0):
    """Hold interval (lo, hi]: the base first exceeds k cells behind its start (or behind the reference) at save hi."""
    def disp(t):
        b = f(r[t])
        if b is None:
            return None
        if ref is None:
            return b - f(r[cut])
        return (b - f(ref[t])) - (f(r[cut]) - f(ref[cut])) if t in ref and f(ref[t]) is not None else None
    ts = [t for t in r if t >= cut]
    prev = cut
    for t in ts[1:]:
        d = disp(t)
        if d is not None and d > k * CELL:
            pts = [(s, f(r[s])) for s in ts if t <= s <= t + span and f(r[s]) is not None]
            return (prev - cut, t - cut), fit(pts), ts[-1] - cut
        prev = t
    return None, (None, None), ts[-1] - cut


ref = run("old:box_large", "box_large_200")
OFF = [("reduced, off 70 us, vs reference", run("old:large_off", "old:large_off_long"), 70.0, ref),
       ("reduced, off 70 us, own start", run("old:large_off", "old:large_off_long"), 70.0, None),
       ("reduced, off 165 us (0.5 us saves)", run("large_off_hr"), 165.0, None),
       ("reduced, dry, vs reference", run("old:large_off_dry"), 70.0, ref),
       ("crop 0.2 mm (0.5 us saves)", run("crop_off_hr"), 50.0, None),
       ("crop 0.2 mm (5 us saves)", run("old:crop_grid_off"), 50.0, None),
       ("crop 0.1 mm (1 us saves)", run("crop_fine_off"), 50.0, None),
       ("crop, plug removed", run("crop_off_cut"), 50.0, None),
       ("crop, 1 mm jet", run("old:crop_grid_d1_off"), 50.0, None)]
LONG = {"80 kHz": run("old:large_f80k", "old:large_f80k_long", "large_f80k_200"),
        "40 kHz": run("old:large_f40k", "large_f40k_200"), "30 kHz": run("large_f30k", "large_f30k_200"),
        "20 kHz": run("old:large_f20k", "large_f20k_200"),
        "half width, patch": run("large_narrow_patch"), "half width, cone": run("old:large_narrow", "large_narrow_long"),
        "half velocity": run("old:large_half", "old:large_half_long"), "jet off": run("old:large_off", "old:large_off_long")}

for bname, hs in BASES.items():
    f = basef(hs)
    print(f"\n######## base = median over {bname}")
    print("hold intervals (us) at k = " + ", ".join(f"{k:g}" for k in KS) + " cells; retreat (mm/us) +- s.e. at k = 1.5")
    for name, r, cut, rr in OFF:
        cells, retreat = [], ""
        for k in KS:
            iv, (v, se), length = hold(r, cut, f, k, rr)
            cells.append(f"({iv[0]:g},{iv[1]:g}]" if iv else f">{length:g}")
            if k == 1.5 and v is not None:
                retreat = f"{v:.3f} +- {se:.3f}"
        print(f"  {name:38s} " + "  ".join(f"{c:>11s}" for c in cells) + f"   {retreat}")
    print("long cases vs reference: largest offset (mm, at us), offset at 200 us, drift 150-200 us (mm/us +- s.e.)")
    for name, r in LONG.items():
        ts = [t for t in r if t in ref and 70 <= t <= 200 and f(r[t]) is not None and f(ref[t]) is not None]
        off = [(t, f(r[t]) - f(ref[t])) for t in ts]
        tmax, omax = max(off, key=lambda p: p[1])
        v, se = fit([(t, o) for t, o in off if t >= 150])
        print(f"  {name:20s} largest {omax:+5.2f} at {tmax:g}   at 200 {dict(off).get(200.0, float('nan')):+5.2f}   drift {v:+.4f} +- {se:.4f}")
