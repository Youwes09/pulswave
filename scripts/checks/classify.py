"""Outcome classes of the revision runs under every combination of analysis choices.

Reads the per-case front files written by tracker_sensitivity.py and applies the classification fixed in docs/experiments.md
(Revision runs, analysis criteria) to every combination of tracker variant x base heights x drift window:
  held          largest |offset| <= 2 mm over the window, and |drift| < 0.02 mm/us or drift within 2 standard errors of zero
  lost          drift >= 0.05 mm/us and more than 2 standard errors above zero, or final offset >= 6 mm
  intermediate  neither
Offset is the base minus the reference base at the same time; drift is the least-squares slope of the offset over the last
W us. A class is reported as robust only if every combination gives it.
Switch-off cases also get the hold interval (bounded by saves) for thresholds of 1.25-2.5 cells.
Crop cases are compared only up to 40 us after the branch, the window over which the crop agrees with the reduced domain;
they get offsets, not classes.
Usage: python scripts/checks/classify.py [tracker_dir] [--json out.json]
"""
import json, math, os, statistics as st, sys

D = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "tracker"
VARIANTS = ("p1.5_c0.02", "p1.3_c0.02", "p2.0_c0.02", "p1.5_c0.01", "p1.5_c0.05", "T1500", "T1900")
BASES = {"4-6": (4, 5, 6), "3": (3,), "2-4": (2, 3, 4), "5-6": (5, 6), "4-6,9": (4, 5, 6, 9)}
WINDOWS = (50, 30, 70)
KS = (1.25, 1.5, 2.0, 2.5)
CELL = 0.2
BASELINE = ("p1.5_c0.02", "4-6", 50)

REDUCED = {"ref": "r_box_ref", "branch": 70.0,
           "cases": ["r_box_f80k", "r_box_f60k", "r_box_f50k", "r_box_f40k", "r_box_f30k", "r_box_f20k", "r_box_q120k",
                     "r_box_half", "r_box_j05", "r_box_cone", "r_box_patch", "r_box_reon", "r_box_dry", "r_box_off"]}
LOW = {"ref": "r_low_cont", "branch": 70.0, "cases": ["r_low_f80k"]}
FINE = {"ref": "r_f15box_cont", "branch": 90.0, "cases": ["r_f15box_f80k"]}
CROP = {"ref": "r_crop_cont", "branch": 50.0, "window": 40.0,
        "cases": ["r_crop_f80k", "r_crop_f60k", "r_crop_f50k", "r_crop_q120k", "r_crop_f40k_d75", "r_crop_off",
                  "r_crop_off_tolctl", "r_crop_f80k_co15", "r_crop_off_co15"]}
OFF = [("r_box_off", "r_box_ref", 70.0), ("r_crop_off", "r_crop_cont", 50.0), ("r_crop_off_tolctl", "r_crop_cont", 50.0)]


def load(name):
    p = os.path.join(D, name + ".json")
    if not os.path.exists(p):
        return None
    return {round(float(t) * 1e6, 2): rec for t, rec in json.load(open(p)).items()}


def base(rec, variant, hs):
    xs = sorted(x for h, x in rec[variant] if h in hs and x is not None)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else None


def offsets(run, ref, variant, hs, t0, t1=1e9):
    out = []
    for t in sorted(run):
        if t0 <= t <= t1 and t in ref:
            b, r = base(run[t], variant, hs), base(ref[t], variant, hs)
            if b is not None and r is not None:
                out.append((t, b - r))
    return out


def fit(pts):
    """Least-squares slope and its standard error."""
    n = len(pts)
    if n < 3:
        return None, None
    tm, om = st.mean(t for t, _ in pts), st.mean(o for _, o in pts)
    sxx = sum((t - tm) ** 2 for t, _ in pts)
    v = sum((t - tm) * (o - om) for t, o in pts) / sxx
    res = sum((o - om - v * (t - tm)) ** 2 for t, o in pts)
    return v, math.sqrt(res / (n - 2) / sxx)


def classify(off, window):
    end = off[-1][0]
    v, se = fit([(t, o) for t, o in off if t >= end - window])
    largest, final = max(abs(o) for _, o in off), off[-1][1]
    if v is None:
        return None, largest, final, v, se
    if largest <= 2.0 and (abs(v) < 0.02 or abs(v) <= 2 * se):
        c = "held"
    elif (v >= 0.05 and v > 2 * se) or final >= 6.0:
        c = "lost"
    else:
        c = "intermediate"
    return c, largest, final, v, se


def hold(run, ref, cut, variant, hs, k):
    """(lo, hi]: the base, relative to the reference, first exceeds k cells behind its value at the cut at save hi."""
    def rel(t):
        b, r = base(run[t], variant, hs), base(ref[t], variant, hs) if t in ref else None
        return None if b is None or r is None else b - r
    r0 = rel(cut)
    prev = cut
    for t in sorted(t for t in run if t > cut):
        d = rel(t)
        if d is not None and d - r0 > k * CELL:
            return prev - cut, t - cut
        prev = t
    return None


def classes(group, report):
    ref = load(group["ref"])
    if ref is None:
        print(f"  (reference {group['ref']} not tracked yet)")
        return
    for name in group["cases"]:
        run = load(name)
        if run is None:
            print(f"  {name:20s} not tracked yet")
            continue
        found, rows = {}, {}
        for variant in VARIANTS:
            for bname, hs in BASES.items():
                off = offsets(run, ref, variant, hs, group["branch"])
                if len(off) < 3:
                    continue
                for w in WINDOWS:
                    res = classify(off, w)
                    rows[(variant, bname, w)] = res
                    found[res[0]] = found.get(res[0], 0) + 1
        b = rows.get(BASELINE)
        span = f"{group['branch']:g}-{max(run):g} us"
        if b is None:
            print(f"  {name:20s} {span}: too few saves")
            continue
        verdict = next(iter(found)) + " (robust)" if len(found) == 1 else "MIXED " + ", ".join(f"{c} {n}" for c, n in sorted(found.items(), key=lambda kv: str(kv[0])))
        drifts = [r[3] for r in rows.values() if r[3] is not None]
        print(f"  {name:20s} {span:13s} baseline: {b[0]:12s} largest |off| {b[1]:4.2f} mm  final {b[2]:+5.2f} mm  "
              f"drift {b[3]:+.4f} +- {b[4]:.4f} mm/us   all {len(rows)} combinations: {verdict}; drift range {min(drifts):+.4f} .. {max(drifts):+.4f}")
        report[name] = {"reference": group["ref"], "window_us": [group["branch"], max(run)],
                        "baseline": dict(zip(("class", "largest_abs_offset_mm", "final_offset_mm", "drift_mm_per_us", "drift_se"), b)),
                        "classes": found, "combinations": {"|".join(map(str, k)): v[0] for k, v in rows.items()}}


def crop(report):
    ref = load(CROP["ref"])
    if ref is None:
        return
    t0, t1 = CROP["branch"], CROP["branch"] + CROP["window"]
    for name in CROP["cases"]:
        run = load(name)
        if run is None:
            print(f"  {name:20s} not tracked yet")
            continue
        at = {}
        for variant in VARIANTS:
            for hs in BASES.values():
                for t, o in offsets(run, ref, variant, hs, t0, t1):
                    at.setdefault(t, []).append(o)
        base_off = dict(offsets(run, ref, *BASELINE[:1], BASES[BASELINE[1]], t0, t1))
        cols = [t for t in (t0 + 10, t0 + 20, t0 + 30, t0 + 40) if t in base_off]
        print(f"  {name:20s} offset (mm) at " + "  ".join(f"+{t - t0:g}: {base_off[t]:+5.2f} [{min(at[t]):+.2f}..{max(at[t]):+.2f}]" for t in cols))
        report[name] = {"reference": CROP["ref"], "offset_mm": {t: base_off[t] for t in cols},
                        "range_over_choices_mm": {t: [min(at[t]), max(at[t])] for t in cols}}


def holds(report):
    for name, refname, cut in OFF:
        run, ref = load(name), load(refname)
        if run is None or ref is None:
            continue
        cells = {}
        for k in KS:
            ivs = {hold(run, ref, cut, v, hs, k) for v in VARIANTS for hs in BASES.values()}
            lo = min((iv[0] for iv in ivs if iv), default=None)
            hi = max((iv[1] for iv in ivs if iv), default=None)
            b = hold(run, ref, cut, BASELINE[0], BASES[BASELINE[1]], k)
            cells[k] = {"baseline": b, "range": [lo, hi], "never": None in ivs}
        print(f"  {name:20s} " + "  ".join(f"k={k:g}: {cells[k]['baseline']} over choices ({cells[k]['range'][0]:g},{cells[k]['range'][1]:g}]"
                                          + (" some never" if cells[k]["never"] else "") for k in KS if cells[k]["range"][0] is not None))
        report[name + ":hold"] = {"reference": refname, "cut_us": cut, "by_k_cells": {str(k): c for k, c in cells.items()}}


if __name__ == "__main__":
    report = {}
    n = len(VARIANTS) * len(BASES) * len(WINDOWS)
    print(f"Classes over {n} combinations ({len(VARIANTS)} tracker variants x {len(BASES)} base definitions x drift windows {WINDOWS} us)."
          f"\nBaseline: {BASELINE[0]}, base y = {BASELINE[1]} mm, drift over the last {BASELINE[2]} us.")
    for title, group in (("Reduced domain, vs r_box_ref", REDUCED), ("Low domain (120 x 25 mm), vs r_low_cont", LOW),
                         ("Reduced domain at 0.15 mm, vs r_f15box_cont", FINE)):
        print(f"\n{title}")
        classes(group, report)
    print(f"\nCrop, vs r_crop_cont, up to +{CROP['window']:g} us (baseline [range over tracker variants and base definitions])")
    crop(report)
    print("\nHold after switch-off relative to the reference, us (k = threshold in cells)")
    holds(report)
    if "--json" in sys.argv:
        json.dump(report, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=str)
