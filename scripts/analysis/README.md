# Analysis scripts

Per-save extraction behind the campaign results. Set `BOXES` to the case directory and `OUT` to the output directory.

| Script | Writes, per save |
|---|---|
| `extract_front.py <case>...` | Front per height, base (median over y = 4-6 mm), liquid edge quantiles, liquid near the jet (x < 53 mm, y < 3 mm) |
| `extract_plug.py <case>...` | Front, liquid in windows behind the jet, and gas and liquid streamwise speed in the plug region (x = 50-52 mm, y < 1 mm) |
| `extract_wall.py <case>...` | Near-wall gas state behind the jet: temperature, fuel, CO2, hot fraction, heat release, peak pressure |
| `plug_gas.py <root> <out> <case>...` | Front and plug-region gas speed only, single process |
| `plug_gas_score.py <json>...` | Plug gas speed per case against the front, with the thresholds fixed before the out-of-sample test |

Numbers in the manuscript, recomputed from the tracked data or from the cases:

| Script | Gives |
|---|---|
| `claims.py [paper/data]` | Every front, hold, retreat, duty, frequency, plug and early-performance number (the ledger) |
| `performance_table.py <dir> <ref> <case>...` | Late-window recovery and burnt fuel over the saves that pass the plane check |
| `plane_bands.py <t0> <t1> <case>...` | Burnt and vapour fuel per height band at the plane |
| `injected.py <case> <t0> <case> <t1>` | Jet liquid injected between two saves |
| `baseline.sh <boxes>` | Near-jet state of the reference and the pocket after switch-off, into `paper/data/campaign/baseline.txt` |
| `jet_shock.py <T> <p atm> <C7H16> <O2> <ratio>...` | Frozen state and ignition delay behind a shock of the given pressure ratio |
| `scan_fuel.py <case>...` | Saves where the n-heptane mass fraction leaves [0, 1], counted in the regions the diagnostics use, into `paper/data/campaign/fuel_bounds.txt` |
