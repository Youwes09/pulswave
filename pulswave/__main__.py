import argparse
from dataclasses import replace

from . import build, foam, health, profiles, reference, wave
from .foam import ATM


def cmd_build(a):
    s = build.PRESETS[a.preset]
    if a.J is not None:
        s = replace(s, jet_u=build.JET_U[a.J])
    for k in ("jet_u", "end", "write", "nproc"):
        if getattr(a, k) is not None:
            s = replace(s, **{k: getattr(a, k)})
    build.build(s, a.dest)


def cmd_ignition(a):
    build.build_ignition(a.dest, a.T, a.p, a.phi)


def cmd_wave(a):
    heights, structs = {}, {}
    for t in a.times:
        rows = foam.load(a.case, t)
        heights[t] = wave.heights(rows)
        structs[t] = wave.structure(rows)
    print("front height y [mm]: hot edge (T > 1900 K) / leading shock, paper Fig. 3c at 0.1 ms")
    print("  x mm  paper" + "".join(f"{float(t) * 1e6:>15.0f} us" for t in a.times))
    for i, xm in enumerate(reference.FIG3C_FRONT):
        print(f"  {xm:4d} {reference.FIG3C_FRONT[xm]:6.1f}" + "".join(f"   {heights[t][i][1]:5.1f} / {heights[t][i][2]:5.1f}" for t in a.times))
    print("jet front per height: shock x [mm], pressure ratio, burn gap [mm]")
    for i, (h, *_rest) in enumerate(structs[a.times[0]]):
        cells = []
        for t in a.times:
            _, x, ratio, gap = structs[t][i]
            cells.append(f"{x:6.1f} {ratio:5.1f}x " + (f"{gap:5.1f}" if gap is not None else "   - "))
        print(f"  y={h:3d}  " + "   ".join(cells))


def cmd_anchor(a):
    for t in a.times:
        r = wave.anchor(foam.load(a.case, t))
        print(f"t={float(t) * 1e6:6.1f} us  burn edge {r['burn_edge_mm']:5.1f} mm  upstream T {r['upstream_T']:5.0f} K"
              f"  CO2max {r['upstream_CO2_max']:.4f}  hot cells {r['upstream_hot_cells']:4d}  burnt cells {r['burnt_cells']}")


def cmd_profile(a):
    rows = foam.load(a.case, a.time)
    for y in a.heights:
        print(f"y = {y} mm:  x  T  p[atm]  CO2  C7H16  ux  Mach")
        for r in profiles.line(rows, y * 1e-3, a.x0 * 1e-3, a.x1 * 1e-3)[::a.step]:
            print(f"  {r['x'] * 1e3:6.1f} {r['T']:5.0f} {r['p'] / ATM:6.2f} {r['CO2']:.3f} {r['NXC7H16']:.3f} {r['ux']:6.0f} {profiles.mach(r):4.2f}")


def cmd_streamline(a):
    path = profiles.streamline(foam.load(a.case, a.time), y0=a.y0 * 1e-3)
    print("x[mm] y[mm] T p[atm] C7H16 CO2 O2")
    next_x = 0.0
    for s in path:
        if s["x"] * 1e3 >= next_x:
            print(f"{s['x'] * 1e3:6.1f} {s['y'] * 1e3:5.2f} {s['T']:5.0f} {s['p'] / ATM:6.2f} {s['NXC7H16']:.4f} {s['CO2']:.4f} {s['O2']:.4f}")
            next_x += a.every


def cmd_health(a):
    rows = foam.load(a.case, a.time)
    b = health.boundaries(rows)
    print(f"outflow min Mach {b['outflow_min_mach']:.2f}; top T {b['top_T_range'][0]:.0f}-{b['top_T_range'][1]:.0f} K,"
          f" p {b['top_p_range_atm'][0]:.3f}-{b['top_p_range_atm'][1]:.3f} atm")
    for xm, h, ang, wall in health.shock_height(rows):
        print(f"  x={xm:3d} mm: leading shock y={h:5.1f} mm ({ang:4.1f} deg)  wall T {wall['T']:5.0f} K  p {wall['p'] / ATM:5.2f} atm  CO2 {wall['CO2']:.3f}")
    print(f"droplet parcels per 1000 cells (loaded freestream {health.loaded_density():.0f}):")
    for name, v in health.droplet_density(foam.parcel_cells(a.case, a.time), rows).items():
        print(f"  {name:32s} {v:6.1f}")


def cmd_guo(a):
    from . import guo

    for k, (ours, paper) in guo.initiation(a.case, a.time, a.phi).items():
        print(f"{k:12s} ours {ours:7.1f}  paper {paper:7.1f}")


def cmd_theory(a):
    from . import theory

    g = theory.gas()
    vapor = build.premixed(1.0)
    if a.what == "shock":
        for name, Y in (("air", theory.AIR), ("vapor phi=1", vapor)):
            b, T2, p2 = theory.oblique_shock(27.0, 697.0, 2.855e4, Y, 2535.0, g)
            print(f"{name:12s} beta {b:5.2f} deg  wall angle {b - 27:5.2f} deg  T2 {T2:5.0f} K  p2 {p2 / ATM:5.2f} atm")
        for phi in (1.0, 0.2):
            b, T2, p2 = theory.oblique_shock(30.0, 298.0, 101325.0, build.premixed(phi), 2900.0, g)
            print(f"guo phi={phi}  beta {b:5.2f} deg  T2 {T2:5.0f} K (paper {reference.GUO_POSTSHOCK_T[phi]} K)")
    elif a.what == "cj":
        for T1 in (1075.0, 1200.0):
            D, pr, T2 = theory.chapman_jouguet(T1, 2.8e5, vapor, g)
            print(f"T1 {T1:.0f} K  D_CJ {D:.0f} m/s  p_CJ/p1 {pr:.1f}  T_CJ {T2:.0f} K")
    elif a.what == "ignition":
        for T in (1200.0, 1400.0, 1485.0, 1645.0, 1900.0):
            print(f"T {T:.0f} K  tau_i {theory.ignition_delay(T, 2.8e5, vapor, g=g) * 1e6:8.1f} us")
    elif a.what == "thermo":
        (d_cp, at_cp), (d_h, at_h) = theory.thermo_mismatch(f"{build.TEMPLATE}/constant/speciesThermo", g=g)
        print(f"worst cp mismatch {d_cp * 100:.3f}% at {at_cp}; worst h mismatch {d_h:.3f} kJ/mol at {at_h}")


def cmd_digitize(a):
    for xm, y in reference.digitize_fig3c(a.png).items():
        print(f"x={xm:4d} mm  front y={y:5.1f} mm")


def main():
    p = argparse.ArgumentParser(prog="pulswave")
    sub = p.add_subparsers(required=True)

    c = sub.add_parser("build")
    c.add_argument("preset", choices=build.PRESETS)
    c.add_argument("dest")
    c.add_argument("--J", type=float, choices=build.JET_U)
    c.add_argument("--jet-u", dest="jet_u", type=float)
    c.add_argument("--end", type=float)
    c.add_argument("--write", type=float)
    c.add_argument("--nproc", type=int)
    c.set_defaults(fn=cmd_build)

    c = sub.add_parser("ignition")
    c.add_argument("dest")
    c.add_argument("--T", type=float, required=True)
    c.add_argument("--p", type=float, default=2.8e5)
    c.add_argument("--phi", type=float, default=1.0)
    c.set_defaults(fn=cmd_ignition)

    for name, fn in (("wave", cmd_wave), ("anchor", cmd_anchor)):
        c = sub.add_parser(name)
        c.add_argument("case")
        c.add_argument("times", nargs="+")
        c.set_defaults(fn=fn)

    c = sub.add_parser("profile")
    c.add_argument("case")
    c.add_argument("time")
    c.add_argument("--heights", type=float, nargs="+", default=[0.1, 1.1, 2.1, 3.1])
    c.add_argument("--x0", type=float, default=18.0)
    c.add_argument("--x1", type=float, default=53.0)
    c.add_argument("--step", type=int, default=8)
    c.set_defaults(fn=cmd_profile)

    c = sub.add_parser("streamline")
    c.add_argument("case")
    c.add_argument("time")
    c.add_argument("--y0", type=float, default=1.0)
    c.add_argument("--every", type=float, default=1.0)
    c.set_defaults(fn=cmd_streamline)

    for name, fn in (("health", cmd_health), ("guo", cmd_guo)):
        c = sub.add_parser(name)
        c.add_argument("case")
        c.add_argument("time")
        if name == "guo":
            c.add_argument("--phi", type=float, choices=reference.GUO_LI_MM, required=True)
        c.set_defaults(fn=fn)

    c = sub.add_parser("theory")
    c.add_argument("what", choices=("shock", "cj", "ignition", "thermo"))
    c.set_defaults(fn=cmd_theory)

    c = sub.add_parser("digitize")
    c.add_argument("png")
    c.set_defaults(fn=cmd_digitize)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
