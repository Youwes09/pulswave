"""Manuscript figures, plotted from the JSON that `python -m pulswave figdata` extracts from the saved fields.

Usage: python paper/figures.py [data_dir] [out_dir]    (defaults: paper/data, paper/figures)
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "figures")

# At most three coloured series per panel (colour-blind safe); the reference is ink, context is grey.
INK, GREY, LIGHT = "#0b0b0b", "#8a8986", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
WIDTH = 6.3  # inches, text width of the preprint layout

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix", "font.size": 9,
    "axes.labelsize": 9, "axes.titlesize": 9, "legend.fontsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.edgecolor": GREY, "axes.linewidth": 0.6, "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.labelcolor": INK, "axes.grid": True, "grid.color": LIGHT, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.4, "lines.markersize": 4.5,
    "legend.frameon": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.03, "savefig.dpi": 600,
    "axes.axisbelow": True, "pdf.fonttype": 42,
})


def load(kind, name):
    with open(os.path.join(DATA, kind, name + ".json")) as f:
        return json.load(f)


def base(cases, h=3):
    """Base x [mm] at height h [mm] against t [us], joined over consecutive cases."""
    out = {}
    for case in cases:
        for t, rows in load("fronts", case).items():
            out[float(t)] = next(x for hh, x, *_ in rows if hh == h)
    ts = sorted(out)
    return np.array(ts), np.array([out[t] for t in ts])


def shade(ax, windows, t1):
    """Grey bands over jet-off phases; windows are the jet-on (start, length) pairs, us."""
    edges = [w for s, d in windows for w in (s, s + d)] + [t1]
    for a, b in zip(edges[1::2], edges[2::2]):
        ax.axvspan(a, min(b, t1), color=LIGHT, lw=0, zorder=0)


def pulses(f_khz, duty, t0, t1):
    period = 1e3 / f_khz
    return [(t0 + k * period, duty * period) for k in range(int(np.ceil((t1 - t0) / period - 1e-9)))]


def label_end(ax, t, x, text, color, dy=0.0):
    ax.annotate(text, (t[-1], x[-1]), xytext=(4, dy), textcoords="offset points", va="center", fontsize=8, color=INK)
    ax.plot(t[-1], x[-1], "o", color=color, ms=3.5)


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name + ".pdf"))
    plt.close(fig)
    print(name)


def fig_validation():
    with open(os.path.join(DATA, "reference.json")) as f:
        ref = json.load(f)["fig3c_front"]
    fig, ax = plt.subplots(figsize=(WIDTH * 0.6, 2.6))
    xs = sorted(int(k) for k in ref)
    ax.errorbar(xs, [ref[str(x)] for x in xs], yerr=1.0, fmt="s", color=INK, ms=4, capsize=2, lw=0.8,
                label="Wang et al., Fig. 3(c), 100 µs")
    for case, t, color, style, text in (("open_wedge_J1_paper", "100", BLUE, "-", "Full domain, 100 µs"),
                                        ("open_wedge_J1_paper", "90", BLUE, ":", "Full domain, 90 µs"),
                                        ("box_large", "70", ORANGE, "--", "Reduced domain, 70 µs")):
        rows = load("heights", case)[t]
        ax.plot([r[0] for r in rows], [r[1] for r in rows], style, color=color, marker="o", label=text)
    ax.set_xlabel("$x$ (mm)")
    ax.set_ylabel("Front height $y$ (mm)")
    ax.legend(loc="upper left")
    save(fig, "fig_validation")


def fig_off():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.6), sharex=True)
    for ax, h in zip(axes, (3, 9)):
        ax.axvline(70, color=INK, lw=0.6, ls=":")
        for cases, color, text in ((("box_large",), INK, "Reference"),
                                   (("large_off", "large_off_long"), ORANGE, "Jet off"),
                                   (("large_off_dry",), AQUA, "Jet off, dry"),
                                   (("large_reon",), BLUE, "On again at 95 µs")):
            t, x = base(cases, h)
            ax.plot(t, x, color=color, marker="o", ms=3, label=text)
        ax.axvline(95, color=BLUE, lw=0.6, ls=":")
        ax.set_title(f"({'a' if h == 3 else 'b'}) $y$ = {h} mm", loc="left")
        ax.set_xlabel("$t$ (µs)")
        ax.set_xlim(65, 202)
        ax.set_ylim(49.5, 62.5)
    axes[0].set_ylabel("Base $x$ (mm)")
    axes[0].legend(loc="upper left")
    save(fig, "fig_off")


def fig_pulsed():
    fig, axes = plt.subplots(3, 1, figsize=(WIDTH, 5.4), sharex=True, sharey=True)
    tr, xr = base(("box_large",))
    to, xo = base(("large_off", "large_off_long"))
    to, xo = to[to <= 145], xo[to <= 145]
    for ax, (f, cases, tag) in zip(axes, ((80, ("large_f80k", "large_f80k_long"), "a"),
                                          (40, ("large_f40k",), "b"), (20, ("large_f20k",), "c"))):
        shade(ax, pulses(f, 0.5, 70, 145), 145)
        ax.plot(to, xo, color=GREY, lw=1.0, label="Jet off")
        ax.plot(tr[tr >= 70], xr[tr >= 70], color=INK, label="Reference")
        t, x = base(cases)
        ax.plot(t, x, color=BLUE, marker="o", ms=3.5, label=f"{f} kHz, $D$ = 0.5")
        ax.set_title(f"({tag}) {f} kHz, $T_\\mathrm{{off}}$ = {500 / f:g} µs", loc="left")
        ax.set_ylabel("Base $x$ (mm)")
        ax.legend(loc="upper left", ncol=3)
    axes[-1].set_xlabel("$t$ (µs)")
    axes[-1].set_xlim(68, 147)
    save(fig, "fig_pulsed")


def fig_excursion():
    pts = []  # excursion as in tab:model: largest minus smallest base x over 95-145 us
    for f, cases in ((80, ("large_f80k", "large_f80k_long")), (40, ("large_f40k",)), (20, ("large_f20k",))):
        t, x = base(cases)
        x = x[(t >= 95) & (t <= 145)]
        pts.append((500 / f, x.max() - x.min()))
    fig, ax = plt.subplots(figsize=(WIDTH * 0.6, 2.8))
    toff = np.linspace(0, 28, 50)
    ax.fill_between(toff, 0.12 * toff, 0.13 * toff, color=ORANGE, alpha=0.45, lw=0, label="$v_r T_\\mathrm{off}$, $v_r$ = 0.12–0.13 mm/µs")
    ax.axvspan(12.5, 25, color=LIGHT, lw=0, zorder=0)
    ax.text(18.75, 0.25, "$f_\\mathrm{cri}$ bracket", ha="center", fontsize=8, color="#52514e")
    ax.axvline(10, color=INK, lw=0.6, ls=":")
    ax.text(10.4, 2.3, "$\\tau$", ha="left", fontsize=9)
    ax.plot(*zip(*pts), "o", color=BLUE, ms=6, label="Simulated, $D$ = 0.5")
    for (to, dx), f in zip(pts, (80, 40, 20)):
        ax.annotate(f"{f} kHz", (to, dx), xytext=(5, -2), textcoords="offset points", fontsize=8)
    ax.set_xlabel("$T_\\mathrm{off}$ (µs)")
    ax.set_ylabel("Base excursion at $y$ = 3 mm,\n95–145 µs (mm)")
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 5.5)
    ax.legend(loc="upper left")
    save(fig, "fig_excursion")


def _perf(case, ts):
    d = load("performance", case)
    rows = [d[t] for t in ts]
    return np.mean([r["recovery"] for r in rows]), np.mean([r["burnt_fuel"] for r in rows]) * 1e3


def fig_performance():
    late, early = ["125", "130", "135", "140", "145"], ["120", "125", "130"]
    cases = (("80 kHz", "large_f80k_long", late), ("40 kHz", "large_f40k", late), ("20 kHz", "large_f20k", late),
             ("Half width", "large_narrow", late), ("Half velocity", "large_half", late), ("Jet off", "large_off", early))
    dr, db = [], []
    for _, case, ts in cases:
        r, b = _perf(case, ts)
        r0, b0 = _perf("box_large", ts)
        dr.append(r - r0)
        db.append(b - b0)
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.7), gridspec_kw={"width_ratios": (1, 1, 1.1)})
    names = [c[0] for c in cases]
    for ax, vals, noise, title in ((axes[0], dr, 0.002, "(a) Recovery,\ncase − reference"),
                                   (axes[1], db, 0.04, "(b) Burnt fuel (g/s),\ncase − reference")):
        y = np.arange(len(vals))
        ax.axvspan(-noise, noise, color=LIGHT, lw=0)
        ax.barh(y, vals, color=BLUE, height=0.6)
        ax.axvline(0, color=INK, lw=0.6)
        ax.set_yticks(y, names if ax is axes[0] else [])
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        ax.set_title(title, loc="left")
    for case, color, text in (("box_large", INK, "Reference"), ("large_half", ORANGE, "Half velocity"),
                              ("large_off", AQUA, "Jet off")):
        d = load("performance", case)
        saves = [d[t] for t in early]
        p0 = np.mean([s["p0_in"] for s in saves])
        bands = saves[0]["bands"]
        rec = [sum(s["bands"][i][3] for s in saves) / sum(s["bands"][i][2] for s in saves) / p0 for i in range(len(bands))]
        mid = [(b[0] + b[1]) / 2 for b in bands]
        axes[2].plot(rec, mid, color=color, marker="o", label=text)
    axes[2].set_xlabel("Recovery")
    axes[2].set_ylabel("$y$ (mm)")
    axes[2].set_title("(c) Recovery by height,\n120–130 µs", loc="left")
    axes[2].legend(loc="upper right")
    save(fig, "fig_performance")


def fig_equalfuel():
    fig, ax = plt.subplots(figsize=(WIDTH, 2.8))
    for cases, color, lw, text in ((("large_off", "large_off_long"), GREY, 1.0, "Jet off"),
                                   (("box_large",), INK, 1.4, "Reference (100%)"),
                                   (("large_half", "large_half_long"), ORANGE, 1.4, "Half velocity, J = 0.25"),
                                   (("large_narrow",), AQUA, 1.4, "Half width, J = 1"),
                                   (("large_f80k", "large_f80k_long"), BLUE, 1.4, "80 kHz, $D$ = 0.5")):
        t, x = base(cases)
        keep = t >= 70
        ax.plot(t[keep], x[keep], color=color, lw=lw, marker="o" if color != GREY else None, ms=3, label=text)
    ax.set_xlabel("$t$ (µs)")
    ax.set_ylabel("Base $x$ at $y$ = 3 mm (mm)")
    ax.set_xlim(68, 202)
    ax.legend(loc="upper left", ncol=2)
    save(fig, "fig_equalfuel")


def fig_grid():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.6), sharex=True)
    for ax, h in zip(axes, (3, 9)):
        for cases, t0, color, marker, text in ((("large_off",), 70, INK, "s", "Reduced domain, 0.2 mm"),
                                               (("crop_grid_off",), 50, BLUE, "o", "Crop, 0.2 mm"),
                                               (("crop_grid_fine_off",), 50, ORANGE, "^", "Crop, 0.15 mm")):
            t, x = base(cases, h)
            keep = (t >= t0) & (t <= t0 + 40)
            ax.plot(t[keep] - t0, x[keep], color=color, marker=marker, ms=4, label=text)
        ax.set_title(f"({'a' if h == 3 else 'b'}) $y$ = {h} mm", loc="left")
        ax.set_xlabel("Time after switch-off (µs)")
    axes[0].set_ylabel("Base $x$ (mm)")
    axes[0].legend(loc="upper left")
    save(fig, "fig_grid")


def _edges(case):
    d = load("edges", case)
    ts = sorted(d, key=float)
    return np.array([float(t) for t in ts]), {k: np.array([d[t][k] for t in ts]) for k in d[ts[0]]}


def fig_edge():
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH, 4.4), sharex=True, sharey="row")
    for col, (case, on, title) in enumerate((("crop_grid_off", "crop_grid", "(a) 0.5 mm jet off"),
                                             ("crop_grid_f80k_q", "crop_grid", "(b) 80 kHz, $D$ = 0.25"),
                                             ("crop_grid_d1_off", "crop_grid_d1", "(c) 1 mm jet off"))):
        t0, e0 = _edges(on)
        t, e = _edges(case)
        t, e = np.r_[t0[-1:], t], {k: np.r_[e0[k][-1:], e[k]] for k in e}
        tb, xb = base((on, case))
        keep = tb >= 50
        ax = axes[0, col]
        if "f80k" in case:
            shade(ax, pulses(80, 0.25, 0, 40), 40)
        ax.fill_between(t - 50, e["x5"] * 1e3, e["x50"] * 1e3, color=BLUE, alpha=0.18, lw=0, label="Liquid, 5–50%")
        ax.plot(t - 50, e["x25"] * 1e3, color=BLUE, ls="--", label="Liquid, 25%")
        ax.plot(tb[keep] - 50, xb[keep], color=INK, marker="o", ms=3, label="Base, $y$ = 3 mm")
        ax.set_title(title, loc="left")
        ax = axes[1, col]
        ax.plot(t - 50, e["liquid"] * 1e6, color=BLUE, marker="o", ms=3, label="In $y$ < 3 mm")
        ax.plot(t - 50, e["near_jet"] * 1e6, color=ORANGE, marker="s", ms=3, label="Within 3 mm of jet")
        ax.set_xlabel("Time after switch (µs)")
    axes[0, 0].set_ylabel("$x$ (mm)")
    axes[1, 0].set_ylabel("Liquid mass (mg)")
    axes[0, 2].legend(loc="upper right")
    fig.legend(*axes[1, 0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2)
    axes[0, 0].set_xlim(-1, 41)
    save(fig, "fig_edge")


def fig_width():
    fig, ax = plt.subplots(figsize=(WIDTH * 0.6, 2.7))
    for on, off, color, text in (("crop_grid", "crop_grid_off", ORANGE, "0.5 mm"), ("crop_grid_d1", "crop_grid_d1_off", BLUE, "1 mm")):
        tb, xb = base((on, off))
        keep = tb >= 50
        ax.plot(tb[keep] - 50, xb[keep] - xb[keep][0], color=color, marker="o", ms=3.5, label=f"{text}, base")
        t0, e0 = _edges(on)
        t, e = _edges(off)
        t, x25 = np.r_[t0[-1:], t], np.r_[e0["x25"][-1:], e["x25"]] * 1e3
        ax.plot(t - 50, x25 - x25[0], color=color, ls="--", label=f"{text}, liquid 25%")
    ax.set_xlabel("Time after switch-off (µs)")
    ax.set_ylabel("Displacement (mm)")
    ax.legend(loc="upper left")
    save(fig, "fig_width")


SEQ_T = LinearSegmentedColormap.from_list("t", ["#fcfcfb", "#f3b28f", ORANGE, "#8c2f0c", "#2b0e03"])
SEQ_F = LinearSegmentedColormap.from_list("f", ["#fcfcfb", "#9cc3ef", BLUE, "#123f78"])


def _field(case, t):
    d = load("fields", f"{case}_{t}us")
    nx, ny = d["nx"], d["ny"]
    grids = {k: np.array([np.nan if v is None else v for v in vals], float).reshape(ny, nx) for k, vals in d["fields"].items()}
    ext = (d["x0"] * 1e3, d["x0"] * 1e3 + nx * d["dx"] * 1e3, d["y0"] * 1e3, d["y0"] * 1e3 + ny * d["dx"] * 1e3)
    return grids, ext, np.array(d["droplets"]).reshape(-1, 3), d["dx"]


def _schlieren(rho, dx):
    gy, gx = np.gradient(rho, dx)
    g = np.hypot(gx, gy)
    return np.exp(-15 * g / np.nanpercentile(g, 99.5))


def _drops(ax, drops, n=6000):
    if len(drops):
        pick = drops[np.random.default_rng(0).choice(len(drops), min(n, len(drops)), replace=False)]
        ax.scatter(pick[:, 0], pick[:, 1], s=0.6, color=INK, lw=0, rasterized=True)


def fig_baseline():
    g, ext, drops, dx = _field("box_large", "70")
    fig, axes = plt.subplots(3, 1, figsize=(WIDTH, 6.2), sharex=True)
    im = dict(origin="lower", extent=ext, aspect="equal", interpolation="nearest", rasterized=True)
    axes[0].imshow(_schlieren(g["rho"], dx), cmap="Greys_r", **im)
    a = axes[1].imshow(g["T"], cmap=SEQ_T, vmin=300, vmax=3200, **im)
    axes[1].contour(g["mach"], levels=[1.0], colors=BLUE, linewidths=0.8, origin="lower", extent=ext)
    _drops(axes[1], drops)
    b = axes[2].imshow(g["fuel"], cmap=SEQ_F, vmin=0, vmax=0.6, **im)
    for ax, title, mappable, unit in ((axes[0], "(a) Numerical schlieren", None, None),
                                      (axes[1], "(b) Temperature, droplets (dots), $M$ = 1 (blue)", a, "$T$ (K)"),
                                      (axes[2], "(c) n-C$_7$H$_{16}$ vapour mass fraction", b, "$Y$")):
        ax.set_title(title, loc="left")
        ax.set_ylabel("$y$ (mm)")
        ax.grid(False)
        # the schlieren panel gets a hidden colour bar so that all three panels have the same width
        cb = fig.colorbar(mappable or ax.images[0], ax=ax, label=unit, fraction=0.025, pad=0.01)
        cb.ax.set_visible(mappable is not None)
    axes[-1].set_xlabel("$x$ (mm)")
    save(fig, "fig_baseline")


def fig_offsnap():
    fig, axes = plt.subplots(4, 1, figsize=(WIDTH, 6.6), sharex=True)
    im = None
    for ax, (t, tag) in zip(axes, (("70", "a"), ("80", "b"), ("95", "c"), ("125", "d"))):
        g, ext, drops, _ = _field("large_off", t)
        im = ax.imshow(g["T"], cmap=SEQ_T, vmin=300, vmax=3200, origin="lower", extent=ext, aspect="equal",
                       interpolation="nearest", rasterized=True)
        _drops(ax, drops)
        ax.set_title(f"({tag}) {float(t) - 70:g} µs after switch-off", loc="left")
        ax.set_ylabel("$y$ (mm)")
        ax.grid(False)
    axes[-1].set_xlabel("$x$ (mm)")
    fig.colorbar(im, ax=axes, label="$T$ (K)", fraction=0.02, pad=0.01)
    save(fig, "fig_offsnap")


def _domain(ax, w, h, color, style, text, xy, **kw):
    ax.add_patch(Rectangle((0, 0), w, h, fill=False, ec=color, ls=style, lw=1.2, **kw))
    ax.annotate(text, xy, fontsize=8, color=INK, va="bottom")


def fig_schematic():
    """Configuration in the wall-aligned frame: domains, jet, measurement plane, and the published J = 1 front."""
    with open(os.path.join(DATA, "reference.json")) as f:
        ref = sorted((float(x), y) for x, y in json.load(f)["fig3c_front"].items())
    osw = load("heights", "open_wedge_J1_paper")["100"][0]  # [x, hot, shock] at the first station behind the jet
    fig, (a, b) = plt.subplots(2, 1, figsize=(WIDTH, 6.0), gridspec_kw={"height_ratios": (124 / 274, 34 / 73)})
    for ax in (a, b):
        ax.grid(False)
        ax.set_aspect("equal")
        ax.set_xlabel("$x$ (mm)")
    # (a) whole configuration; the wedge OSW is drawn at the slope of the computed shock just behind the jet
    a.fill_between([-12, 262], -6, 0, color=LIGHT, lw=0)
    a.plot([-12, 262], [0, 0], color=INK, lw=1.0)
    _domain(a, 250, 100, GREY, "-", "Full domain, 250 × 100 mm", (249, 101.5))
    _domain(a, 120, 45, BLUE, "-", "Reduced, 120 × 45 mm", (123, 46.5))
    _domain(a, 100, 25, ORANGE, "--", "Crop, 100 × 25 mm", (103, 26))
    a.plot([0, osw[0]], [0, osw[2]], color=INK, lw=0.9, ls=":")
    near = [(x, hh) for hh, x, *_ in load("fronts", "open_wedge_J1_paper")["100"] if hh <= 9]
    a.plot(*zip(*(near + ref)), color=INK, lw=1.6)
    a.annotate("Wedge OSW", (6, 2.5), fontsize=8, rotation=10)
    a.annotate("ODW: this work to $y$ = 9 mm,\nthen Ref. Fig. 3c", (185, 74), xytext=(212, 14), fontsize=8, ha="center",
               arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    a.plot([100, 100], [0, 25], color=AQUA, lw=2.4, solid_capstyle="butt")
    for k in range(4):
        y = 30 + 18 * k
        a.annotate("", (16, y - 8.2), xytext=(0, y), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
    a.annotate("Inflow, 27° to the wall\n2535 m/s, droplets", (3, 97), fontsize=8, va="top", color=INK)
    a.annotate("Jet, $x$ = 50 mm", (44, -5), fontsize=8, va="top")
    a.plot(50, 0, marker="^", color=INK, ms=5, clip_on=False)
    a.annotate("Wedge surface, leading edge at $x$ = 0", (130, -5), fontsize=8, va="top")
    a.set_xlim(-12, 262)
    a.set_ylim(-14, 110)
    a.set_ylabel("$y$ (mm)")
    a.set_title("(a) Domains and the steady J = 1 front", loc="left")
    a.annotate("Measurement\nplane", (102, 2), fontsize=8, color=INK)
    # (b) region near the jet: base heights, jet, crop outlet and measurement plane
    b.fill_between([35, 108], -2, 0, color=LIGHT, lw=0)
    b.plot([35, 108], [0, 0], color=INK, lw=1.0)
    rows = load("fronts", "box_large")["70"]
    front = [(x, hh) for hh, x, *_ in rows if hh <= 30]
    b.plot(*zip(*front), color=INK, lw=1.6)
    for hh in (3, 9, 15):
        x = next(x for h2, x, *_ in rows if h2 == hh)
        b.plot([35, x], [hh, hh], color=GREY, lw=0.7, ls="--")
        b.plot(x, hh, "o", color=INK, ms=3.5)
        b.annotate(f"Base at $y$ = {hh} mm", (x + 1.2, hh - 0.5), fontsize=7.5, color=INK, va="top")
    b.plot([100, 100], [0, 25], color=AQUA, lw=2.4, solid_capstyle="butt")
    b.annotate("Measurement plane, $x$ = 100 mm", (101.5, 12.5), fontsize=8, rotation=90, va="center")
    b.plot([35, 100], [25, 25], color=ORANGE, lw=1.2, ls="--")
    b.annotate("0.5 mm jet", (38, -1.9), fontsize=8, va="bottom")
    b.plot(50, 0, marker="^", color=INK, ms=5, clip_on=False)
    b.annotate("Crop top, $y$ = 25 mm", (36, 25.6), fontsize=8)
    b.set_xlim(35, 110)
    b.set_ylim(-2, 32)
    b.set_ylabel("$y$ (mm)")
    b.set_title("(b) Near the jet: reduced-domain front at 70 µs, heights at which the base is tracked", loc="left")
    fig.subplots_adjust(hspace=0.32)
    save(fig, "fig_schematic")


def _mech_panel(ax, title, jet, layer, base, note=None):
    """One state of the base: wall, jet, wall liquid layer (x0, x1), detonation base at x = base."""
    ax.grid(False)
    ax.set_xlim(-1.5, 13)
    ax.set_ylim(-0.8, 6.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.fill_between([-1.5, 13], -0.8, 0, color=LIGHT, lw=0)
    ax.plot([-1.5, 13], [0, 0], color=INK, lw=1.0)
    ax.plot(0, 0, marker="^", color=INK, ms=5, clip_on=False)
    if jet:
        ax.annotate("", (0, 2.2), xytext=(0, 0.1), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.4))
        ax.annotate("Jet on", (0, 2.45), fontsize=8, color=INK, ha="center")
    else:
        ax.annotate("Jet off", (0, 2.45), fontsize=8, color=GREY, ha="center")
    for x0, x1 in layer:
        xs = np.linspace(x0, x1, 40)
        ax.fill_between(xs, 0, 0.8 * np.sin(np.pi * (xs - x0) / (x1 - x0)) ** 0.5, color=BLUE, alpha=0.55, lw=0)
    xb = base
    ax.plot([xb, xb + 3.2, xb + 7.5], [0, 3.0, 5.6], color=INK, lw=1.8)
    ax.plot(xb, 0.02, "o", color=INK, ms=4)
    ax.annotate("Base", (xb, 0), xytext=(xb + 0.35, -0.12), fontsize=7.5, va="top")
    ax.set_title(title, loc="left", fontsize=8.5)
    if note:
        ax.annotate(note, (12.8, 0.9), fontsize=7.5, ha="right", color=INK)


def fig_mechanism():
    """The base follows the upstream end of the wall liquid layer (cartoon; measured values in the labels)."""
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 3.6))
    _mech_panel(axes[0, 0], "(a) Jet on: liquid layer at the jet,\nbase at the jet", True, [(0.3, 4.0)], 0.0)
    axes[0, 0].annotate("Wall liquid", (2.2, 0.6), xytext=(4.6, 1.3), fontsize=7.5,
                        arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    _mech_panel(axes[0, 1], "(b) Off, $t < \\tau \\approx$ 10 µs: layer still\nat the jet, base held", False,
                [(0.3, 4.0)], 0.0)
    _mech_panel(axes[1, 0], "(c) Off, $t > \\tau$: layer slides downstream,\nbase follows its upstream end", False,
                [(2.8, 6.8)], 2.4, note="$v_r \\approx$ 0.12 mm/µs")
    ax = axes[1, 0]
    ax.annotate("", (2.4, 0.9), xytext=(0.2, 0.9), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.2))
    _mech_panel(axes[1, 1], "(d) Back on: liquid at the jet within 5 µs,\nbase keeps retreating 10–20 µs or more", True,
                [(0.3, 2.2), (2.8, 6.8)], 2.4)
    ax = axes[1, 1]
    ax.annotate("", (0.4, 0.9), xytext=(2.3, 0.9), arrowprops=dict(arrowstyle="-|>", color=AQUA, lw=1.2))
    fig.subplots_adjust(wspace=0.05, hspace=0.35)
    save(fig, "fig_mechanism")


FIGURES = (fig_schematic, fig_mechanism, fig_validation, fig_off, fig_pulsed, fig_excursion, fig_performance, fig_equalfuel, fig_grid, fig_edge,
           fig_width, fig_baseline, fig_offsnap)

if __name__ == "__main__":
    for fn in FIGURES:
        fn()
