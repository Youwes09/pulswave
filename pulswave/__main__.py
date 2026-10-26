import argparse
import os
from dataclasses import replace

from . import build, foam, health, performance, profiles, reference, wave
from .foam import ATM


def cmd_build(a):
    s = build.PRESETS[a.preset]
    if a.J is not None:
        s = replace(s, jet_u=build.JET_U[a.J])
    for k in ("jet_u", "end", "write", "nproc"):
        if getattr(a, k) is not None:
            s = replace(s, **{k: getattr(a, k)})
    build.build(s, a.dest)


def cmd_branch(a):
    t = float(a.time)
    changes = {"end": a.end}
    if a.wall:
        changes["wall"] = a.wall
    if a.write:
        changes["write"] = a.write
    if a.no_slip:
        changes["gas_wall"] = "noSlip"
    if a.jet_u:
        changes["jet_u"] = a.jet_u
    if a.half_width:
        changes["jet_faces"] = 1
        if not (a.jet_off or a.jet_on or a.pulse):
            a.jet_on = True
    if a.jet_scale:
        changes["jet_scale"] = a.jet_scale
    if a.jet_off:
        changes["jet_windows"] = build.truncate_windows(build.load_setup(a.src).jet_windows, t) or ((0.0, t),)
    elif a.jet_on:
        changes["jet_windows"] = ((t, a.end - t),)
    elif a.pulse:
        f, duty = a.pulse
        changes["jet_windows"] = build.pulse_windows(f, duty, t, a.end)
    s = build.branch(a.src, a.dest, a.time, a.drop_jet_liquid, a.drop_wall_liquid, **changes)
    print(f"{a.dest}: restart at {t * 1e6:g} us, end {s.end * 1e6:g} us, jet windows {len(s.jet_windows) or 'continuous'}")


def cmd_ignition(a):
    build.build_ignition(a.dest, a.T, a.p, a.phi)


def cmd_wave(a):
    heights, structs = {}, {}
    for t in a.times:
        rows = foam.load(a.case, t)
        dx = foam.cell_size(rows)
        heights[t] = wave.heights(rows, dx=dx)
        structs[t] = wave.structure(rows, dx=dx)
    print("front height y [mm]: hot edge (T > 1900 K) / leading shock, paper Fig. 3c at 0.1 ms")
    print("  x mm  paper" + "".join(f"{float(t) * 1e6:>15.0f} us" for t in a.times))
    for i, xm in enumerate(reference.FIG3C_FRONT):
        print(f"  {xm:4d} {reference.FIG3C_FRONT[xm]:6.1f}" + "".join(f"   {heights[t][i][1]:5.1f} / {heights[t][i][2]:5.1f}" for t in a.times))
    print("jet front per height: shock x [mm], pressure ratio, burn gap [mm]")
    for i, (h, *_rest) in enumerate(structs[a.times[0]]):
        cells = []
        for t in a.times:
            _, x, ratio, gap = structs[t][i]
            cells.append("     -        - " if x is None else f"{x:6.1f} {ratio:5.1f}x " + (f"{gap:5.1f}" if gap is not None else "   - "))
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


def cmd_nearjet(a):
    r = wave.near_jet(foam.load(a.case, a.time), foam.parcels(a.case, a.time))
    u = r["upstream"]
    print(f"upstream near wall: T {u['T']:.0f} K  p {u['p'] / ATM:.2f} atm  ux {u['ux']:.0f} m/s  C7H16 {u['NXC7H16']:.4f}  O2 {u['O2']:.4f}")
    x0, x1 = r["layer_x_mm"]
    w = r["layer"]
    print(f"fuel-rich wall layer (y < 1 mm, C7H16 > 0.2): x {x0:.1f}-{x1:.1f} mm, T {w['T']:.0f} K, p {w['p'] / ATM:.2f} atm,"
          f" ux {w['ux']:.0f} m/s, C7H16 {w['NXC7H16']:.3f}, O2 {w['O2']:.4f}")
    if r["subsonic_x_mm"]:
        s0, s1 = r["subsonic_x_mm"]
        print(f"  subsonic part: x {s0:.1f}-{s1:.1f} mm, ux {r['subsonic_ux']:.0f} m/s")
    print(f"liquid within 30 mm of the jet, y < 3 mm: {r['liquid_near_jet_kg'] * 1e9:.0f} ug in {r['parcels_near_jet']} parcels")
    for y, x, ux in r["fronts"]:
        print(f"  y={y:2d} mm: burning from x={x:5.1f} mm, gas speed over the next 20 mm {ux:5.0f} m/s ({0.02 / ux * 1e6:4.1f} us)")


def cmd_pocket(a):
    rows = foam.load(a.case, a.time, foam.FIELDS + ("rho",))
    r = wave.pocket(rows, foam.parcels(a.case, a.time, extra=("T", "rho")), dx=foam.cell_size(rows))
    print(f"liquid at x = 49.5-80 mm, y < 3 mm: {r['liquid_kg'] * 1e9:.0f} ug in {r['parcels']} parcels, d {r['d'] * 1e6:.2f} um")
    print(f"mass-weighted: droplet T {r['T_droplet']:.0f} K, gas T {r['T_gas']:.0f} K, gas C7H16 {r['C7H16_gas']:.3f};"
          f" liquid in gas above 800 K {r['liquid_in_hot_gas'] * 100:.1f}%")
    print(f"liquid/gas mass loading {r['mass_loading']:.2f} over the region, {r['mass_loading_occupied']:.2f} over the"
          f" {r['occupied_cells']} cells holding liquid; liquid volume fraction {r['volume_fraction'] * 100:.2f}% and"
          f" {r['volume_fraction_occupied'] * 100:.2f}%")


def cmd_liquid(a):
    for t in a.times:
        m = wave.liquid_map(foam.parcels(a.case, t))
        print(f"t = {float(t) * 1e6:.0f} us: total {sum(m.values()) * 1e9:.0f} ug; per 10 mm of x [ug], bands y < 1, 1-5, > 5 mm")
        for i in sorted({i for i, _ in m}):
            print(f"  x {i * 10:3d}-{i * 10 + 10:3d} mm  " + "  ".join(f"{m[(i, b)] * 1e9:7.0f}" for b in ("y<1", "1-5", ">5")))


def cmd_performance(a):
    s = build.load_setup(a.case) if os.path.exists(os.path.join(a.case, "setup.json")) else build.PRESETS[a.preset]
    plane = [v * 1e-3 if v else None for v in (a.x, a.ymax)]
    runs = [performance.summary(foam.load(a.case, t, performance.FIELDS), s, a.duty, *plane, dx=s.dx) for t in a.times]
    r = {k: sum(x[k] for x in runs) / len(runs) for k in runs[0]}
    fuel = r["fuel_freestream"] + r["fuel_jet"]
    print(f"averaged over {len(runs)} save(s); mass flux per {build.DEPTH * 1e3:g} mm depth")
    print(f"plane x = {a.x or 'outflow'} mm, y < {a.ymax or 'top'} mm")
    print(f"mass in {r['mass_in'] * 1e3:.2f} g/s, out {r['mass_out'] * 1e3:.2f} g/s, of which shocked {r['mass_shocked'] * 1e3:.2f} g/s")
    print(f"total pressure: in {r['p0_in'] / ATM:.1f} atm, out {r['p0_out'] / ATM:.1f} atm (recovery {r['p0_out'] / r['p0_in']:.3f}),"
          f" shocked part {r['p0_shocked'] / ATM:.1f} atm (recovery {r['p0_shocked'] / r['p0_in']:.3f})")
    print(f"fuel supplied {fuel * 1e3:.3f} g/s: freestream {r['fuel_freestream'] * 1e3:.3f}, jet {r['fuel_jet'] * 1e3:.3f} (duty {a.duty:g})")
    print(f"fuel crossing the plane: burnt (CO2 + CO carbon) {r['fuel_burnt_out'] * 1e3:.3f} g/s, as vapour {r['fuel_vapour_out'] * 1e3:.3f} g/s")
    if a.by_height:
        saves = [performance.by_height(foam.load(a.case, t, performance.FIELDS), plane[0], dx=s.dx) for t in a.times]
        print("by height: y [mm], mean mass g/s, recovery (mass-weighted over all saves)")
        for lo, hi, m, q in performance.pooled_by_height(saves):
            print(f"  {lo:2d}-{hi:2d}  {m * 1e3:6.2f}  {q:.3f}")
    if a.check:
        print("plane check per save: mass g/s, reversed g/s, cells below 600 K, largest cell p0 ratio, recovery of the clean cells (share of flux)")
        for t in a.times:
            c = performance.plane_check(foam.load(a.case, t, performance.FIELDS), *plane, dx=s.dx)
            print(f"  {float(t) * 1e6:5.0f} us  {c['mass'] * 1e3:6.2f}  {c['reversed'] * 1e3:5.2f}  {c['cold_cells']:4d}"
                  f"  {c['max_cell_ratio']:6.2f}  {c['recovery_clean']:.3f} ({c['clean_share'] * 100:.0f}%)")


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
    elif a.what == "timescales":
        Y = {"NXC7H16": a.fuel, "O2": a.o2, "N2": 1 - a.fuel - a.o2}
        r = theory.timescales(a.T, a.p * ATM, Y, a.u, g)
        T2, p2 = r["postshock"]
        print(f"upstream: M {r['mach']:.2f}, ignition delay {r['tau_ign_upstream'] * 1e6:.0f} us"
              f" (transit to the jet {0.05 / a.u * 1e6:.0f} us)")
        print(f"behind a normal shock: {T2:.0f} K, {p2 / ATM:.1f} atm, ignition delay {r['tau_ign_postshock'] * 1e6:.2f} us")
    elif a.what == "thermo":
        (d_cp, at_cp), (d_h, at_h) = theory.thermo_mismatch(f"{build.TEMPLATE}/constant/speciesThermo", g=g)
        print(f"worst cp mismatch {d_cp * 100:.3f}% at {at_cp}; worst h mismatch {d_h:.3f} kJ/mol at {at_h}")


def cmd_digitize(a):
    for xm, y in reference.digitize_fig3c(a.png).items():
        print(f"x={xm:4d} mm  front y={y:5.1f} mm")


def cmd_figdata(a):
    from . import figdata

    figdata.extract(a.root, a.out, a.only, a.force, a.procs)


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

    c = sub.add_parser("branch")
    c.add_argument("src")
    c.add_argument("dest")
    c.add_argument("time")
    c.add_argument("--end", type=float, required=True)
    c.add_argument("--wall", choices=("rebound", "escape", "stick"))
    c.add_argument("--drop-jet-liquid", dest="drop_jet_liquid", action="store_true")
    c.add_argument("--drop-wall-liquid", dest="drop_wall_liquid", type=float, default=0.0, metavar="X",
                   help="remove the liquid in y < 3 mm from the jet to x = X (m) at the branch time")
    c.add_argument("--write", type=float)
    c.add_argument("--no-slip", dest="no_slip", action="store_true", help="no-slip gas wall from the branch time")
    c.add_argument("--jet-u", dest="jet_u", type=float)
    c.add_argument("--half-width", dest="half_width", action="store_true")
    c.add_argument("--jet-scale", dest="jet_scale", type=float, help="jet mass flow as a fraction of its width's, at unchanged J")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--jet-off", dest="jet_off", action="store_true")
    g.add_argument("--jet-on", dest="jet_on", action="store_true")
    g.add_argument("--pulse", type=float, nargs=2, metavar=("FREQ_HZ", "DUTY"))
    c.set_defaults(fn=cmd_branch)

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

    for name, fn in (("health", cmd_health), ("guo", cmd_guo), ("nearjet", cmd_nearjet)):
        c = sub.add_parser(name)
        c.add_argument("case")
        c.add_argument("time")
        if name == "guo":
            c.add_argument("--phi", type=float, choices=reference.GUO_LI_MM, required=True)
        c.set_defaults(fn=fn)

    c = sub.add_parser("performance")
    c.add_argument("case")
    c.add_argument("times", nargs="+")
    c.add_argument("--preset", choices=build.PRESETS, default="paper_j1")
    c.add_argument("--duty", type=float, default=1.0)
    c.add_argument("--x", type=float)
    c.add_argument("--ymax", type=float)
    c.add_argument("--by-height", dest="by_height", action="store_true", help="recovery in height bands up to 25 mm (needs --x)")
    c.add_argument("--check", action="store_true", help="per-save plane diagnostics: reversed flow, cold cells, outlier cells")
    c.set_defaults(fn=cmd_performance)

    c = sub.add_parser("pocket")
    c.add_argument("case")
    c.add_argument("time")
    c.set_defaults(fn=cmd_pocket)

    c = sub.add_parser("liquid")
    c.add_argument("case")
    c.add_argument("times", nargs="+")
    c.set_defaults(fn=cmd_liquid)

    c = sub.add_parser("theory")
    c.add_argument("what", choices=("shock", "cj", "ignition", "thermo", "timescales"))
    c.add_argument("--T", type=float, default=1134.0)
    c.add_argument("--p", type=float, default=2.75)
    c.add_argument("--u", type=float, default=2083.0)
    c.add_argument("--fuel", type=float, default=0.0926)
    c.add_argument("--o2", type=float, default=0.2087)
    c.set_defaults(fn=cmd_theory)

    c = sub.add_parser("digitize")
    c.add_argument("png")
    c.set_defaults(fn=cmd_digitize)

    c = sub.add_parser("figdata", help="extract the data behind the manuscript figures into JSON")
    c.add_argument("root", help="directory holding the cases (open_wedge_J1_paper and boxes/)")
    c.add_argument("out")
    c.add_argument("--only", nargs="+", default=(), help="case names to (re)extract")
    c.add_argument("--force", action="store_true")
    c.add_argument("--procs", type=int, default=8)
    c.set_defaults(fn=cmd_figdata)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
