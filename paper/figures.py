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


def front(*names):
    """Front per height against t [us], joined over a chain of segments; "old:" segments are in fronts/, the rest in campaign/front/."""
    out = {}
    for n in names:
        if n.startswith("old:"):
            out.update({float(t): rows for t, rows in load("fronts", n[4:]).items()})
        else:
            out.update({float(t) * 1e6: v["front"] for t, v in load("campaign/front", n)["saves"].items()})
    return {t: {h: x for h, x, *_ in out[t]} for t in sorted(out)}


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else np.nan


def base(*names, h=None):
    """Base x [mm] against t [us]: the median of the front at y = 4, 5 and 6 mm, or the front at height h."""
    fr = front(*names)
    ts = np.array(list(fr))
    return ts, np.array([_median([f.get(k) for k in (4, 5, 6)]) if h is None else (f.get(h) or np.nan) for f in fr.values()])


# case chains, as in scripts/analysis/claims.py
REF = ("old:box_large", "box_large_200")
OFF = ("old:large_off", "old:large_off_long")
CROP_OFF = ("old:crop_grid", "old:crop_grid_off")
F80 = ("old:large_f80k", "old:large_f80k_long", "large_f80k_200")
F40 = ("old:large_f40k", "large_f40k_200")
F30 = ("large_f30k", "large_f30k_200")
F20 = ("old:large_f20k", "large_f20k_200")


def shade(ax, windows, t1):
    """Grey bands over jet-off phases; windows are the jet-on (start, length) pairs, us."""
    edges = [w for s, d in windows for w in (s, s + d)] + [t1]
    for a, b in zip(edges[1::2], edges[2::2]):
        if a < t1:
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
                label="Wang et al., Fig. 3(c), digitized")
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
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.7))
    ax = axes[0]
    for cases, color, marker, text in ((REF, INK, None, "Reference"), (OFF, GREY, "o", "Jet off"),
                                       (("old:large_off_dry",), AQUA, "^", "Jet off, dry"), (("old:large_reon",), BLUE, "s", "On again at 95 µs")):
        t, x = base(*cases)
        keep = t >= 70
        ax.plot(t[keep], x[keep], color=color, marker=marker, ms=2.5, label=text)
    for t0, color in ((70, INK), (95, BLUE)):
        ax.axvline(t0, color=color, lw=0.6, ls=":")
    ax.set_title("(a) Base after switch-off at 70 µs", loc="left")
    ax.set_xlabel("$t$ (µs)")
    ax.set_ylabel("Base $x$ (mm)")
    ax.set_xlim(65, 202)
    ax.legend(loc="upper left")
    ax = axes[1]
    for cases, cut, color, style, marker, text in ((OFF, 70, GREY, "-", "o", "Reduced, off at 70 µs"),
                                                   (("large_off_hr",), 165, GREY, "--", None, "Reduced, off at 165 µs"),
                                                   (("crop_off_hr",), 50, BLUE, "-", None, "Crop, off at 50 µs"),
                                                   (("old:large_off_dry",), 70, AQUA, "-", "^", "Reduced, dry"),
                                                   (("crop_off_cut",), 50, AQUA, "--", "s", "Crop, plug removed")):
        t, x = base(*cases)
        keep = (t >= cut) & (t <= cut + 40)
        ax.plot(t[keep] - cut, x[keep] - x[keep][0], color=color, ls=style, marker=marker, ms=3, label=text)
    ax.axhline(0.3, color=GREY, lw=0.6, ls=":")
    ax.set_title("(b) Displacement since switch-off", loc="left")
    ax.set_xlabel("Time after switch-off (µs)")
    ax.set_ylabel("Base displacement (mm)")
    ax.set_xlim(0, 40)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, fontsize=7)
    save(fig, "fig_off")


def fig_duty():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.7), sharey=True)
    tc, xc = base("crop_grid")
    to, xo = base(*CROP_OFF)
    for ax, title, series in ((axes[0], "(a) $T_\\mathrm{off}$ = 6.25 µs", (("crop_f80k", BLUE, "o", "$D$ = 0.5, 80 kHz"),
                                                                         ("crop_d375_100k", AQUA, "^", "$D$ = 0.375, 100 kHz"),
                                                                         ("crop_d25_120k", ORANGE, "s", "$D$ = 0.25, 120 kHz"))),
                              (axes[1], "(b) $D$ = 0.25", (("crop_f160k_q", BLUE, "D", "$T_\\mathrm{off}$ = 4.7 µs, 160 kHz"),
                                                           ("crop_d25_120k", ORANGE, "s", "$T_\\mathrm{off}$ = 6.25 µs, 120 kHz"),
                                                           ("old:crop_grid_f80k_q", AQUA, "v", "$T_\\mathrm{off}$ = 9.4 µs, 80 kHz")))):
        ax.plot(tc[(tc >= 40) & (tc <= 50)], xc[(tc >= 40) & (tc <= 50)], color=INK, label="Continuous, to 50 µs")
        ax.plot(to[to >= 50], xo[to >= 50], color=GREY, lw=1.0, label="Jet off")
        for name, color, marker, text in series:
            t, x = base(name)
            keep = (t >= 50) & (t <= 90)
            ax.plot(t[keep], x[keep], color=color, marker=marker, ms=2.5, label=text)
        ax.set_title(title, loc="left")
        ax.set_xlabel("$t$ (µs)")
        ax.set_xlim(40, 91)
        ax.legend(loc="upper left", fontsize=7)
    axes[0].set_ylabel("Base $x$ (mm)")
    save(fig, "fig_duty")


def fig_pulsed():
    fig, axes = plt.subplots(4, 1, figsize=(WIDTH, 7.0), sharex=True, sharey=True)
    tr, xr = base(*REF)
    to, xo = base(*OFF)
    for ax, (f, cases, tag) in zip(axes, ((80, F80, "a"), (40, F40, "b"), (30, F30, "c"), (20, F20, "d"))):
        shade(ax, pulses(f, 0.5, 70, 200), 200)
        ax.plot(to[to >= 70], xo[to >= 70], color=GREY, lw=1.0, label="Jet off")
        ax.plot(tr[tr >= 70], xr[tr >= 70], color=INK, label="Reference")
        t, x = base(*cases)
        keep = t >= 70
        ax.plot(t[keep], x[keep], color=BLUE, marker="o", ms=2.5, label=f"{f} kHz, $D$ = 0.5")
        ax.set_title(f"({tag}) {f} kHz, $T_\\mathrm{{off}}$ = {500 / f:.3g} µs", loc="left")
        ax.set_ylabel("Base $x$ (mm)")
    axes[0].legend(loc="upper left", ncol=3)
    axes[-1].set_xlabel("$t$ (µs)")
    axes[-1].set_xlim(68, 202)
    save(fig, "fig_pulsed")


def _late_perf(case):
    d = load("campaign/performance", case)
    return {t: v for t, v in d.items() if v["check"]["clean_share"] >= 0.95}


def _bands():
    """Burnt and vapour fuel per height band over 150-200 us, from plane_bands_150_200.txt."""
    out, case = {}, None
    with open(os.path.join(DATA, "campaign", "plane_bands_150_200.txt")) as f:
        for line in f:
            w = line.split()
            if not w:
                continue
            if "saves;" in line:
                case = w[0]
                out[case] = []
            elif "-" in w[0] and case:
                lo, hi = (float(v) for v in w[0].split("-"))
                out[case].append((lo, hi, float(w[1]), float(w[2])))
    return out


def fig_performance():
    ref = _late_perf("box_large_200")
    cases = (("80 kHz", "large_f80k_200"), ("80 kHz, restarted", "large_f80k_rep"), ("40 kHz", "large_f40k_200"),
             ("30 kHz", "large_f30k_200"), ("20 kHz", "large_f20k_200"), ("Half width, cone (lost)", "large_narrow_long"),
             ("Half width, patch", "large_narrow_patch"), ("Half velocity (lost)", "large_half_long"))
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.9), gridspec_kw={"width_ratios": (1, 1, 1.1)})
    for ax, key, scale, title in ((axes[0], "recovery", 1, "(a) Recovery,\ncase − reference"),
                                  (axes[1], "burnt_fuel", 1e3, "(b) Burnt fuel (g/s),\ncase − reference")):
        for i, (_, case) in enumerate(cases):
            r = _late_perf(case)
            d = [(r[t][key] - ref[t][key]) * scale for t in r if t in ref]
            ax.plot(d, [i] * len(d), "o", color=GREY, ms=2.5, alpha=0.7)
            ax.plot(np.mean(d), i, "D", color=BLUE, ms=5)
        ax.axvline(0, color=INK, lw=0.6)
        ax.set_yticks(range(len(cases)), [c[0] for c in cases] if ax is axes[0] else [])
        ax.set_ylim(len(cases) - 0.5, -0.5)
        ax.grid(axis="y", visible=False)
        ax.set_title(title, loc="left")
    for case, color, style, text in (("box_large_200", INK, "-", "Reference"), ("large_f80k_200", BLUE, "-", "80 kHz"),
                                     ("large_narrow_patch", AQUA, "--", "Half width, patch"), ("large_half_long", ORANGE, ":", "Half velocity")):
        rows = _bands()[case]
        rows = rows[:max(i for i, r in enumerate(rows) if r[3] > 0) + 1]
        axes[2].plot([v / (hi - lo) for lo, hi, _, v in rows for _ in (0, 1)], [y for lo, hi, *_ in rows for y in (lo, hi)],
                     color=color, ls=style, label=text)
    axes[2].set_ylim(0, 8)
    axes[2].set_xlabel("Vapour (g/s per mm of $y$)")
    axes[2].set_ylabel("$y$ (mm)")
    axes[2].set_title("(c) Unburnt vapour by height", loc="left")
    axes[2].legend(loc="upper right", fontsize=7)
    save(fig, "fig_performance")


def fig_equalfuel():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0))
    for cases, color, style, text in ((OFF, GREY, "-", "Jet off"), (REF, INK, "-", "Reference"),
                                      (("old:large_half", "old:large_half_long"), ORANGE, "-", "Half velocity, $J$ = 0.25"),
                                      (("large_narrow_patch",), AQUA, "-", "Half width, $J$ = 1, patch"),
                                      (("old:large_narrow", "large_narrow_long"), AQUA, "--", "Half width, $J$ = 1, cone"),
                                      (F80, BLUE, "-", "80 kHz, $D$ = 0.5")):
        t, x = base(*cases)
        keep = t >= 70
        marker = {ORANGE: "s", BLUE: "o"}.get(color, "^" if style == "-" else "v")
        ax.plot(t[keep], x[keep], color=color, ls=style, lw=1.0 if color == GREY else 1.4,
                marker=None if color in (GREY, INK) else marker, ms=2.5, label=text)
    ax.set_xlabel("$t$ (µs)")
    ax.set_ylabel("Base $x$ (mm)")
    ax.set_xlim(68, 202)
    ax.legend(loc="upper left", ncol=2)
    save(fig, "fig_equalfuel")


def fig_grid():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.6), sharex=True)
    for ax, h, title in ((axes[0], None, "(a) Base"), (axes[1], 9, "(b) $y$ = 9 mm")):
        for cases, t0, color, marker, text in ((("old:large_off",), 70, INK, "s", "Reduced domain, 0.2 mm"),
                                               (("old:crop_grid_off",), 50, BLUE, "o", "Crop, 0.2 mm"),
                                               (("old:crop_grid_fine_off",), 50, ORANGE, "^", "Crop, 0.15 mm"),
                                               (("crop_fine_off",), 50, AQUA, None, "Crop, 0.1 mm")):
            t, x = base(*cases, h=h)
            keep = (t >= t0) & (t <= t0 + 40)
            ax.plot(t[keep] - t0, x[keep], color=color, marker=marker, ms=3.5, label=text)
        ax.set_title(title, loc="left")
        ax.set_xlabel("Time after switch-off (µs)")
    axes[0].set_ylabel("Base $x$ (mm)")
    axes[1].set_ylabel("Front $x$ (mm)")
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
        tb, xb = base("old:" + on, "old:" + case)
        keep = tb >= 50
        ax = axes[0, col]
        if "f80k" in case:
            for a in axes[:, col]:
                shade(a, pulses(80, 0.25, 0, 40), 40)
        ax.fill_between(t - 50, e["x5"] * 1e3, e["x50"] * 1e3, color=BLUE, alpha=0.18, lw=0, label="Liquid, 5–50%")
        ax.plot(t - 50, e["x25"] * 1e3, color=BLUE, ls="--", label="Liquid, 25%")
        ax.plot(tb[keep] - 50, xb[keep], color=INK, marker="o", ms=3, label="Base")
        ax.set_title(title, loc="left")
        ax = axes[1, col]
        ax.plot(t - 50, e["liquid"] * 1e6, color=BLUE, marker="o", ms=3, label="Wall layer")
        ax.plot(t - 50, e["near_jet"] * 1e6, color=ORANGE, marker="s", ms=3, label="Plug")
        ax.set_xlabel("Time after switch (µs)")
    axes[0, 0].set_ylabel("$x$ (mm)")
    axes[1, 0].set_ylabel("Liquid mass (mg)")
    axes[0, 2].legend(loc="upper right")
    fig.legend(*axes[1, 0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2)
    axes[0, 0].set_xlim(-1, 41)
    save(fig, "fig_edge")


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
                                      (axes[2], "(c) n-C$_7$H$_{16}$ vapour mass fraction", b, "$Y_\\mathrm{C_7H_{16}}$")):
        ax.set_title(title, loc="left")
        ax.set_ylabel("$y$ (mm)")
        ax.grid(False)
        # the schlieren panel gets a hidden colour bar so that all three panels have the same width
        cb = fig.colorbar(mappable or ax.images[0], ax=ax, label=unit, fraction=0.025, pad=0.01, extend="max" if mappable else "neither")
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
    fig.colorbar(im, ax=axes, label="$T$ (K)", fraction=0.02, pad=0.01, extend="max")
    save(fig, "fig_offsnap")


def _domain(ax, w, h, color, style, text, xy, **kw):
    ax.add_patch(Rectangle((0, 0), w, h, fill=False, ec=color, ls=style, lw=1.2, **kw))
    ax.annotate(text, xy, fontsize=8, color=INK, va="bottom")


def fig_schematic():
    """Configuration in the wall-aligned frame: domains, jet, measurement plane, and the published J = 1 front."""
    with open(os.path.join(DATA, "reference.json")) as f:
        ref = sorted((float(x), y) for x, y in json.load(f)["fig3c_front"].items())
    fig, (a, b) = plt.subplots(2, 1, figsize=(WIDTH, 6.0), gridspec_kw={"height_ratios": (124 / 274, 34 / 73)})
    for ax in (a, b):
        ax.grid(False)
        ax.set_aspect("equal")
        ax.set_xlabel("$x$ (mm)")
    # (a) whole configuration
    a.fill_between([-12, 262], -6, 0, color=LIGHT, lw=0)
    a.plot([-12, 262], [0, 0], color=INK, lw=1.0)
    _domain(a, 250, 100, GREY, "-", "Full domain, 250 × 100 mm", (160, 101.5))
    _domain(a, 120, 45, BLUE, "-", "Reduced, 120 × 45 mm", (123, 46.5))
    _domain(a, 100, 25, ORANGE, "--", "Crop, 100 × 25 mm", (103, 26))
    near = [(x, hh) for hh, x, *_ in load("fronts", "open_wedge_J1_paper")["100"] if hh <= 9]
    a.plot(*zip(*near), color=INK, lw=1.6)
    a.plot(*zip(*([near[-1]] + ref)), color=INK, lw=1.2, ls="--")
    a.annotate("ODW: computed to $y$ = 9 mm (solid),\nRef. Fig. 3(c) above (dashed)", (185, 74), xytext=(212, 14), fontsize=8, ha="center",
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
    a.set_title("(a) Domains and the $J$ = 1 front", loc="left")
    a.annotate("Measurement\nplane", (102, 2), fontsize=8, color=INK)
    # (b) region near the jet: base heights, jet, crop outlet and measurement plane
    b.fill_between([35, 108], -2, 0, color=LIGHT, lw=0)
    b.plot([35, 108], [0, 0], color=INK, lw=1.0)
    rows = load("fronts", "box_large")["70"]
    front = [(x, hh) for hh, x, *_ in rows if hh <= 30]
    b.plot(*zip(*front), color=INK, lw=1.6)
    xs = [next(x for h2, x, *_ in rows if h2 == hh) for hh in (4, 5, 6)]
    b.fill_between([35, 108], 4, 6, color=BLUE, alpha=0.12, lw=0)
    b.plot(xs, (4, 5, 6), "o", color=INK, ms=3.5)
    b.annotate("Base: median of the front at $y$ = 4–6 mm", (max(xs) + 1.2, 6.6), fontsize=7.5, color=INK, va="bottom")
    b.plot([100, 100], [0, 25], color=AQUA, lw=2.4, solid_capstyle="butt")
    b.annotate("Measurement plane, $x$ = 100 mm", (101.5, 12.5), fontsize=8, rotation=90, va="center")
    b.plot([35, 100], [25, 25], color=ORANGE, lw=1.2, ls="--")
    b.annotate("0.5 mm jet", (38, -1.9), fontsize=8, va="bottom")
    b.plot(50, 0, marker="^", color=INK, ms=5, clip_on=False)
    b.annotate("Crop top, $y$ = 25 mm", (36, 25.6), fontsize=8)
    b.set_xlim(35, 110)
    b.set_ylim(-2, 28)
    b.set_ylabel("$y$ (mm)")
    b.set_title("(b) Near the jet: reduced-domain front at 70 µs and the heights that define the base", loc="left")
    fig.subplots_adjust(hspace=0.32)
    save(fig, "fig_schematic")


FIGURES = (fig_schematic, fig_validation, fig_grid, fig_baseline, fig_off, fig_offsnap, fig_edge, fig_duty, fig_pulsed, fig_equalfuel,
           fig_performance)

if __name__ == "__main__":
    for fn in FIGURES:
        fn()
