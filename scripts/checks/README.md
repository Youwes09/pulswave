# Checks

One-off checks behind statements in the docs and the manuscript.

| Script | Checks |
|---|---|
| `check_tex.py <tex>` | Manuscript source: every citation defined and cited in order, bibliography order (`--fix-order` re-sorts it), labels and references, figure order, and known-error strings |
| `sensitivity.py [paper/data]` | Holds, retreat speeds, offsets and drift for five base definitions and hold thresholds of 1.25–2.5 cells |
| `tracker_sensitivity.py <case>...` | Front positions for every tracker variant: pressure factor 1.3 / 1.5 / 2.0, burnt-gas cutoff 0.01 / 0.02 / 0.05, temperature fronts at 1500 and 1900 K |
| `tracker_compare.py <case>...` | Base per height with the earlier tracker (largest pressure rise) against the current one, every save from 70 µs |
| `total_pressure_cantera.py <case> <t> <x,y>...` | Cell total pressure from `pulswave.performance` against Cantera (isentropic, frozen composition) |
| `liquid_edge.py <case> <t...>` | Near-wall liquid behind the jet: total mass, mass within 3 mm of the jet, and its 5, 25 and 50% points |
