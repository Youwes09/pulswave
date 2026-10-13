import glob
import math
import os
import re

ATM = 101325.0
FIELDS = ("T", "p", "U", "NXC7H16", "O2", "CO2", "H2O")


def _read(path, n):
    if not os.path.exists(path):
        return [0.0] * n
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*\n\d+\s*\n\(\n(.*?)\n\)\s*;", txt, re.S)
    if m:
        lines = m.group(2).split("\n")
        if m.group(1) == "vector":
            return [tuple(float(v) for v in l.strip("() ").split()) for l in lines]
        return [float(l) for l in lines]
    v = re.search(r"internalField\s+uniform\s+(\([^)]*\)|[^;\s]+)\s*;", txt).group(1)
    return [tuple(float(s) for s in v.strip("()").split()) if v.startswith("(") else float(v)] * n


def _parts(case):
    return sorted(glob.glob(os.path.join(case, "processor*"))) or [case]


def load(case, t, fields=FIELDS):
    if not os.path.isdir(os.path.join(_parts(case)[0], t)):
        raise FileNotFoundError(f"{case} has no save at t = {t}")
    rows = []
    for part in _parts(case):
        C = _read(os.path.join(part, "0", "C"), 0)
        n = len(C)
        data = {f: _read(os.path.join(part, t, f), n) for f in fields}
        for i, c in enumerate(C):
            r = {"x": c[0], "y": c[1]}
            for f, vals in data.items():
                if f == "U":
                    r["ux"], r["uy"] = vals[i][0], vals[i][1]
                else:
                    r[f] = vals[i]
            rows.append(r)
    return rows


def cell_size(rows):
    xs = sorted({round(r["x"], 9) for r in rows})
    return min(b - a for a, b in zip(xs, xs[1:]))


def _cloud_list(txt):
    m = re.search(r"\n(\d+)\s*\n\(\n(.*?)\n\)\s*\n", txt, re.S)
    if m:
        return m.span(), m.group(2).split("\n")
    m = re.search(r"\n(\d+)\{([^}]*)\}", txt)
    return (m.span(), [m.group(2)] * int(m.group(1))) if m else ((0, 0), [])


def _cloud_field(cloud, name):
    return _cloud_list(open(os.path.join(cloud, name)).read())[1]


def _cloud_cells(cloud):
    return [int(m.group(1)) for m in re.finditer(r"\)\s+(\d+)\s+\d+\s+\d+", open(os.path.join(cloud, "positions")).read())]


def _clouds(case, t):
    for part in _parts(case):
        cloud = os.path.join(part, t, "lagrangian", "sprayCloud")
        if os.path.exists(os.path.join(cloud, "positions")):
            yield _read(os.path.join(part, "0", "C"), 0), cloud


def filter_cloud(cloud, keep):
    for name in os.listdir(cloud):
        path = os.path.join(cloud, name)
        txt = open(path).read()
        (a, b), items = _cloud_list(txt)
        assert len(items) == len(keep), path
        kept = [v for v, k in zip(items, keep) if k]
        body = "\n" + str(len(kept)) + "\n(\n" + "".join(v + "\n" for v in kept) + ")\n"
        open(path, "w").write(txt[:a] + body + txt[b:])


def injected_at(cloud):
    return [tuple(float(v) for v in s.strip("()").split()) for s in _cloud_field(cloud, "position0")]


def parcels(case, t, rho_l=680.0, extra=()):
    out = []
    for C, cloud in _clouds(case, t):
        d = [float(v) for v in _cloud_field(cloud, "d")]
        n = [float(v) for v in _cloud_field(cloud, "nParticle")]
        more = [[float(v) for v in _cloud_field(cloud, f)] for f in extra]
        out += [(C[c][0], C[c][1], di, ni * rho_l * math.pi / 6 * di ** 3, *e)
                for c, di, ni, *e in zip(_cloud_cells(cloud), d, n, *more)]
    return out


def parcel_cells(case, t):
    return [C[c] for C, cloud in _clouds(case, t) for c in _cloud_cells(cloud)]
