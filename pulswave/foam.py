import glob
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


def parcel_cells(case, t):
    out = []
    for part in _parts(case):
        pos = os.path.join(part, t, "lagrangian", "sprayCloud", "positions")
        if not os.path.exists(pos):
            continue
        C = _read(os.path.join(part, "0", "C"), 0)
        out += [C[int(m.group(1))] for m in re.finditer(r"\)\s+(\d+)\s+\d+\s+\d+", open(pos).read())]
    return out

