import math

from .build import PRESETS, fuel_rate, parcel_mass
from .foam import ATM
from .profiles import sound

BOXES = {
    "freestream ahead of jet front": (40, 55, 9, 15),
    "freestream high": (20, 60, 30, 60),
    "freestream far": (150, 240, 60, 95),
    "near wall upstream of jet": (20, 45, 0, 3),
}


def boundaries(rows, s=PRESETS["paper_j1"]):
    out_col = [r for r in rows if r["x"] > s.lx - s.dx]
    top = [r for r in rows if r["y"] > s.ly - s.dx]
    return {
        "outflow_min_mach": min(r["ux"] / sound(r["T"]) for r in out_col),
        "top_T_range": (min(r["T"] for r in top), max(r["T"] for r in top)),
        "top_p_range_atm": (min(r["p"] for r in top) / ATM, max(r["p"] for r in top) / ATM),
    }


def shock_height(rows, xs_mm=(20, 40, 80, 120, 160, 200, 240), dx=0.2e-3):
    out = []
    for xm in xs_mm:
        col = sorted((r for r in rows if int(r["x"] / dx) == int(xm * 1e-3 / dx + 1e-6)), key=lambda r: -r["y"])
        s = next((r for r in col if r["p"] > 0.5 * ATM), None)
        h = s["y"] * 1e3 if s else float("nan")
        out.append((xm, h, math.degrees(math.atan(h / xm)), col[-1]))
    return out


def droplet_density(cells, rows, boxes=BOXES):
    def inside(c, b):
        return b[0] <= c[0] * 1e3 < b[1] and b[2] <= c[1] * 1e3 < b[3]

    out = {}
    for name, b in boxes.items():
        n_cells = sum(inside((r["x"], r["y"]), b) for r in rows)
        out[name] = 1e3 * sum(inside(c, b) for c in cells) / max(n_cells, 1)
    return out


def loaded_density(s=PRESETS["paper_j1"]):
    ux, _ = s.U
    pps = fuel_rate(s, ux, s.ly) / parcel_mass()
    return 1e3 * pps / (s.ly * ux) * s.dx ** 2
