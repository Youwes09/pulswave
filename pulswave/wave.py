from collections import defaultdict

from .foam import ATM
from .profiles import line, mach
from .reference import FIG3C_FRONT


def _by_row(rows, key, dx=0.2e-3):
    out = defaultdict(list)
    for r in rows:
        out[int(r[key] / dx)].append(r)
    return out


def _cells(dx):
    # windows were set as cell counts on the 0.2 mm grid; keep their physical length on other grids
    return lambda k: max(1, round(k * 0.2e-3 / dx))


def structure(rows, heights_mm=(1, 2, 3, 4, 5, 6, 9, 12, 15, 18, 22, 26, 30, 34, 38), x0=0.035, x1=0.14, dx=0.2e-3, rise=1.5):
    """Per height: the first shock (pressure rising by `rise` over four cells) with burnt gas (CO + CO2 > 0.02) within five
    cells behind it, as (y mm, x mm, pressure ratio, shock-to-burnt gap mm); x is None where no reacting front is found."""
    rows_y = _by_row(rows, "y", dx)
    n = _cells(dx)
    out = []
    for h in heights_mm:
        line = sorted((r for r in rows_y[int(h * 1e-3 / dx + 1e-6)] if x0 < r["x"] < x1), key=lambda r: r["x"])
        if len(line) < 3:
            out.append((h, None, None, None))
            continue
        burnt = [r["CO2"] + r["CO"] > 0.02 for r in line]
        j = next((i for i in range(n(4), len(line))
                  if line[i]["p"] >= rise * line[i - n(4)]["p"] and any(burnt[i - n(2):i + n(5)])), None)
        if j is None:
            out.append((h, None, None, None))
            continue
        ratio = max(r["p"] for r in line[j:j + n(10)]) / line[max(j - n(4), 0)]["p"]
        b = next((k for k in range(j - n(2), len(line)) if burnt[k]), None)
        out.append((h, line[j]["x"] * 1e3, ratio, None if b is None else (line[b]["x"] - line[j]["x"]) * 1e3))
    return out


def base(front, heights_mm=(4, 5, 6)):
    """Front base: median front position over y = 4-6 mm, which wall flares at y <= 3 mm do not reach."""
    xs = sorted(x for h, x, *_ in front if h in heights_mm and x is not None)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else None


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


def near_jet(rows, parcels, x_jet=0.05):
    up = [r for r in rows if 0.02 < r["x"] < x_jet - 0.005 and r["y"] < 1e-3]
    upstream = {k: sum(r[k] for r in up) / len(up) for k in ("T", "p", "ux", "NXC7H16", "O2")}
    layer = [r for r in rows if r["x"] > x_jet - 0.0005 and r["y"] < 1e-3 and r["NXC7H16"] > 0.2]
    wake = [r for r in layer if mach(r) < 1]
    near = [p for p in parcels if x_jet - 0.0005 < p[0] < x_jet + 0.03 and p[1] < 3e-3]
    fronts = []
    for y_mm in (3, 6, 9, 12, 15):
        hot = [r for r in line(rows, y_mm * 1e-3, x_jet - 0.005, 0.1) if r["T"] > 2500]
        if hot:
            seg = [r for r in hot if r["x"] <= hot[0]["x"] + 0.02]
            fronts.append((y_mm, hot[0]["x"] * 1e3, sum(r["ux"] for r in seg) / len(seg)))
    return {
        "upstream": upstream,
        "layer_x_mm": (min(r["x"] for r in layer) * 1e3, max(r["x"] for r in layer) * 1e3),
        "layer": {k: sum(r[k] for r in layer) / len(layer) for k in ("T", "p", "ux", "NXC7H16", "O2")},
        "subsonic_x_mm": (min(r["x"] for r in wake) * 1e3, max(r["x"] for r in wake) * 1e3) if wake else None,
        "subsonic_ux": sum(r["ux"] for r in wake) / len(wake) if wake else float("nan"),
        "fronts": fronts,
        "liquid_near_jet_kg": sum(p[3] for p in near),
        "parcels_near_jet": len(near),
    }


def pocket(rows, parcels, x0=0.0495, x1=0.08, y1=3e-3, dx=0.2e-3, depth=2e-3):
    """parcels as foam.parcels(..., extra=("T", "rho"))."""
    grid = {(int(r["x"] / dx), int(r["y"] / dx)): r for r in rows}
    sel = [(m, d, Td, grid[(int(x / dx), int(y / dx))], m / rho) for x, y, d, m, Td, rho in parcels if x0 < x < x1 and y < y1]
    M = sum(s[0] for s in sel)
    V = sum(s[4] for s in sel)
    cell = dx * dx * depth
    gas = sum(r["rho"] for r in rows if x0 < r["x"] < x1 and r["y"] < y1) * cell
    occupied = {id(g): g for _, _, _, g, _ in sel}
    gas_occupied = sum(g["rho"] for g in occupied.values()) * cell

    def avg(f):
        return sum(m * f(d, Td, g) for m, d, Td, g, _ in sel) / M

    return {
        "liquid_kg": M,
        "parcels": len(sel),
        "d": avg(lambda d, Td, g: d),
        "T_droplet": avg(lambda d, Td, g: Td),
        "T_gas": avg(lambda d, Td, g: g["T"]),
        "C7H16_gas": avg(lambda d, Td, g: g["NXC7H16"]),
        "liquid_in_hot_gas": sum(m for m, _, _, g, _ in sel if g["T"] > 800) / M,
        "mass_loading": M / gas,
        "volume_fraction": V / ((x1 - x0) * y1 * depth),
        "occupied_cells": len(occupied),
        "mass_loading_occupied": M / gas_occupied,
        "volume_fraction_occupied": V / (len(occupied) * cell),
    }


def liquid_edge(parcels, x0=0.0495, x1=0.1, y1=3e-3, near=0.0525, quantiles=(0.05, 0.25, 0.5)):
    """Wall liquid behind the jet: total mass, mass within 3 mm of the jet, and the x below which each quantile lies."""
    ps = sorted((p[0], p[3]) for p in parcels if x0 < p[0] < x1 and p[1] < y1)
    total = sum(m for _, m in ps)
    xs, acc, qs = [], 0.0, list(quantiles)
    for x, m in ps:
        acc += m
        while qs and acc >= qs[0] * total:
            xs.append(x)
            qs.pop(0)
    return total, sum(m for x, m in ps if x < near), xs


def liquid_map(parcels, x_bin=0.01, x_max=0.11):
    out = defaultdict(float)
    for x, y, _, m in parcels:
        band = "y<1" if y < 1e-3 else "1-5" if y < 5e-3 else ">5"
        out[(min(int(x / x_bin), int(x_max / x_bin)), band)] += m
    return out
