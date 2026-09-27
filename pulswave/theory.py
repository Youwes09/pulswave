import math
import os
import re

import cantera as ct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MECH = os.path.join(ROOT, "mechanisms", "nHeptane.yaml")
AIR = {"O2": 0.233, "N2": 0.767}


def gas():
    return ct.Solution(MECH)


def normal_shock(g, T1, p1, Y, un):
    g.TPY = T1, p1, Y
    r1, h1 = g.density, g.enthalpy_mass
    r2 = 5 * r1
    for _ in range(200):
        u2 = r1 * un / r2
        p2 = p1 + r1 * un ** 2 - r2 * u2 ** 2
        g.HPY = h1 + 0.5 * (un ** 2 - u2 ** 2), p2, Y
        r2 = 0.5 * (r2 + g.density)
    return g.T, p2, r1 / r2


def oblique_shock(theta, T1, p1, Y, u1, g=None):
    g = g or gas()
    lo, hi = math.radians(theta) + 1e-3, math.radians(89)
    for _ in range(60):
        b = 0.5 * (lo + hi)
        un, ut = u1 * math.sin(b), u1 * math.cos(b)
        T2, p2, eps = normal_shock(g, T1, p1, Y, un)
        lo, hi = (b, hi) if math.degrees(b - math.atan(eps * un / ut)) < theta else (lo, b)
    return math.degrees(b), T2, p2


def chapman_jouguet(T1, p1, Y, g=None):
    g = g or gas()
    g.TPY = T1, p1, Y
    h1, v1 = g.enthalpy_mass, 1 / g.density
    best = None
    for i in range(1, 60):
        v2 = v1 * (0.30 + 0.01 * i)
        lo, hi = 1000.0, 5000.0
        for _ in range(50):
            T2 = 0.5 * (lo + hi)
            g.TDY = T2, 1 / v2, Y
            g.equilibrate("TV")
            f = g.enthalpy_mass - h1 - 0.5 * (g.P - p1) * (v1 + v2)
            lo, hi = (T2, hi) if f < 0 else (lo, T2)
        if g.P > p1:
            D = v1 * math.sqrt((g.P - p1) / (v1 - v2))
            if best is None or D < best[0]:
                best = (D, g.P / p1, T2)
    return best


def ignition_delay(T, p, Y, t_max=5e-3, g=None):
    g = g or gas()
    g.TPY = T, p, Y
    r = ct.IdealGasConstPressureReactor(g)
    net = ct.ReactorNet([r])
    t, q_max, t_max_q = 0.0, 0.0, None
    while t < t_max and r.T < T + 1500:
        t = net.step()
        q = -sum(r.thermo.net_production_rates * r.thermo.partial_molar_enthalpies)
        if q > q_max:
            q_max, t_max_q = q, t
    return t_max_q


def thermo_mismatch(species_thermo, temps=(300.0, 700.0, 1000.0, 1500.0, 2500.0), g=None):
    g = g or gas()
    txt = open(species_thermo).read()
    worst_cp = worst_h = (0.0, ("", 0.0))
    for name, body in re.findall(r"^(\w+)\s*\{(.*?)^\}", txt, re.S | re.M):
        coeffs = {k: [float(v) for v in re.search(k + r"\s*\(([^)]*)\)", body).group(1).split()] for k in ("highCpCoeffs", "lowCpCoeffs")}
        t_common = float(re.search(r"Tcommon\s+([0-9.eE+-]+);", body).group(1))
        sp = g.species(name)
        for T in temps:
            c = coeffs["highCpCoeffs" if T > t_common else "lowCpCoeffs"]
            cp = c[0] + c[1] * T + c[2] * T ** 2 + c[3] * T ** 3 + c[4] * T ** 4
            h = c[0] + c[1] * T / 2 + c[2] * T ** 2 / 3 + c[3] * T ** 3 / 4 + c[4] * T ** 4 / 5 + c[5] / T
            d_cp = abs(cp - sp.thermo.cp(T) / ct.gas_constant) / (sp.thermo.cp(T) / ct.gas_constant)
            d_h = abs(h - sp.thermo.h(T) / (ct.gas_constant * T)) * T * 8.314e-3
            worst_cp = max(worst_cp, (d_cp, (name, T)))
            worst_h = max(worst_h, (d_h, (name, T)))
    return worst_cp, worst_h
