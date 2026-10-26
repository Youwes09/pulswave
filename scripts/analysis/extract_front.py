"""Per save: front at every height, liquid plug state and jet phase, for building the pulsing rule. One JSON per case."""
import glob, json, math, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import foam, wave

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
OUT = os.environ.get("OUT", "rule")
X_JET = 0.05


def droplets(case, t):
    out = []
    for C, cloud in foam._clouds(case, t):
        d, n, rho, U = (foam._cloud_field(cloud, f) for f in ("d", "nParticle", "rho", "U"))
        for c, di, ni, ri, ui in zip(foam._cloud_cells(cloud), d, n, rho, U):
            out.append((C[c][0], C[c][1], float(ni) * float(ri) * math.pi / 6 * float(di) ** 3, float(ui.strip("() ").split()[0])))
    return out


def quantile(pairs, q):
    pairs, acc = sorted(pairs), 0.0
    total = sum(w for _, w in pairs)
    for v, w in pairs:
        acc += w
        if acc >= q * total:
            return v


def one(job):
    case, t = job
    rows = foam.load(case, t)
    front = wave.structure(rows, dx=foam.cell_size(rows))
    p = [q for q in droplets(case, t) if q[1] < 3e-3 and X_JET - 5e-4 < q[0] < 0.1]
    xm = [(q[0], q[2]) for q in p]
    x10 = quantile(xm, 0.1) if p else None
    lead = [q for q in p if q[0] <= x10] if p else []
    near = [q for q in p if q[0] < X_JET + 3e-3]
    return t, {
        "front": [[h, x, r] for h, x, r, _ in front],
        "base": wave.base(front),
        "edge5": quantile(xm, 0.05) * 1e3 if p else None,
        "edge25": quantile(xm, 0.25) * 1e3 if p else None,
        "liquid_ug": sum(q[2] for q in p) * 1e9,
        "near_ug": sum(q[2] for q in near) * 1e9,
        "u_lead": sum(q[2] * q[3] for q in lead) / sum(q[2] for q in lead) if lead else None,
    }


def saves(case):
    return sorted((d for d in os.listdir(os.path.join(case, "processor0")) if d.replace(".", "").replace("e-", "").isdigit() and float(d) > 0), key=float)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[1:]:
        case = os.path.join(B, name)
        path = os.path.join(OUT, name + ".json")
        done = json.load(open(path))["saves"] if os.path.exists(path) else {}
        todo = [(case, t) for t in saves(case) if t not in done]
        with Pool(6) as pool:
            for t, rec in pool.imap_unordered(one, todo):
                done[t] = rec
        windows = json.load(open(os.path.join(case, "setup.json")))["jet_windows"]
        json.dump({"case": name, "jet_windows": windows, "saves": dict(sorted(done.items(), key=lambda kv: float(kv[0])))}, open(path, "w"))
        print(name, len(done), flush=True)
