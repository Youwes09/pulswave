FIG3C_FRONT = {52: 10.4, 54: 13.3, 56: 14.8, 58: 16.3, 60: 17.0, 63: 20.0, 66: 21.5, 70: 23.7, 75: 28.1, 80: 30.4,
               85: 33.3, 90: 36.3, 100: 41.5, 120: 49.6, 150: 63.0, 200: 79.3}

GUO_LI_MM = {1.0: 19.8, 0.2: 3.47}
GUO_POSTSHOCK_T = {1.0: 1452, 0.2: 1601}

FIG3C_PANEL = {"x_span_mm": 209.0, "y_span_mm": 100.0, "window": (570, 870, 1280, 1430)}


def digitize_fig3c(png, xs_mm=tuple(FIG3C_FRONT)):
    from PIL import Image

    px = Image.open(png).convert("RGB").load()
    x0, x1, y0, y1 = FIG3C_PANEL["window"]
    coloured = lambda c: max(c) - min(c) > 60
    hot = lambda c: c[0] > 170 and c[0] > c[2] + 60
    cols = [x for x in range(x0, x1) if sum(coloured(px[x, y]) for y in range(y0, y1)) > 0.6 * (y1 - y0)]
    rows = [y for y in range(y0, y1) if sum(coloured(px[x, y]) for x in range(x0, x1)) > 0.6 * (x1 - x0)]
    xl, xr, yt, yb = min(cols), max(cols), min(rows), max(rows)
    out = {}
    for xm in xs_mm:
        x = round(xl + (xr - xl) * xm / FIG3C_PANEL["x_span_mm"])
        y = next((y for y in range(yt, yb - 2) if all(hot(px[x, y + k]) for k in range(3))), None)
        out[xm] = (yb - y) / (yb - yt) * FIG3C_PANEL["y_span_mm"] if y is not None else float("nan")
    return out
