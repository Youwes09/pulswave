"""Robustness extraction: front at all heights, near-jet liquid in several windows, and gas speed in the plug region."""
import json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_front import B, X_JET, droplets, saves
from pulswave import foam, wave

OUT = os.environ.get("OUT", "rule2")
WINDOWS = {f"x{dx}_y{dy}": (dx * 1e-3, dy * 1e-3) for dx in (1, 2, 3, 5) for dy in (1, 2, 3)}


def one(job):
    case, t = job
    rows = foam.load(case, t)
    front = wave.structure(rows, dx=foam.cell_size(rows))
    p = droplets(case, t)
    near = {k: sum(m for x, y, m, _ in p if X_JET - 5e-4 < x < X_JET + dx and y < dy) * 1e9 for k, (dx, dy) in WINDOWS.items()}
    # gas in the plug region: mean streamwise speed and its minimum over cells just behind the jet, below 1 mm
    gas = [r["ux"] for r in rows if X_JET < r["x"] < X_JET + 2e-3 and r["y"] < 1e-3]
    liq = [(m, u) for x, y, m, u in p if X_JET < x < X_JET + 2e-3 and y < 1e-3]
    return t, {
        "front": [[h, x] for h, x, *_ in front],
        "near": near,
        "gas_ux": sum(gas) / len(gas) if gas else None,
        "gas_ux_min": min(gas) if gas else None,
        "liq_ux": sum(m * u for m, u in liq) / sum(m for m, _ in liq) if liq else None,
        "liq_ug_plug": sum(m for m, _ in liq) * 1e9,
    }


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[1:]:
        case = os.path.join(B, name)
        with Pool(6) as pool:
            done = dict(pool.imap_unordered(one, [(case, t) for t in saves(case)]))
        windows = json.load(open(os.path.join(case, "setup.json")))["jet_windows"]
        json.dump({"case": name, "jet_windows": windows, "saves": dict(sorted(done.items(), key=lambda kv: float(kv[0])))},
                  open(os.path.join(OUT, name + ".json"), "w"))
        print(name, len(done), flush=True)
