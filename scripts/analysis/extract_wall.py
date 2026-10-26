"""Near-wall gas state behind the jet per save, to test whether recapture after a pulse is re-ignition of the pulse's fuel."""
import json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_front import B, X_JET, saves
from pulswave import foam

OUT = os.environ.get("OUT", "rule3")
BOXES = {"x0_3_y1": (0.0, 3e-3, 1e-3), "x0_3_y2": (0.0, 3e-3, 2e-3), "x3_8_y2": (3e-3, 8e-3, 2e-3)}


def one(job):
    case, t = job
    rows = foam.load(case, t, foam.FIELDS + ("Qdot",))
    out = {}
    for k, (a, b, h) in BOXES.items():
        c = [r for r in rows if X_JET + a < r["x"] < X_JET + b and r["y"] < h]
        out[k] = {
            "T_mean": sum(r["T"] for r in c) / len(c),
            "T_max": max(r["T"] for r in c),
            "fuel": sum(r["NXC7H16"] for r in c) / len(c),
            "CO2": sum(r["CO2"] for r in c) / len(c),
            "hot_frac": sum(r["T"] > 2000 for r in c) / len(c),
            "Qdot": sum(r["Qdot"] for r in c),
            "p_max": max(r["p"] for r in c),
        }
    return t, out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[1:]:
        case = os.path.join(B, name)
        with Pool(4) as pool:
            done = dict(pool.imap_unordered(one, [(case, t) for t in saves(case)]))
        windows = json.load(open(os.path.join(case, "setup.json")))["jet_windows"]
        json.dump({"case": name, "jet_windows": windows, "saves": dict(sorted(done.items(), key=lambda kv: float(kv[0])))},
                  open(os.path.join(OUT, name + ".json"), "w"))
        print(name, len(done), flush=True)
