from collections import defaultdict

from .foam import ATM
from .reference import FIG3C_FRONT


def _by_row(rows, key, dx=0.2e-3):
    out = defaultdict(list)
    for r in rows:
        out[int(r[key] / dx)].append(r)
    return out


def structure(rows, heights_mm=(1, 2, 3, 4, 6, 9, 12, 15, 18, 22, 26, 30, 34, 38), x0=0.035, x1=0.14, dx=0.2e-3):
    rows_y = _by_row(rows, "y", dx)
    out = []
    for h in heights_mm:
        line = sorted((r for r in rows_y[int(h * 1e-3 / dx + 1e-6)] if x0 < r["x"] < x1), key=lambda r: r["x"])
        j = max(range(2, len(line)), key=lambda i: line[i]["p"] - line[i - 2]["p"])
        ratio = max(r["p"] for r in line[j:j + 10]) / line[max(j - 4, 0)]["p"]
        burn = next((r["x"] for r in line[j - 2:] if r["CO2"] > 0.02), None)
        gap = None if burn is None else (burn - line[j]["x"]) * 1e3
        out.append((h, line[j]["x"] * 1e3, ratio, gap))
    return out


def heights(rows, xs_mm=tuple(FIG3C_FRONT), T_hot=1900.0, dx=0.2e-3):
    cols = _by_row(rows, "x", dx)
    out = []
    for xm in xs_mm:
        col = cols[int(xm * 1e-3 / dx + 1e-6)]
        hot = [r["y"] for r in col if r["T"] > T_hot]
        shock = [r["y"] for r in col if r["p"] > 0.5 * ATM]
        out.append((xm, max(hot) * 1e3 if hot else float("nan"), max(shock) * 1e3 if shock else float("nan")))
    return out


def anchor(rows, x_jet=0.05):
    near = [r for r in rows if r["y"] < 3e-3 and 0.005 < r["x"] < x_jet - 0.005]
    burn = [r["x"] for r in rows if r["y"] < 3e-3 and r["CO2"] > 0.02]
    up = [r for r in rows if 0.02 < r["x"] < x_jet - 0.005 and r["y"] < 1e-3]
    return {
        "burn_edge_mm": min(burn) * 1e3 if burn else float("nan"),
        "upstream_T": sum(r["T"] for r in up) / len(up),
        "upstream_CO2_max": max(r["CO2"] for r in near),
        "upstream_hot_cells": sum(r["T"] > 1500 for r in near),
        "burnt_cells": sum(r["CO2"] > 0.02 for r in rows),
    }
