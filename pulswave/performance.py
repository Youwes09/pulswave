import math
import os
import re

from .build import DEPTH, TEMPLATE, fuel_rate

THERMO_FILE = os.path.join(TEMPLATE, "constant", "speciesThermo")
SPECIES = tuple(re.search(r"species\s+\d+\s*\(([^)]*)\)", open(THERMO_FILE).read()).group(1).split())
FIELDS = ("T", "p", "U", "rho") + SPECIES
RU = 8314.46
FUEL_PER_C = 100.204 / 7


def _number(block, key):
    return float(re.search(rf"{key}\s+([\d.eE+-]+)", block).group(1))


def _list(block, key):
    return [float(v) for v in re.search(rf"{key}\s+\(([^)]*)\)", block).group(1).split()]


def _janaf(species=SPECIES):
    txt = open(THERMO_FILE).read()
    out = {}
    for s in species:
        block = re.search(rf"\n{s}\s*\n\{{(.*?)\n\}}", txt, re.S).group(1)
        out[s] = (_number(block, "molWeight"), _number(block, "Tcommon"), _list(block, "highCpCoeffs"), _list(block, "lowCpCoeffs"))
    return out


THERMO = _janaf()


def _coeffs(s, T):
    _, tc, high, low = THERMO[s]
    return high if T > tc else low


def _h(s, T):
    a = _coeffs(s, T)
    return (a[0] + a[1] * T / 2 + a[2] * T ** 2 / 3 + a[3] * T ** 3 / 4 + a[4] * T ** 4 / 5 + a[5] / T) * T


def _cp(s, T):
    a = _coeffs(s, T)
    return a[0] + a[1] * T + a[2] * T ** 2 + a[3] * T ** 3 + a[4] * T ** 4


def _s(s, T):
    a = _coeffs(s, T)
    return a[0] * math.log(T) + a[1] * T + a[2] * T ** 2 / 2 + a[3] * T ** 3 / 3 + a[4] * T ** 4 / 4 + a[6]


def _moles(r):
    return {s: r[s] / THERMO[s][0] for s in SPECIES if r[s] > 0}


def _mix(moles, f, T):
    return sum(v * f(s, T) for s, v in moles.items())


def total_pressure(r):
    n = _moles(r)
    total = sum(n.values())
    T = r["T"]
    h0 = _mix(n, _h, T) * RU + 0.5 * (r["ux"] ** 2 + r["uy"] ** 2)
    T0 = T
    for _ in range(30):
        step = (h0 - _mix(n, _h, T0) * RU) / (_mix(n, _cp, T0) * RU)
        T0 += step
        if abs(step) < 1e-3:
            break
    return r["p"] * math.exp((_mix(n, _s, T0) - _mix(n, _s, T)) / total)


def _boundary(rows, dx, plane_x=None, y_max=None):
    x0 = min(r["x"] for r in rows)
    x1 = max(r["x"] for r in rows) if plane_x is None else (math.floor(plane_x / dx) + 0.5) * dx
    y1 = max(r["y"] for r in rows)
    y_max = y1 if y_max is None else y_max
    inflow = [(r, r["rho"] * r["ux"] * dx * DEPTH) for r in rows if r["x"] < x0 + 0.5 * dx]
    p_inf = sum(r["p"] for r, _ in inflow) / len(inflow)
    # once the upper front reaches the top boundary, its shocked cells there are not freestream inflow
    top = [(r, -r["rho"] * r["uy"] * dx * DEPTH) for r in rows if r["y"] > y1 - 0.5 * dx and r["uy"] < 0 and r["p"] < 1.5 * p_inf]
    outflow = [(r, r["rho"] * r["ux"] * dx * DEPTH) for r in rows if abs(r["x"] - x1) < 0.5 * dx and r["y"] < y_max]
    return inflow + top, outflow


def _weighted(cells, f):
    m = sum(w for _, w in cells)
    return sum(f(r) * w for r, w in cells) / m, m


def burnt_fuel(r):
    return (r["CO2"] / 44.01 + r["CO"] / 28.01) * FUEL_PER_C


def summary(rows, s, jet_duty=1.0, plane_x=None, y_max=None, dx=0.2e-3):
    inflow, outflow = _boundary(rows, dx, plane_x, y_max)
    p_ref = sum(r["p"] for r, _ in inflow) / len(inflow)
    shocked = [(r, w) for r, w in outflow if r["p"] > 1.5 * p_ref]
    p0_in, m_in = _weighted(inflow, total_pressure)
    p0_out, m_out = _weighted(outflow, total_pressure)
    p0_shocked, m_shocked = _weighted(shocked, total_pressure) if shocked else (float("nan"), 0.0)
    ux, uy = s.U
    freestream = fuel_rate(s, ux, s.ly) + fuel_rate(s, -uy, s.lx) if s.spray else 0.0
    return {
        "p0_in": p0_in,
        "p0_out": p0_out,
        "p0_shocked": p0_shocked,
        "mass_in": m_in,
        "mass_out": m_out,
        "mass_shocked": m_shocked,
        "fuel_freestream": freestream,
        "fuel_jet": s.jet_rate * jet_duty,
        "fuel_burnt_out": sum(burnt_fuel(r) * w for r, w in outflow),
        "fuel_vapour_out": sum(r["NXC7H16"] * w for r, w in outflow),
    }


BANDS = ((0, 3), (3, 6), (6, 10), (10, 15), (15, 20), (20, 25))


def by_height(rows, plane_x, bands=BANDS, dx=0.2e-3):
    inflow, plane = _boundary(rows, dx, plane_x, bands[-1][1] * 1e-3)
    p0_in = _weighted(inflow, total_pressure)[0]
    out = []
    for lo, hi in bands:
        cells = [(r, w) for r, w in plane if lo <= r["y"] * 1e3 < hi]
        out.append((lo, hi, sum(w for _, w in cells), sum(total_pressure(r) * w for r, w in cells)))
    return p0_in, out


def pooled_by_height(saves):
    p0_in = sum(p for p, _ in saves) / len(saves)
    out = []
    for i, (lo, hi, _, _) in enumerate(saves[0][1]):
        m = sum(b[i][2] for _, b in saves)
        out.append((lo, hi, m / len(saves), sum(b[i][3] for _, b in saves) / m / p0_in))
    return out


def plane_check(rows, plane_x, y_max, dx=0.2e-3):
    inflow, plane = _boundary(rows, dx, plane_x, y_max)
    p0_in = _weighted(inflow, total_pressure)[0]
    cells = [(r, w, total_pressure(r) / p0_in) for r, w in plane]
    clean = [(w, q) for r, w, q in cells if w > 0 and q < 0.5]
    return {
        "mass": sum(w for _, w, _ in cells),
        "reversed": sum(-w for _, w, _ in cells if w < 0),
        "cold_cells": sum(r["T"] < 600 for r, _, _ in cells),
        "max_cell_ratio": max(q for _, _, q in cells),
        "recovery_clean": sum(w * q for w, q in clean) / sum(w for w, _ in clean),
        "clean_share": sum(w for w, _ in clean) / sum(abs(w) for _, w, _ in cells),
    }
