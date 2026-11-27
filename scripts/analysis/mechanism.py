"""Time series of the processes around the base after a jet change.

Per save it writes:
  base                 x of the base (median front over y = 4-6 mm), mm
  ratio_base, gap_base median front pressure ratio and shock-to-burnt-gas gap over y = 4-6 mm
  ratio_jet            median front pressure ratio over y = 1-3 mm (the jet-induced shock while the jet acts)
  q_base               heat release integrated over x = base-1 .. base+4 mm, y = 3-7 mm, W per m of depth
  q_wall               heat release integrated over x = 49.5-60 mm, y < 3 mm
  plug_liquid          liquid mass in x = 49.5-52.5 mm, y < 3 mm, ug (per 2 mm depth)
  layer_liquid         liquid mass in x = 49.5-100 mm, y < 3 mm, ug
  evap_plug            evaporation rate in the plug region, g/s per 2 mm depth (rhoTrans of the last step / deltaT), if written
  base_C7H16/O2        mean vapor and O2 just ahead of the base (x = base-2..base mm, y = 3-7 mm): the mixture the base burns
  layer_C7H16/O2       mean vapor and O2 in the near-wall layer behind the jet (x = 50-60 mm, y < 1 mm)
  plug_ux, plug_mach   mass-weighted streamwise gas speed and Mach number in x = 50-52.5 mm, y < 1 mm
  subsonic_area        area of gas with M < 1 in x = 49.5-90 mm, y < 3 mm, mm^2
  upstream_C7H16/O2    mean vapor and O2 mass fractions in x = 45-49.5 mm, y < 1 mm (the gas reaching the jet; unaffected by it)
  sumY_max             largest sum of species mass fractions in x = 45-100 mm, y < 3 mm (vapor-defect monitor)
Usage: python scripts/analysis/mechanism.py <case_dir> <out.json> [t0_us t1_us]
Single process. Mach numbers use Cantera's frozen sound speed of the local mixture (mechanisms/nHeptane.yaml).
"""
import glob, json, math, os, re, statistics as st, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import cantera as ct
from pulswave import foam, wave

DEPTH = 2e-3
case, out = sys.argv[1], sys.argv[2]
t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0, 1e9)
gas = ct.Solution(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mechanisms", "nHeptane.yaml"))
SPECIES = re.search(r"species\s+\d+\s*\(([^)]*)\)", open(os.path.join(case, "constant", "speciesThermo")).read()).group(1).split()


def read_internal(path, n):
    """Read a volScalarField::Internal (spray source) file, whose data sit under 'value' instead of 'internalField'."""
    txt = open(path).read()
    m = re.search(r"value\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\n?\(\s*(.*?)\)\s*;", txt, re.S)
    if m:
        return [float(v) for v in m.group(2).split()]
    m = re.search(r"value\s+uniform\s+([^;\s]+)\s*;", txt)
    return [float(m.group(1))] * n


times = sorted((t for t in os.listdir(os.path.join(case, "processor0")) if re.fullmatch(r"[0-9.e+-]+", t) and t != "0"), key=float)
times = [t for t in times if t0 <= float(t) * 1e6 <= t1]
result = {}
for t in times:
    extra = ["Qdot", "rho"]
    rows = foam.load(case, t, foam.FIELDS + tuple(extra))
    CELL = foam.cell_size(rows)  # grid spacing of this case (0.2, 0.15 or 0.1 mm)
    front = wave.structure(rows, dx=CELL)
    base = wave.base(front)
    fr = {h: (x, r, g) for h, x, r, g in front}
    med = lambda hs, k: st.median([fr[h][k] for h in hs if fr.get(h) and fr[h][k] is not None]) if any(fr.get(h) and fr[h][k] is not None for h in hs) else None
    A = CELL * CELL
    q_base = None if base is None else sum(r["Qdot"] for r in rows if base - 1 <= r["x"] * 1e3 <= base + 4 and 3e-3 <= r["y"] <= 7e-3) * A
    q_wall = sum(r["Qdot"] for r in rows if 0.0495 <= r["x"] <= 0.060 and r["y"] < 3e-3) * A

    # near-wall region with full composition, for Mach and the species-sum monitor
    region = [i for i, r in enumerate(rows) if 0.045 <= r["x"] <= 0.100 and r["y"] < 3e-3]
    full = {}
    for part in foam._parts(case):
        pass
    # load all species only in the region: read per processor and map by cell order
    allY, k0 = {}, 0
    for part in foam._parts(case):
        C = foam._read(os.path.join(part, "0", "C"), 0)
        n = len(C)
        idx = [k0 + i for i, c in enumerate(C) if 0.045 <= c[0] <= 0.100 and c[1] < 3e-3]
        if idx:
            local = [i - k0 for i in idx]
            data = {s: foam._read(os.path.join(part, t, s), n) for s in SPECIES}
            for g_i, l_i in zip(idx, local):
                allY[g_i] = [data[s][l_i] for s in SPECIES]
        k0 += n
    mach, sumY = {}, []
    for i in region:
        r, Y = rows[i], allY[i]
        sumY.append(sum(Y))
        try:
            gas.TPY = r["T"], r["p"], dict(zip(SPECIES, Y))
            mach[i] = math.hypot(r["ux"], r["uy"]) / gas.sound_speed
        except ct.CanteraError:
            mach[i] = float("nan")
    plug = [i for i in region if 0.050 <= rows[i]["x"] <= 0.0525 and rows[i]["y"] < 1e-3]
    m = sum(rows[i]["rho"] for i in plug)
    plug_ux = sum(rows[i]["rho"] * rows[i]["ux"] for i in plug) / m
    plug_mach = sum(rows[i]["rho"] * mach[i] for i in plug) / m
    subsonic = sum(1 for i in region if rows[i]["x"] >= 0.0495 and rows[i]["x"] <= 0.090 and mach[i] < 1) * A * 1e6
    up = [r for r in rows if 0.045 <= r["x"] <= 0.0495 and r["y"] < 1e-3]
    # gas reaching the base (just ahead of and at the base, y = 3-7 mm) and the near-wall layer behind the jet (x = 50-60 mm, y < 1 mm)
    at_base = [] if base is None else [r for r in rows if base - 2 <= r["x"] * 1e3 <= base and 3e-3 <= r["y"] <= 7e-3]
    layer = [r for r in rows if 0.050 <= r["x"] <= 0.060 and r["y"] < 1e-3]
    dt_step = float(re.search(r"deltaT\s+(\S+);", open(os.path.join(foam._parts(case)[0], t, "uniform", "time")).read()).group(1))

    parts = foam.parcels(case, t)
    plug_liq = sum(p[3] for p in parts if 0.0495 <= p[0] <= 0.0525 and p[1] < 3e-3) * 1e9
    layer_liq = sum(p[3] for p in parts if 0.0495 <= p[0] <= 0.100 and p[1] < 3e-3) * 1e9
    evap = None
    rt = os.path.join(foam._parts(case)[0], t, "sprayCloud:rhoTrans_NXC7H16")
    if os.path.exists(rt):
        vals = []
        for part in foam._parts(case):
            C = foam._read(os.path.join(part, "0", "C"), 0)
            v = read_internal(os.path.join(part, t, "sprayCloud:rhoTrans_NXC7H16"), len(C))
            vals += [vi for c, vi in zip(C, v) if 0.0495 <= c[0] <= 0.0525 and c[1] < 3e-3]
        evap = sum(vals) / dt_step * 1e3  # g/s per 2 mm depth: mass transferred in the last step / that step
    result[t] = {"base": base, "ratio_base": med((4, 5, 6), 1), "gap_base": med((4, 5, 6), 2), "ratio_jet": med((1, 2, 3), 1),
                 "q_base": q_base, "q_wall": q_wall, "plug_liquid": plug_liq, "layer_liquid": layer_liq, "evap_plug": evap,
                 "plug_ux": plug_ux, "plug_mach": plug_mach, "subsonic_area": subsonic,
                 "upstream_C7H16": st.mean(r["NXC7H16"] for r in up), "upstream_O2": st.mean(r["O2"] for r in up),
                 "base_C7H16": st.mean(r["NXC7H16"] for r in at_base) if at_base else None,
                 "base_O2": st.mean(r["O2"] for r in at_base) if at_base else None,
                 "layer_C7H16": st.mean(r["NXC7H16"] for r in layer), "layer_O2": st.mean(r["O2"] for r in layer),
                 "dx_mm": CELL * 1e3,
                 "sumY_max": max(sumY)}
    v = result[t]
    print(f"{float(t)*1e6:6.1f} us  base {v['base']}  ratio jet/base {v['ratio_jet'] and round(v['ratio_jet'],1)}/{v['ratio_base'] and round(v['ratio_base'],1)}"
          f"  gap {v['gap_base']}  q_base {v['q_base'] and round(v['q_base']/1e3)} kW/m  q_wall {round(v['q_wall']/1e3)} kW/m"
          f"  plug {plug_liq:.0f} ug  layer {layer_liq:.0f} ug  plug ux {plug_ux:.0f} m/s M {plug_mach:.2f}  subsonic {subsonic:.1f} mm2"
          f"  up C7H16 {v['upstream_C7H16']:.3f} O2 {v['upstream_O2']:.3f}  sumY {v['sumY_max']:.3f}", flush=True)
json.dump({"case": os.path.basename(os.path.normpath(case)), "saves": result}, open(out, "w"), indent=1)
