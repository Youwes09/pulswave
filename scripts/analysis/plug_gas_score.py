"""Score the gas-speed criterion (thresholds fixed in oos_predictions.md) against each case's front."""
import json, sys

HOLD, FAIL = 450, 520
for path in sys.argv[1:]:
    d = json.load(open(path))
    s = sorted(((float(t) * 1e6, r) for t, r in d["saves"].items()), key=lambda v: v[0])
    g = sorted(r["gas_ux"] for _, r in s if r["gas_ux"] is not None)
    med = g[len(g) // 2]
    call = "HOLD" if med <= HOLD else "FAIL" if med >= FAIL else "GREY"
    y4 = lambda r: next((x for h, x in r["front"] if h == 4), None)
    trace = "  ".join(f"{t:.0f}:{r['gas_ux']:.0f}/{y4(r) or 0:.1f}" for t, r in s)
    print(f"{d['case']:18s} median {med:5.0f} -> {call}\n   t:gas/y4  {trace}")
