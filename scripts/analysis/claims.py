"""Recompute every number the manuscript states about the fronts from the tracked JSON in paper/data, so each can be checked.

Usage: python scripts/analysis/claims.py [paper/data]
"""
import json, os, statistics as st, sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "paper", "data")
CELL = 0.2


def _load(path):
    d = json.load(open(path))
    saves, scale = (d["saves"], 1e6) if "saves" in d else (d, 1.0)
    return {round(float(t) * scale, 2): {h: x for h, x, *_ in fr} for t, fr in
            ((t, v["front"] if isinstance(v, dict) else v) for t, v in saves.items())}


def run(*names):
    """A case chain: old figure-data segments (fronts/) and campaign segments (campaign/front/), later ones overriding."""
    out = {}
    for n in names:
        sub = "fronts" if n.startswith("old:") else "campaign/front"
        out.update(_load(os.path.join(D, sub, n.removeprefix("old:") + ".json")))
    return dict(sorted(out.items()))


def base(fr):
    xs = sorted(fr[h] for h in (4, 5, 6) if fr.get(h) is not None)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else None


def at(r, t, f=base):
    return f(r[min(r, key=lambda s: abs(s - t))])


def band(fr, hs=(6, 9)):
    xs = [fr[h] for h in hs if fr.get(h) is not None]
    return sum(xs) / len(xs) if xs else None


def hold_retreat(r, cut, span=20.0, k=1.5):
    """Hold: first save after the cut with the base more than k cells behind its position at the cut.
    Retreat: least-squares speed of the base over the following `span` us."""
    b0 = at(r, cut)
    after = [(t, base(f)) for t, f in r.items() if t > cut and base(f) is not None]
    t_go = next((t for t, b in after if b > b0 + k * CELL), None)
    if t_go is None:
        return None, None
    pts = [(t, b) for t, b in after if t_go <= t <= t_go + span]
    if len(pts) < 3:
        return t_go - cut, None
    tm, bm = st.mean(t for t, _ in pts), st.mean(b for _, b in pts)
    v = sum((t - tm) * (b - bm) for t, b in pts) / sum((t - tm) ** 2 for t, _ in pts)
    return t_go - cut, v


def maxdiff(a, b, f=base, t0=-1, t1=1e9):
    ts = [t for t in a if t in b and t0 <= t <= t1 and f(a[t]) is not None and f(b[t]) is not None]
    return max(abs(f(a[t]) - f(b[t])) for t in ts), len(ts)


def say(tag, text):
    print(f"[{tag}] {text}")


# jet switch-off: hold time and retreat speed
for name, r, cut in (("large (0.5 us saves)", run("large_off_hr"), 165.0), ("crop 0.2 mm", run("crop_off_hr"), 50.0),
                     ("crop 0.1 mm", run("crop_fine_off"), 50.0), ("crop 3-4x parcels", run("crop_off_np1"), 50.0)):
    h, v = hold_retreat(r, cut)
    say("off", f"{name}: base {at(r, cut):.2f} mm at cut-off {cut:.0f} us; holds {h} us; then retreats {v and round(v, 3)} mm/us")

# grid, wall model and parcel count, crop, jet off at 50 us
hr, fine = run("crop_off_hr"), run("crop_fine_off")
d_hr, d_fine = at(hr, 75) - at(hr, 50), at(fine, 75) - at(fine, 50)
say("grid", f"base displacement 50-75 us: 0.2 mm {d_hr:.2f} mm, 0.1 mm {d_fine:.2f} mm, ratio {d_fine / d_hr:.2f}")
for n in ("crop_off_fric", "crop_off_stick", "crop_off_np1"):
    m, k = maxdiff(run(n), hr, t0=50)
    say("robust", f"{n} vs crop_off_hr: largest base difference {m:.2f} mm ({m / CELL:.1f} cells) over {k} common saves")

# duty at a fixed 6.25 us off-time, and 25% at 4.7 us off-time
for n in ("crop_f80k", "crop_d375_100k", "crop_d25_120k", "crop_f160k_q"):
    r = run(n)
    say("duty", f"{n}: base {at(r, 50):.2f} mm at 50 us, {at(r, 70):.2f} at 70, {at(r, 90):.2f} at 90")
for n in ("crop_off_fric", "crop_off_stick"):
    r = run(n)
    say("duty", f"{n} (jet off, for comparison): base {at(r, 70):.2f} mm at 70 us, {at(r, 90):.2f} at 90")

# frequency at 50% duty, large domain, to 200 us, against the continuous jet
ref = run("old:box_large", "box_large_200")
chains = {"80 kHz": run("old:large_f80k", "old:large_f80k_long", "large_f80k_200"),
          "40 kHz": run("old:large_f40k", "large_f40k_200"), "30 kHz": run("large_f30k", "large_f30k_200"),
          "20 kHz": run("old:large_f20k", "large_f20k_200"),
          "half width, patch": run("large_narrow_patch"), "half width, cone": run("old:large_narrow", "large_narrow_long"),
          "half velocity": run("old:large_half", "old:large_half_long"), "jet off": run("old:large_off", "old:large_off_long")}
say("ref", f"continuous jet: base {at(ref, 150):.2f} mm at 150 us, {at(ref, 200):.2f} at 200; y6-9 {at(ref, 200, band):.2f}")
for k, r in chains.items():
    late = [t for t in r if 150 <= t <= 200 and base(r[t]) is not None]
    worst = max(base(r[t]) for t in late) if late else None
    say("200us", f"{k}: base at 200 us {at(r, 200):.2f} mm ({at(r, 200) - at(ref, 200):+.2f} vs ref), worst over 150-200 {worst:.2f};"
                 f" y6-9 at 200 {at(r, 200, band):.2f} ({at(r, 200, band) - at(ref, 200, band):+.2f})")
p, f80 = chains["half width, patch"], chains["80 kHz"]
ts = [t for t in f80 if t in p and 150 <= t <= 200]
gap = [band(p[t]) - band(f80[t]) for t in ts]
say("equal", f"y6-9, patch half width minus 80 kHz over 150-200 us: {min(gap):.2f} to {max(gap):.2f} mm, mean {st.mean(gap):.2f} ({len(ts)} saves)")
cone = chains["half width, cone"]
say("equal", f"cone half width: base {at(cone, 100):.2f} at 100 us, {at(cone, 145):.2f} at 145, {at(cone, 175):.2f} at 175, {at(cone, 200):.2f} at 200")

# restarts are deterministic: a restart from another time gives no new realization
for a, b in (("large_narrow_seed", "large_narrow_long"), ("large_f80k_rep", "large_f80k_200")):
    allh = lambda fr: max((x for h, x in fr.items() if h <= 9 and x is not None), default=None)
    m, k = maxdiff(run(a), run(b))
    say("restart", f"{a} vs {b}: largest base difference {m:.2f} mm over {k} common saves")

# re-on, dry, wider jet (old figure-data segments, current tracker)
reon, off = run("old:large_reon"), run("old:large_off")
say("reon", "jet back on at 95 us: base " + ", ".join(f"{t:.0f}:{base(f):.1f}" for t, f in reon.items()))
for n, cut in (("old:large_off", 70.0), ("old:large_off_dry", 70.0), ("old:crop_grid_off", 50.0), ("old:crop_grid_d1_off", 50.0)):
    h, v = hold_retreat(run(n), cut)
    say("off", f"{n.removeprefix('old:')}: holds {h} us; then retreats {v and round(v, 3)} mm/us")

say("St", f"St = f d / u = {80e3 * 0.5e-3 / 60.83:.2f} at 80 kHz (d = 0.5 mm, u = 60.83 m/s)")

# wall liquid layer after switch-off (crop, x = 49.5-100 mm, y < 3 mm; per-parcel density)
for n, cut in (("crop_grid_off", 50.0), ("crop_grid_d1_off", 50.0), ("crop_grid_f80k_q", 50.0)):
    e = {float(t): v for t, v in json.load(open(os.path.join(D, "edges", n + ".json"))).items()}
    r = run("old:" + n)
    ts = sorted(t for t in e if t >= cut)
    tm, xm = st.mean(ts), st.mean(e[t]["x25"] * 1e3 for t in ts)
    v25 = sum((t - tm) * (e[t]["x25"] * 1e3 - xm) for t in ts) / sum((t - tm) ** 2 for t in ts)
    off = [base(r[t]) - e[t]["x25"] * 1e3 for t in ts if t in r and base(r[t]) is not None]
    say("layer", f"{n}: liquid {e[ts[0]]['liquid'] * 1e9:.0f} -> {e[ts[-1]]['liquid'] * 1e9:.0f} ug over {ts[0]:.0f}-{ts[-1]:.0f} us"
                 f" ({(e[ts[-1]]['liquid'] / e[ts[0]]['liquid'] - 1) * 100:+.0f}%); 25% point moves {v25:.3f} mm/us;"
                 f" base minus 25% point {min(off):+.2f} to {max(off):+.2f} mm")

# plug-region gas speed: median over saves per case (fitted cases), and the out-of-sample test
med = st.median
for sub, tag in (("plug", "plug fit"), ("plug_gas", "plug test")):
    rows = []
    for f in sorted(os.listdir(os.path.join(D, "campaign", sub))):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(D, "campaign", sub, f)))
            g = [v["gas_ux"] for v in d["saves"].values() if v["gas_ux"] is not None]
            rows.append(f"{d['case']} {med(g):.0f}")
    say(tag, "median plug gas speed (m/s): " + ", ".join(rows))

# plug removed at switch-off (crop_off_cut: wall liquid from the jet to about 52.5 mm deleted at 50 us), and no-slip gas wall
for n in ("crop_off_cut", "crop_noslip_off"):
    r = run(n)
    h, v = hold_retreat(r, 50.0)
    say("off", f"{n}: base {at(r, 50):.2f} at 50 us, " + ", ".join(f"{t:.0f}:{base(f):.1f}" for t, f in r.items() if base(f) is not None)
               + f"; holds {h} us, then {v and round(v, 3)} mm/us")
m, k = maxdiff(run("crop_noslip_off"), hr, t0=50)
say("robust", f"crop_noslip_off vs crop_off_hr: largest base difference {m:.2f} mm ({m / CELL:.1f} cells) over {k} common saves")

# 0.15 mm against 0.2 mm (crop, cut at 50 us), crop against reduced domain at equal time after cut-off, droplet escape wall
m, k = maxdiff(run("old:crop_grid_fine_off"), run("old:crop_grid_off"), t0=50)
say("robust", f"crop 0.15 vs 0.2 mm after cut-off: largest base difference {m:.2f} mm over {k} saves")
c, l = run("old:crop_grid_off"), run("old:large_off")
d = [abs(base(c[t]) - base(l[t + 20])) for t in c if t >= 50 and t + 20 in l and base(c[t]) and base(l[t + 20])]
say("robust", f"crop (cut 50 us) vs reduced domain (cut 70 us), equal time after cut: largest base difference {max(d):.2f} mm over {len(d)} saves")
esc = _load(os.path.join(D, "campaign", "plug_gas", "large_off_escape.json"))
m, k = maxdiff(esc, l, t0=70)
say("robust", f"droplet escape wall vs rebound (reduced domain, jet off at 70 us): largest base difference {m:.2f} mm over {k} saves")

# the continuous-jet reference: base drift and liquid inventory (y < 3 mm; near the jet: x < 53 mm)
liq = {}
for n in ("box_large", "box_large_200"):
    for t, v in json.load(open(os.path.join(D, "campaign", "front", n + ".json")))["saves"].items():
        liq[round(float(t) * 1e6)] = (v["liquid_ug"], v["near_ug"])
t0, t1 = min(liq), max(liq)
say("ref", f"base " + ", ".join(f"{t:.0f}:{base(ref[t]):.1f}" for t in ref if t >= 70 and t % 20 == 10 and base(ref[t])))
say("ref", f"liquid in y < 3 mm {liq[t0][0]:.0f} ug at {t0} us -> {liq[t1][0]:.0f} at {t1} ({(liq[t1][0] - liq[t0][0]) / (t1 - t0):.1f} ug/us"
           f" against 41.36 injected); near the jet {min(v[1] for v in liq.values()):.0f}-{max(v[1] for v in liq.values()):.0f} ug")

# smaller domain (90 x 35 mm) against the reduced domain (120 x 45 mm), continuous jet, equal times
small, large = _load(os.path.join(D, "campaign", "plug_gas", "box_small.json")), run("old:box_large")
for hs in ((4, 5, 6), (9,), (15,), (22,), (26,)):
    ts = [t for t in small if t in large and t >= 30 and all(small[t].get(h) is not None and large[t].get(h) is not None for h in hs)]
    m = max(abs(st.mean(small[t][h] for h in hs) - st.mean(large[t][h] for h in hs)) for t in ts) if ts else None
    say("domain", f"90 x 35 vs 120 x 45 mm at y = {hs}: largest difference {m and round(m, 2)} mm over {len(ts)} saves from 30 us")

# robustness to 90 us against crop_grid_off (same set-up as crop_off_hr, saves to 90 us)
g = run("old:crop_grid_off")
m, k = maxdiff(hr, g, t0=50)
say("robust", f"crop_off_hr vs crop_grid_off (same set-up): largest base difference {m:.2f} mm over {k} saves")
for n in ("crop_off_fric", "crop_off_stick", "crop_noslip_off", "crop_off_np1"):
    m, k = maxdiff(run(n), g, t0=50)
    say("robust", f"{n} vs crop_grid_off to the end of the run: largest base difference {m:.2f} mm ({m / CELL:.1f} cells) over {k} saves")

# hold and retreat over thresholds of 1.25-2.5 cells
for n, cut in (("large_off_hr", 165.0), ("crop_off_hr", 50.0), ("crop_fine_off", 50.0), ("old:large_off", 70.0),
               ("old:large_off_dry", 70.0), ("crop_off_cut", 50.0), ("old:crop_grid_off", 50.0), ("old:crop_grid_d1_off", 50.0)):
    hv = [hold_retreat(run(n), cut, k=k) for k in (1.25, 1.5, 2.0, 2.5)]
    hs, vs = [h for h, _ in hv if h is not None], [v for _, v in hv if v is not None]
    say("range", f"{n.removeprefix('old:')}: hold {min(hs):g}-{max(hs):g} us, retreat " + (f"{min(vs):.3f}-{max(vs):.3f} mm/us" if vs else "- (fewer than 3 saves)"))

# 25% duty at 80 kHz (9.4 us off) and the 1 mm jet, crop
q, d1, cg = run("old:crop_grid_f80k_q"), run("old:crop_grid_d1", "old:crop_grid_d1_off"), run("old:crop_grid", "old:crop_grid_off")
say("duty", "crop_grid_f80k_q: base " + ", ".join(f"{t:.0f}:{at(q, t):.1f}" for t in (50, 60, 70, 80, 90))
            + "; jet off " + ", ".join(f"{t:.0f}:{at(cg, t):.1f}" for t in (50, 60, 70, 80, 90)))
say("width", "1 mm jet: base " + ", ".join(f"{t:.0f}:{at(d1, t):.1f}" for t in (40, 50, 60, 70, 80))
             + "; 0.5 mm " + ", ".join(f"{t:.0f}:{at(cg, t):.1f}" for t in (40, 50, 60, 70, 80)))
say("reon", "behind the reference: " + ", ".join(f"{t:.0f}:{at(reon, t) - at(ref, t):+.1f}" for t in (100, 110, 120, 130)))
lo = run("old:large_off", "old:large_off_long")
say("off", "jet off to 200 us: base " + ", ".join(f"{t:.0f}:{at(lo, t):.1f}" for t in (70, 100, 130, 160, 200))
           + "; y15 " + ", ".join(f"{t:.0f}:{at(lo, t, lambda f: f.get(15)):.1f}" for t in (70, 100, 130, 160, 200)))

# performance over 125-145 us (paper/data/performance, regenerated with the inflow fix; no plane check stored)
perf = lambda c: json.load(open(os.path.join(D, "performance", c + ".json")))
pref = perf("box_large")
for c in ("large_f80k_long", "large_f40k", "large_f20k", "large_narrow", "large_half", "large_off"):
    r = perf(c)
    ts = sorted((t for t in r if t in pref and 125 <= float(t) <= 145), key=float)
    rec, fuel = st.mean(r[t]["recovery"] for t in ts), st.mean(r[t]["burnt_fuel"] for t in ts) * 1e3
    say("perf", f"{c} {ts[0]}-{ts[-1]} us: recovery {rec:.3f} (ref {st.mean(pref[t]['recovery'] for t in ts):.3f}),"
                f" burnt {fuel:.2f} g/s (ref {st.mean(pref[t]['burnt_fuel'] for t in ts) * 1e3:.2f})")

# plug region (x = 50-52 mm, y < 1 mm): when the gas there first exceeds 500 m/s, against when the base leaves
def plug(sub, *names):
    out = {}
    for n in names:
        for t, v in json.load(open(os.path.join(D, "campaign", sub, n + ".json")))["saves"].items():
            out[round(float(t) * 1e6, 2)] = v
    return dict(sorted(out.items()))


for sub, names, cut in (("plug", ("crop_off_hr",), 50.0), ("plug", ("large_off_hr",), 165.0), ("plug", ("crop_off_cut",), 50.0),
                        ("plug_gas", ("large_half", "large_half_long"), 70.0), ("plug", ("large_narrow_long",), 145.0),
                        ("plug_gas", ("crop_grid_f80k_q",), 50.0)):
    r = plug(sub, *names)
    fr = {t: {h: x for h, x, *_ in v["front"]} for t, v in r.items()}
    b0 = base(fr[min(fr, key=lambda s: abs(s - cut))])
    fast = next((t for t, v in r.items() if t >= cut and v["gas_ux"] > 500), None)
    go = next((t for t, f in fr.items() if t > cut and base(f) is not None and base(f) > b0 + 1.5 * CELL), None)
    liq = [f"{t:.0f}:{v['liq_ug_plug']:.0f}" for t, v in r.items() if "liq_ug_plug" in v and cut <= t <= cut + 20 and t % 5 == 0]
    say("plug", f"{names[-1]} from {cut:.0f} us: gas above 500 m/s first at {fast} us, base leaves at {go} us"
                + (f"; plug liquid ug {', '.join(liq)}" if liq else ""))

# 50% duty: largest lag behind the reference over the whole run, and when
for k in ("80 kHz", "40 kHz", "30 kHz", "20 kHz"):
    r = chains[k]
    lag = [(base(r[t]) - at(ref, t), t) for t in r if t >= 70 and base(r[t]) is not None]
    m, t = max(lag)
    say("lag", f"{k}: largest base lag behind the reference over 70-200 us {m:+.1f} mm at {t:.0f} us; at 145 us {at(r, 145) - at(ref, 145):+.1f}")

# matched windows: base displacement over 10-20 us after the cut, liquid removed against left in place (same save interval)
def slope(r, t0, t1):
    pts = [(t, base(f)) for t, f in r.items() if t0 <= t <= t1 and base(f) is not None]
    tm, bm = st.mean(t for t, _ in pts), st.mean(b for _, b in pts)
    return sum((t - tm) * (b - bm) for t, b in pts) / sum((t - tm) ** 2 for t, _ in pts)


for a, b, cut in (("crop_off_cut", "old:crop_grid_off", 50.0), ("old:large_off_dry", "old:large_off", 70.0)):
    for w in ((cut, cut + 20), (cut + 10, cut + 20)):
        va, vb = slope(run(a), *w), slope(run(b), *w)
        say("matched", f"{a.removeprefix('old:')} vs {b.removeprefix('old:')} over {w[0] - cut:.0f}-{w[1] - cut:.0f} us after the cut:"
                       f" {va:.3f} vs {vb:.3f} mm/us, ratio {va / vb:.2f}")

# half-width patch jet against 80 kHz at the base, 150-200 us
ts = [t for t in f80 if t in p and 150 <= t <= 200 and base(p[t]) is not None and base(f80[t]) is not None]
g = [base(p[t]) - base(f80[t]) for t in ts]
say("equal", f"base, patch half width minus 80 kHz over 150-200 us: {min(g):.2f} to {max(g):.2f} mm, mean {st.mean(g):.2f}")

# jet-off front higher up, 70-160 us and at 200 us
for h in (9, 12, 15, 18, 22):
    xs = [lo[t].get(h) for t in lo if 70 <= t <= 160 and lo[t].get(h) is not None]
    say("off", f"jet off, y = {h} mm: {min(xs):.1f}-{max(xs):.1f} mm over 70-160 us; {at(lo, 200, lambda f: f.get(h))} at 200 us")

# base displacement 20 us after the cut, liquid removed against left in place
for a, b, cut in (("crop_off_cut", "old:crop_grid_off", 50.0), ("old:large_off_dry", "old:large_off", 70.0)):
    ra, rb = run(a), run(b)
    say("matched", f"displacement 20 us after the cut: {a.removeprefix('old:')} {at(ra, cut + 20) - at(ra, cut):.1f} mm,"
                   f" {b.removeprefix('old:')} {at(rb, cut + 20) - at(rb, cut):.1f} mm")

# 50% duty: base displacement within each on- and off-phase (phases start with an on-phase at 70 us)
for k, f in (("20 kHz", 20.0), ("30 kHz", 30.0)):
    r, period = chains[k], 1e3 / f
    edges = [70 + i * period / 2 for i in range(int((200 - 70) / (period / 2)) + 1)]
    moves = [f"{'on' if i % 2 == 0 else 'off'} {a:.0f}-{b:.0f}: {at(r, b) - at(r, a):+.1f}" for i, (a, b) in enumerate(zip(edges, edges[1:]))]
    say("phase", f"{k}: base displacement per phase (mm): " + ", ".join(moves))

# displacement after the cut against the reference at equal times (the reference itself drifts upstream after 70 us)
for a, cut in (("old:large_off", 70.0), ("old:large_off_dry", 70.0)):
    r = run(a)
    own, rel = at(r, cut + 20) - at(r, cut), (at(r, cut + 20) - at(ref, cut + 20)) - (at(r, cut) - at(ref, cut))
    say("relref", f"{a.removeprefix('old:')}: displacement 20 us after the cut {own:.1f} mm from its own start, {rel:.1f} mm against the reference")

# outcome per case: largest offset behind the reference over 70-200 us, offset at 200 us, and drift over 150-200 us
for k, r in chains.items():
    off = [(base(r[t]) - at(ref, t), t) for t in r if t >= 70 and base(r[t]) is not None]
    m, tm = max(off)
    say("outcome", f"{k}: largest offset {m:+.1f} mm at {tm:.0f} us, {at(r, 200) - at(ref, 200):+.1f} at 200 us, drift 150-200 us {slope(r, 150, 200):+.3f} mm/us")

# pressure ratio across the front at the base heights and at y = 9 mm, jet off and reference
def ratios(*names):
    out = {}
    for n in names:
        sub = "fronts" if n.startswith("old:") else "campaign/front"
        d = json.load(open(os.path.join(D, sub, n.removeprefix("old:") + ".json")))
        saves, scale = (d["saves"], 1e6) if "saves" in d else (d, 1.0)
        out.update({round(float(t) * scale, 2): {h: p for h, x, p, *_ in (v["front"] if isinstance(v, dict) else v) if x is not None}
                    for t, v in saves.items()})
    return dict(sorted(out.items()))


for name, r in (("jet off", ratios("old:large_off", "old:large_off_long")), ("reference", ratios("old:box_large", "box_large_200"))):
    rows = [(t, [f[h] for h in (4, 5, 6) if f.get(h)], f.get(9)) for t, f in r.items() if t >= 70 and t % 15 == 10]
    say("ratio", f"{name}: median pressure ratio y 4-6 / y 9: " + ", ".join(
        f"{t:.0f}:{st.median(b):.1f}/{n9:.0f}" for t, b, n9 in rows if b and n9))

# the plug as defined in the text (x < 52.5 mm, y < 3 mm), crop, jet off at 50 us
e = {float(t): v for t, v in json.load(open(os.path.join(D, "edges", "crop_grid_off.json"))).items()}
say("plug", "defined plug (ug): " + ", ".join(f"{t - 50:+.0f}:{e[t]['near_jet'] * 1e9:.0f}" for t in sorted(e) if t >= 50)
            + f"; wall layer at the cut {e[50.0]['liquid'] * 1e9:.0f}")

# save-to-save scatter of the reference on the plane, 150-200 us
pr200 = json.load(open(os.path.join(D, "campaign", "performance", "box_large_200.json")))
v = [pr200[t] for t in pr200 if 150e-6 - 1e-9 <= float(t) <= 200e-6 + 1e-9]
say("perf", f"reference 150-200 us, {len(v)} saves: recovery sd {st.stdev(x['recovery'] for x in v):.4f},"
            f" burnt fuel sd {st.stdev(x['burnt_fuel'] for x in v) * 1e3:.3f} g/s")

# hold measured against the reference at equal times (base minus reference, relative to its value at the cut)
for a, cut in (("old:large_off", 70.0), ("old:large_off_dry", 70.0)):
    r = run(a)
    d0 = at(r, cut) - at(ref, cut)
    for k in (1.25, 1.5, 2.0, 2.5):
        go = next((t for t in r if t > cut and t in ref and base(r[t]) and base(ref[t]) and base(r[t]) - base(ref[t]) - d0 > k * CELL), None)
        say("relref", f"{a.removeprefix('old:')}: hold against the reference at {k} cells: {go and go - cut} us")

# largest upstream jump of the base between consecutive saves, 50% duty
for k in ("80 kHz", "40 kHz", "30 kHz", "20 kHz"):
    pts = [(t, base(f)) for t, f in chains[k].items() if t >= 70 and base(f) is not None]
    jumps = sorted(((b0 - b1, t0, t1) for (t0, b0), (t1, b1) in zip(pts, pts[1:]) if b0 - b1 >= 0.8), reverse=True)
    say("jump", f"{k}: upstream jumps of at least 0.8 mm between saves: " + ", ".join(f"{j:.1f} mm at {t0:.0f}-{t1:.0f} us" for j, t0, t1 in jumps))

# gas colder than the freestream (T < 600 K) downstream of the jet, jet off at 70 us (paper/data/fields, Fig. 6)
for name in ("large_off_70us", "large_off_95us", "large_off_125us"):
    d = json.load(open(os.path.join(D, "fields", name + ".json")))
    nx, dx, x0, y0, f = d["nx"], d["dx"], d["x0"], d["y0"], d["fields"]
    cells = [(1e3 * (x0 + (i % nx + 0.5) * dx), 1e3 * (y0 + (i // nx + 0.5) * dx), i) for i, T in enumerate(f["T"]) if T is not None and T < 600]
    cells = [(x, y, i) for x, y, i in cells if x > 52]
    md = lambda k: st.median(f[k][i] for *_, i in cells)
    say("cold", f"{name}: {len(cells)} cells, x {min(c[0] for c in cells):.0f}-{max(c[0] for c in cells):.0f} mm, y up to {max(c[1] for c in cells):.1f} mm;"
                f" median C7H16 {md('fuel'):.2f}, Mach {md('mach'):.1f}, p {md('p') / 101325:.1f} atm; CO2 at most {max(f['CO2'][i] for *_, i in cells):.3f}")
