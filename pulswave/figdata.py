"""Extract the data behind every manuscript figure from the saved fields into small JSON files.

Runs where the cases are (pure Python, one process per save); paper/figures.py plots the result.
"""
import json
import os
from multiprocessing import Pool

from . import build, foam, performance, profiles, reference, wave

BOX, CROP = "boxes/", "boxes/"
FRONT_CASES = (
    "open_wedge_J1_paper", BOX + "box_large", BOX + "large_off", BOX + "large_off_dry", BOX + "large_off_long",
    BOX + "large_reon", BOX + "large_f80k", BOX + "large_f80k_long", BOX + "large_f40k", BOX + "large_f20k",
    BOX + "large_half", BOX + "large_half_long", BOX + "large_narrow", CROP + "crop_grid", CROP + "crop_grid_fine",
    CROP + "crop_grid_off", CROP + "crop_grid_fine_off", CROP + "crop_grid_f80k_q", CROP + "crop_grid_d1",
    CROP + "crop_grid_d1_off",
)
EDGE_CASES = (CROP + "crop_grid", CROP + "crop_grid_off", CROP + "crop_grid_f80k_q", CROP + "crop_grid_d1",
              CROP + "crop_grid_d1_off")
HEIGHTS = (("open_wedge_J1_paper", ("9e-05", "0.0001")), (BOX + "box_large", ("7e-05",)))
# performance windows of tab:performance; the reference is evaluated over both windows
PERF = {
    BOX + "box_large": ("0.00012", "0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_f80k_long": ("0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_f40k": ("0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_f20k": ("0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_narrow": ("0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_half": ("0.00012", "0.000125", "0.00013", "0.000135", "0.00014", "0.000145"),
    BOX + "large_off": ("0.00012", "0.000125", "0.00013"),
}
PLANE_X, PLANE_Y = 0.1, 0.025
FIELD_WINDOW = (0.04, 0.1, 0.0, 0.02)
FIELDS = ((BOX + "box_large", "7e-05"), (BOX + "large_off", "7e-05"), (BOX + "large_off", "8e-05"),
          (BOX + "large_off", "9.5e-05"), (BOX + "large_off", "0.000125"))


def saves(case):
    part = foam._parts(case)[0]
    return sorted((t for t in os.listdir(part) if t != "0" and t[0].isdigit()), key=float)


def _setup(case):
    return build.load_setup(case) if os.path.exists(os.path.join(case, "setup.json")) else build.PRESETS["box_large"]


def _front(case, t):
    rows = foam.load(case, t)
    return [[h, x, ratio, gap] for h, x, ratio, gap in wave.structure(rows, dx=foam.cell_size(rows))]


def _edge(case, t):
    total, near, xs = wave.liquid_edge(foam.parcels(case, t))
    return {"liquid": total, "near_jet": near, "x5": xs[0], "x25": xs[1], "x50": xs[2]}


def _heights(case, t):
    rows = foam.load(case, t)
    return [[xm, hot, shock] for xm, hot, shock in wave.heights(rows, dx=foam.cell_size(rows))]


def _perf(case, t):
    rows = foam.load(case, t, performance.FIELDS)
    s = _setup(case)
    r = performance.summary(rows, s, 1.0, PLANE_X, PLANE_Y, dx=s.dx)
    p0_in, bands = performance.by_height(rows, PLANE_X, dx=s.dx)
    return {"recovery": r["p0_out"] / r["p0_in"], "burnt_fuel": r["fuel_burnt_out"], "mass": r["mass_out"],
            "p0_in": p0_in, "bands": [list(b) for b in bands]}


def _field(case, t):
    x0, x1, y0, y1 = FIELD_WINDOW
    rows = foam.load(case, t, foam.FIELDS + ("rho",))
    dx = foam.cell_size(rows)
    nx, ny = round((x1 - x0) / dx), round((y1 - y0) / dx)
    grid = {k: [None] * (nx * ny) for k in ("T", "p", "rho", "fuel", "CO2", "mach")}
    for r in rows:
        i, j = int((r["x"] - x0) / dx), int((r["y"] - y0) / dx)
        if 0 <= i < nx and 0 <= j < ny:
            k = j * nx + i
            grid["T"][k], grid["p"][k], grid["rho"][k] = round(r["T"], 1), round(r["p"], 0), r["rho"]
            grid["fuel"][k], grid["CO2"][k] = round(r["NXC7H16"], 4), round(r["CO2"], 4)
            grid["mach"][k] = round(profiles.mach(r), 3)
    drops = [[round(x * 1e3, 2), round(y * 1e3, 2), round(d * 1e6, 2)]
             for x, y, d, _ in foam.parcels(case, t) if x0 < x < x1 and y0 < y < y1]
    return {"x0": x0, "y0": y0, "dx": dx, "nx": nx, "ny": ny, "fields": grid, "droplets": drops}


KINDS = {"fronts": _front, "edges": _edge, "heights": _heights, "performance": _perf, "fields": _field}


def _run(job):
    kind, root, case, t = job
    return job, KINDS[kind](os.path.join(root, case), t)


def jobs(root, only=()):
    want = lambda case: not only or os.path.basename(case) in only
    for case in filter(want, FRONT_CASES):
        for t in saves(os.path.join(root, case)):
            yield "fronts", root, case, t
    for case in filter(want, EDGE_CASES):
        for t in saves(os.path.join(root, case)):
            yield "edges", root, case, t
    for case, ts in HEIGHTS:
        if want(case):
            for t in ts:
                yield "heights", root, case, t
    for case, ts in PERF.items():
        if want(case):
            for t in ts:
                yield "performance", root, case, t
    for case, t in FIELDS:
        if want(case):
            yield "fields", root, case, t


def _path(out, kind, case, t=None):
    name = os.path.basename(case) + (f"_{float(t) * 1e6:g}us" if t else "")
    return os.path.join(out, kind, name + ".json")


def extract(root, out, only=(), force=False, procs=8):
    todo = list(jobs(root, only))
    if not force:
        todo = [j for j in todo if not os.path.exists(_path(out, j[0], j[2], j[3] if j[0] == "fields" else None))]
    results = {}
    with Pool(procs) as pool:
        for (kind, _, case, t), r in pool.imap_unordered(_run, todo):
            results.setdefault((kind, case), {})[f"{float(t) * 1e6:g}"] = r
            print(kind, case, t, flush=True)
    for (kind, case), by_t in results.items():
        if kind == "fields":
            for t, r in by_t.items():
                _write(_path(out, kind, case, float(t) * 1e-6), r)
        else:
            _write(_path(out, kind, case), dict(sorted(by_t.items(), key=lambda kv: float(kv[0]))))
    _write(os.path.join(out, "reference.json"), {"fig3c_front": reference.FIG3C_FRONT})


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
