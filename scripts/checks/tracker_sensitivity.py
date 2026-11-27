"""Front positions at y = 2-9 mm for every variant of the tracker thresholds, per save.

Variants: pressure factor 1.3 / 1.5 / 2.0 (burnt-gas cutoff 0.02); burnt-gas cutoff 0.01 / 0.05 (factor 1.5);
temperature fronts at 1500 K and 1900 K. One JSON per case in $OUT (default tracker/), resumable.
Usage (run host): OUT=~/tracker python3 scripts/checks/tracker_sensitivity.py case [case ...]
"""
import json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import foam, wave

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
OUT = os.environ.get("OUT", "tracker")
H = (2, 3, 4, 5, 6, 9)
VARIANTS = {f"p{r}_c{c}": (r, c) for r, c in ((1.3, 0.02), (1.5, 0.02), (2.0, 0.02), (1.5, 0.01), (1.5, 0.05))}


def one(job):
    case, t = job
    rows = foam.load(case, t, fields=("T", "p", "CO2", "CO"))
    dx = foam.cell_size(rows)
    rec = {k: [[h, x] for h, x, *_ in wave.structure(rows, heights_mm=H, dx=dx, rise=r, burnt_min=c)]
           for k, (r, c) in VARIANTS.items()}
    for T in (1500, 1900):
        rec[f"T{T}"] = [[h, x] for h, x in wave.front_T(rows, T, heights_mm=H, dx=dx)]
    return t, rec


def saves(case):
    return sorted((d for d in os.listdir(os.path.join(case, "processor0"))
                   if d.replace(".", "").replace("e-", "").isdigit() and float(d) > 0), key=float)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[1:]:
        case, path = os.path.join(B, name), os.path.join(OUT, name + ".json")
        done = json.load(open(path)) if os.path.exists(path) else {}
        todo = [(case, t) for t in saves(case) if t not in done]
        with Pool(int(os.environ.get("NP", "6"))) as pool:
            for t, rec in pool.imap_unordered(one, todo):
                done[t] = rec
        json.dump(dict(sorted(done.items(), key=lambda kv: float(kv[0]))), open(path, "w"))
        print(name, len(done), flush=True)
