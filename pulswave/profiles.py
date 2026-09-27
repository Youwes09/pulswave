import math

KEYS = ("T", "p", "NXC7H16", "CO2", "O2")


def line(rows, y, x0, x1, dx=0.2e-3):
    j = int(y / dx + 1e-6)
    return sorted((r for r in rows if int(r["y"] / dx) == j and x0 <= r["x"] <= x1), key=lambda r: r["x"])


def sound(T):
    return math.sqrt(1.3 * 8.314 / 0.0288 * T)


def mach(r):
    return math.hypot(r["ux"], r["uy"]) / sound(r["T"])


def streamline(rows, x0=0.0, y0=1e-3, dx=0.2e-3, ds=0.05e-3):
    grid = {(int(r["x"] / dx), int(r["y"] / dx)): r for r in rows}
    nx = 1 + max(i for i, _ in grid)
    ny = 1 + max(j for _, j in grid)
    keys = ("ux", "uy") + KEYS

    def sample(x, y):
        fx, fy = x / dx - 0.5, y / dx - 0.5
        i0, j0 = math.floor(fx), math.floor(fy)
        ax, ay = fx - i0, fy - j0
        acc = dict.fromkeys(keys, 0.0)
        for di, dj, w in ((0, 0, (1 - ax) * (1 - ay)), (1, 0, ax * (1 - ay)), (0, 1, (1 - ax) * ay), (1, 1, ax * ay)):
            r = grid[(min(max(i0 + di, 0), nx - 1), min(max(j0 + dj, 0), ny - 1))]
            for k in keys:
                acc[k] += w * r[k]
        return acc

    x, y, path = x0, y0, []
    while x < (nx - 1) * dx and 0 < y < ny * dx:
        s = sample(x, y)
        path.append(dict(s, x=x, y=y))
        m = math.hypot(s["ux"], s["uy"])
        h = sample(x + 0.5 * ds * s["ux"] / m, y + 0.5 * ds * s["uy"] / m)
        m2 = math.hypot(h["ux"], h["uy"])
        x += ds * h["ux"] / m2
        y = max(y + ds * h["uy"] / m2, 0.5 * dx)
    return path
