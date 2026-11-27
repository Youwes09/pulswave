"""Outcome classes of the revision runs under every combination of analysis choices, by the original and the amended criteria.

Reads the per-case front files written by tracker_sensitivity.py. Offset = base minus the reference base at the same time.

Original criteria (docs/experiments.md, fixed 2026-11-27 08:03 UTC), applied unchanged:
  held          largest |offset| <= 2 mm over the window, and |drift| < 0.02 mm/us or drift within 2 OLS standard errors of 0
  lost          drift >= 0.05 mm/us and more than 2 OLS standard errors above 0, or final offset (last save) >= 6 mm
  intermediate  neither
  drift = least-squares slope of the offset over the last W us (W = 50, 30, 70); 7 tracker variants x 5 base definitions.
Amended criteria (2026-11-27 evening, after an independent audit; see docs/experiments.md, changes to the criteria):
  - temperature fronts must stay hot over 2 mm (T1500s, T1900s replace T1500, T1900: the single-cell version picks up gas
    heated by the jet's bow shock upstream of the front)
  - base definitions 3 mm and 2-4 mm dropped (they lie in the wall flares that wave.base excludes)
  - drift window max(W, 3 pulse periods), with harmonics at the pulse frequency and twice it removed in the fit
  - standard errors from Newey-West (Bartlett kernel, lag max(15 saves, one period)): the 1 us saves are autocorrelated
  - held needs |drift| + 1.96 SE < 0.02 mm/us (equivalence) instead of "not different from zero"
  - final offset = mean over the last max(10 us, one period)
A class is robust only if every combination gives it. Retreat onset = first save after which the offset stays above 1 mm.
Switch-off cases also get hold intervals for thresholds of 1.25-2.5 cells; crop cases get offsets up to 40 us after the branch.
Usage: python scripts/checks/classify.py [tracker_dir] [--json out.json]
"""
import json, math, os, statistics as st, sys

D = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "tracker"
CELL = 0.2
WINDOWS = (50, 30, 70)
KS = (1.25, 1.5, 2.0, 2.5)
ORIGINAL = {"variants": ("p1.5_c0.02", "p1.3_c0.02", "p2.0_c0.02", "p1.5_c0.01", "p1.5_c0.05", "T1500", "T1900"),
            "bases": {"4-6": (4, 5, 6), "3": (3,), "2-4": (2, 3, 4), "5-6": (5, 6), "4-6,9": (4, 5, 6, 9)}}
AMENDED = {"variants": ("p1.5_c0.02", "p1.3_c0.02", "p2.0_c0.02", "p1.5_c0.01", "p1.5_c0.05", "T1500s", "T1900s"),
           "bases": {"4-6": (4, 5, 6), "5-6": (5, 6), "4-6,9": (4, 5, 6, 9)}}
BASELINE = ("p1.5_c0.02", (4, 5, 6))

# run: (reference, start of the compared window in us, pulse frequency in kHz or None); *_ext runs are appended to their parent
REDUCED = {
    "r_box_f80k": ("r_box_ref", 70, 80), "r_box_f80k_p71": ("r_box_ref", 71, 80), "r_box_f80k_p73": ("r_box_ref", 73, 80),
    "r_box_f60k": ("r_box_ref", 70, 60), "r_box_f50k": ("r_box_ref", 70, 50), "r_box_f40k": ("r_box_ref", 70, 40),
    "r_box_f30k": ("r_box_ref", 70, 30), "r_box_f20k": ("r_box_ref", 70, 20), "r_box_f20k_p75": ("r_box_ref", 75, 20),
    "r_box_f10k": ("r_box_ref", 70, 10), "r_box_q120k": ("r_box_ref", 70, 120),
    "r_box_half": ("r_box_ref", 70, None), "r_box_j05": ("r_box_ref", 70, None), "r_box_cone": ("r_box_ref", 70, None),
    "r_box_patch": ("r_box_ref", 70, None), "r_box_reon": ("r_box_ref", 95, None), "r_box_dry": ("r_box_ref", 70, None),
    "r_box_off": ("r_box_ref", 70, None),
    "r_low_f80k": ("r_low_cont", 70, 80), "r_f15box_f80k": ("r_f15box_cont", 90, 80)}
CROP = {"ref": "r_crop_cont", "branch": 50.0, "window": 40.0,
        "cases": ["r_crop_f80k", "r_crop_f60k", "r_crop_f50k", "r_crop_q120k", "r_crop_f40k_d75", "r_crop_off",
                  "r_crop_off_tolctl", "r_crop_f80k_co15", "r_crop_off_co15"]}
OFF = [("r_box_off", "r_box_ref", 70.0), ("r_crop_off", "r_crop_cont", 50.0), ("r_crop_off_tolctl", "r_crop_cont", 50.0)]
PAIRED = [("r_box_f80k_tolctl", "r_box_f80k"), ("r_crop_off_tolctl", "r_crop_off"), ("r_box_f80k_p71", "r_box_f80k"),
          ("r_box_f80k_p73", "r_box_f80k")]
RECAPTURE = ("r_box_f20k", "r_box_f30k", "r_box_f20k_p75")


def _read(name):
    p = os.path.join(D, name + ".json")
    return {round(float(t) * 1e6, 2): rec for t, rec in json.load(open(p)).items()} if os.path.exists(p) else None


def load(name):
    """A run with its *_ext continuation appended, if tracked."""
    run = _read(name)
    ext = _read(name + "_ext")
    if run is not None and ext is not None:
        run = {**run, **ext}
    return run


def base(rec, variant, hs):
    xs = sorted(x for h, x in rec.get(variant, ()) if h in hs and x is not None)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else None


def offsets(run, ref, variant, hs, t0, t1=1e9):
    out = []
    for t in sorted(run):
        if t0 <= t <= t1 and t in ref:
            b, r = base(run[t], variant, hs), base(ref[t], variant, hs)
            if b is not None and r is not None:
                out.append((t, b - r))
    return out


def _solve(A, y):
    """Least squares by normal equations (small systems): coefficients and (X'X)^-1."""
    k = len(A[0])
    M = [[sum(a[i] * a[j] for a in A) for j in range(k)] for i in range(k)]
    inv = [[float(i == j) for j in range(k)] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p], inv[c], inv[p] = M[p], M[c], inv[p], inv[c]
        d = M[c][c]
        M[c] = [v / d for v in M[c]]; inv[c] = [v / d for v in inv[c]]
        for r in range(k):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]; inv[r] = [a - f * b for a, b in zip(inv[r], inv[c])]
    beta = [sum(inv[i][j] * sum(a[j] * yy for a, yy in zip(A, y)) for j in range(k)) for i in range(k)]
    return beta, inv


def fit(pts, freq_khz=None, hac_lag=None):
    """Slope of offset against time with optional harmonics (f, 2f); returns slope, OLS SE, Newey-West SE."""
    n = len(pts)
    if n < 3:
        return None, None, None
    tm = st.mean(t for t, _ in pts)
    A = []
    for t, _ in pts:
        row = [1.0, t - tm]
        if freq_khz:
            for m in (1, 2):
                w = 2 * math.pi * freq_khz * 1e-3 * m * t
                row += [math.sin(w), math.cos(w)]
        A.append(row)
    if len(A[0]) >= n:
        return None, None, None
    y = [o for _, o in pts]
    beta, inv = _solve(A, y)
    e = [yy - sum(b * a for b, a in zip(beta, row)) for row, yy in zip(A, y)]
    k = len(beta)
    ols = math.sqrt(sum(v * v for v in e) / (n - k) * inv[1][1])
    if hac_lag is None:
        return beta[1], ols, None
    # Newey-West sandwich for the slope: (X'X)^-1 S (X'X)^-1, Bartlett weights
    g = [[row[i] * ei for i in range(k)] for row, ei in zip(A, e)]
    S = [[sum(gt[i] * gt[j] for gt in g) for j in range(k)] for i in range(k)]
    for L in range(1, min(hac_lag, n - 1) + 1):
        w = 1 - L / (hac_lag + 1)
        for i in range(k):
            for j in range(k):
                c = sum(g[t][i] * g[t - L][j] + g[t - L][i] * g[t][j] for t in range(L, n))
                S[i][j] += w * c
    var = sum(inv[1][i] * S[i][j] * inv[j][1] for i in range(k) for j in range(k)) * n / (n - k)
    return beta[1], ols, math.sqrt(max(var, 0.0))


def classify_original(off, window):
    end = off[-1][0]
    v, se, _ = fit([(t, o) for t, o in off if t >= end - window])
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


def classify_amended(off, window, freq):
    end = off[-1][0]
    period = 1e3 / freq if freq else 0.0
    w = max(window, 3 * period)
    v, _, se = fit([(t, o) for t, o in off if t >= end - w], freq, hac_lag=max(15, int(round(period))))
    tail = max(10.0, period)
    final = st.mean(o for t, o in off if t >= end - tail)
    largest = max(abs(o) for _, o in off)
    if v is None or se is None:
        return None, largest, final, v, se
    if largest <= 2.0 and abs(v) + 1.96 * se < 0.02:
        c = "held"
    elif (v >= 0.05 and v > 2 * se) or final >= 6.0:
        c = "lost"
    else:
        c = "intermediate"
    return c, largest, final, v, se


def onset(off, level=1.0):
    """First save after which the offset stays above `level` mm to the end of the run."""
    t_on = None
    for t, o in off:
        if o > level:
            t_on = t if t_on is None else t_on
        else:
            t_on = None
    return t_on


def classes(report):
    for name, (refname, t0, freq) in REDUCED.items():
        run, ref = load(name), load(refname)
        if run is None or ref is None:
            print(f"  {name:20s} not tracked yet" + ("" if ref is not None else f" (reference {refname} missing)"))
            continue
        entry = {"reference": refname, "window_us": [t0, max(run)], "freq_khz": freq}
        for label, cfg, rule in (("original", ORIGINAL, "o"), ("amended", AMENDED, "a")):
            found, rows = {}, {}
            for variant in cfg["variants"]:
                for bname, hs in cfg["bases"].items():
                    off = offsets(run, ref, variant, hs, t0)
                    if len(off) < 3:
                        continue
                    for w in WINDOWS:
                        res = classify_original(off, w) if rule == "o" else classify_amended(off, w, freq)
                        rows[(variant, bname, w)] = res
                        found[res[0]] = found.get(res[0], 0) + 1
            entry[label] = {"classes": found, "combinations": {"|".join(map(str, k)): v[0] for k, v in rows.items()},
                            "baseline": dict(zip(("class", "largest_abs_offset_mm", "final_offset_mm", "drift_mm_per_us", "drift_se"),
                                                 rows.get(("p1.5_c0.02", "4-6", 50), (None,) * 5)))}
        off = offsets(run, ref, *BASELINE, t0)
        entry["onset_us"] = onset(off)
        report[name] = entry
        fmt = lambda c: ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0])))
        o, a = entry["original"]["baseline"], entry["amended"]["baseline"]
        if o["class"] is None:
            print(f"  {name:20s} {t0:g}-{max(run):g} us: too few saves"); continue
        print(f"  {name:20s} {t0:g}-{max(run):g} us  onset {entry['onset_us']}\n"
              f"      original: {o['class']:12s} drift {o['drift_mm_per_us']:+.4f} +- {o['drift_se']:.4f} (OLS)  final {o['final_offset_mm']:+.2f}  largest {o['largest_abs_offset_mm']:.2f}   all: {fmt(entry['original']['classes'])}\n"
              f"      amended:  {a['class']:12s} drift {a['drift_mm_per_us']:+.4f} +- {a['drift_se']:.4f} (HAC)  final {a['final_offset_mm']:+.2f} (mean)            all: {fmt(entry['amended']['classes'])}")


def paired(report):
    """Base of a control run against the run it repeats, at the paper's settings."""
    for name, other in PAIRED:
        a, b = load(name), _read(other)
        if a is None or b is None:
            continue
        common = [t for t in sorted(a) if t in b]
        d = [(t, base(a[t], *BASELINE) - base(b[t], *BASELINE)) for t in common
             if base(a[t], *BASELINE) is not None and base(b[t], *BASELINE) is not None]
        if not d:
            continue
        worst = max(d, key=lambda p: abs(p[1]))
        cells = sum(abs(x) > CELL + 1e-9 for _, x in d)
        print(f"  {name:20s} vs {other:16s} {d[0][0]:g}-{d[-1][0]:g} us: largest |difference| {abs(worst[1]):.2f} mm at {worst[0]:g} us; saves beyond one cell: {cells} of {len(d)}")
        report[name + ":paired"] = {"against": other, "span_us": [d[0][0], d[-1][0]], "largest_abs_diff_mm": abs(worst[1]),
                                    "at_us": worst[0], "saves_beyond_one_cell": cells, "saves": len(d)}


def recapture(report):
    """Rule fixed for the 350 us runs (before their results): over the last three pulse periods, the amended drift satisfies
    |drift| + 1.96 HAC SE < 0.02 mm/us, and the largest offset over 200-350 us is at most one cell above that over 70-200 us."""
    for name in RECAPTURE:
        run, ref = load(name), load("r_box_ref")
        if run is None or ref is None or max(run) < 349.5 or max(ref) < 349.5:
            print(f"  {name:20s} not yet at 350 us"); continue
        refname, t0, freq = REDUCED[name]
        off = offsets(run, ref, *BASELINE, t0)
        period = 1e3 / freq
        v, _, hac = fit([(t, o) for t, o in off if t >= off[-1][0] - 3 * period], freq, hac_lag=max(15, int(round(period))))
        early = max(o for t, o in off if t <= 200)
        late = max(o for t, o in off if t >= 200)
        ok = abs(v) + 1.96 * hac < 0.02 and late <= early + CELL
        print(f"  {name:20s} drift over the last {3 * period:g} us {v:+.4f} +- {hac:.4f} (HAC); largest offset 70-200 {early:+.2f}, "
              f"200-350 {late:+.2f} -> {'meets' if ok else 'fails'} the rule")
        report[name + ":recapture"] = {"drift": v, "se_hac": hac, "largest_70_200": early, "largest_200_350": late, "meets": ok}


def crop(report):
    ref = load(CROP["ref"])
    if ref is None:
        return
    t0, t1 = CROP["branch"], CROP["branch"] + CROP["window"]
    for name in CROP["cases"]:
        run = load(name)
        if run is None:
            continue
        at = {}
        for variant in AMENDED["variants"]:
            for hs in AMENDED["bases"].values():
                for t, o in offsets(run, ref, variant, hs, t0, t1):
                    at.setdefault(t, []).append(o)
        base_off = dict(offsets(run, ref, *BASELINE, t0, t1))
        cols = [t for t in (t0 + 10, t0 + 20, t0 + 30, t0 + 40) if t in base_off]
        print(f"  {name:20s} " + "  ".join(f"+{t - t0:g}: {base_off[t]:+5.2f} [{min(at[t]):+.2f}..{max(at[t]):+.2f}]" for t in cols))
        report[name] = {"reference": CROP["ref"], "offset_mm": {t: base_off[t] for t in cols},
                        "range_over_choices_mm": {t: [min(at[t]), max(at[t])] for t in cols}}


def hold(run, ref, cut, variant, hs, k):
    """(lo, hi]: the base, relative to the reference, first exceeds k cells behind its value at the cut at save hi;
    lo is the last save with a valid offset before hi."""
    def rel(t):
        if t not in ref:
            return None
        b, r = base(run[t], variant, hs), base(ref[t], variant, hs)
        return None if b is None or r is None else b - r
    r0 = rel(cut)
    if r0 is None:
        return None
    prev = cut
    for t in sorted(t for t in run if t > cut):
        d = rel(t)
        if d is None:
            continue
        if d - r0 > k * CELL:
            return prev - cut, t - cut
        prev = t
    return None


def holds(report):
    for name, refname, cut in OFF:
        run, ref = load(name), load(refname)
        if run is None or ref is None:
            continue
        cells = {}
        for k in KS:
            ivs = [hold(run, ref, cut, v, hs, k) for v in AMENDED["variants"] for hs in AMENDED["bases"].values()]
            got = [iv for iv in ivs if iv]
            cells[k] = {"baseline": hold(run, ref, cut, *BASELINE, k),
                        "range": [min(iv[0] for iv in got), max(iv[1] for iv in got)] if got else None,
                        "never": len(got) < len(ivs)}
        print(f"  {name:20s} " + "  ".join(f"k={k:g}: {c['baseline']} over choices ({c['range'][0]:g},{c['range'][1]:g}]"
                                          + (" some never" if c["never"] else "") for k, c in cells.items() if c["range"]))
        report[name + ":hold"] = {"reference": refname, "cut_us": cut, "by_k_cells": {str(k): c for k, c in cells.items()}}


if __name__ == "__main__":
    report = {}
    print("Baseline: pressure factor 1.5, burnt-gas cutoff 0.02, base y = 4-6 mm, drift over the last 50 us.\n"
          f"Original: {len(ORIGINAL['variants'])} variants x {len(ORIGINAL['bases'])} bases x {len(WINDOWS)} windows; "
          f"amended: {len(AMENDED['variants'])} x {len(AMENDED['bases'])} x {len(WINDOWS)} (see the docstring).")
    print("\nReduced-domain runs (and the low-domain and 0.15 mm runs against their own references)")
    classes(report)
    print("\nControls against the run they repeat (paper settings)")
    paired(report)
    print("\nRecapture rule for the 350 us runs")
    recapture(report)
    print(f"\nCrop, vs r_crop_cont, up to +{CROP['window']:g} us (baseline [range over the amended choices])")
    crop(report)
    print("\nHold after switch-off relative to the reference, us (k = threshold in cells; range over the amended choices)")
    holds(report)
    if "--json" in sys.argv:
        json.dump(report, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=str)
