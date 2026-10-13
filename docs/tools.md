# Tools

Everything runs through `python -m pulswave <command>`.

The analysis commands (`wave`, `anchor`, `profile`, `streamline`, `health`, `nearjet`, `pocket`, `liquid`, `performance`, `guo`) use only the Python standard library, so they run directly on the compute host. They read decomposed cases, and need the cell centres that `scripts/run.sh` writes to `processor*/0/C`. Times are given as the time-directory names, for example `9e-05`.

The `theory` command needs Cantera, and `digitize` needs Pillow. Both are provided by `nix develop`.

## Building cases

| Command | Result |
|---|---|
| `build <preset> <dest> [--J 0.1\|0.5\|1\|2] [--jet-u U] [--end T] [--write T] [--nproc N]` | Writes a complete detonationFoam case and its parameters (`setup.json`). Presets are listed in [reproduce.md](reproduce.md). |
| `ignition <dest> --T T [--p P] [--phi PHI]` | Writes a chemFoam constant-pressure ignition case for the same mechanism |
| `branch <src> <dest> <t> --end T [--jet-off \| --jet-on \| --pulse FREQ_HZ DUTY] [--jet-u M_S] [--half-width] [--jet-scale F] [--wall rebound\|escape\|stick] [--drop-jet-liquid]` | Copies a decomposed case at time t and restarts it with the jet stopped at t, switched on from t, or pulsed from t onward, with the jet velocity changed by `--jet-u`, optionally with a different droplet–wall interaction. Pulses are separate injection windows. `--half-width` halves the jet's width and fuel at the same velocity: the jet injects over the downstream one of its two wall faces (`coneInjection` on a one-cell disc) instead of the whole patch, so the mesh is unchanged. `--jet-scale F` multiplies the jet mass flow (and parcel rate) by F at the same velocity, so J by velocity is unchanged but the momentum flux per unit area falls by F; with `--half-width`, `--jet-scale 0.5` gives a quarter of the full jet fuel. `--drop-jet-liquid` deletes every parcel injected by the jet from the copied save, identified by its injection position (`position0`), and keeps the freestream spray. |

`scripts/run.sh <case>` then meshes the case, cuts the jet patch if there is one, decomposes it, writes the cell centres and launches the solver detached. `scripts/run.sh --restart <case>` launches a branch from its copied save without meshing or decomposing, which would discard that save. Set `SIF` to the container image when it is not at `~/PULSWAVE/container/detonationfoam.sif`.

## Analysis

| Command | Output |
|---|---|
| `wave <case> <t...>` | Front height at the x positions digitized from paper Fig. 3c, both the top of the region above 1900 K and the leading shock, next to the paper's values. Also, per height above the wall: the detonation base (the first strong pressure rise with CO2 > 0.02 within 1 mm behind it), the pressure ratio across it, and the gap between the shock and the start of burning. |
| `anchor <case> <t...>` | Upstream edge of burning near the wall, and the upstream near-wall temperature, maximum CO2 and number of cells above 1500 K. These separate an anchored front from upstream flashback or startup pockets. |
| `profile <case> <t> [--heights mm...] [--x0 mm] [--x1 mm] [--step n]` | Rows of T, p, CO2, C7H16, ux and Mach at fixed heights |
| `streamline <case> <t> [--y0 mm] [--every mm]` | RK2 streamline from (0, y0), the same construction as paper Figs. 3 and 6 |
| `health <case> <t>` | Minimum Mach at the outflow (sound speed from the local composition, within 3% of Cantera), the state along the top boundary, the leading-shock height and angle along x, and droplet parcels per 1000 cells in fixed regions compared with the fully loaded freestream value |
| `nearjet <case> <t>` | Near-wall state upstream of the jet, the fuel-rich wall layer behind it and its subsonic part, the liquid mass within 30 mm of the jet, and the gas speed behind the front at several heights |
| `performance <case> <t...> [--x MM] [--ymax MM] [--duty D] [--preset NAME]` | Mass-flux-weighted total pressure entering the domain and crossing a plane (default: the outflow), the part of that plane behind the leading shock, fuel supplied by the freestream and the jet, and fuel crossing the plane burnt (CO2 + CO carbon) and as vapour. Averaged over the given saves. Total pressure uses the frozen composition of all species in the mechanism and the solver JANAF tables, and matches Cantera to 0.005%. `--preset` is used when the case has no `setup.json`. `--by-height` adds recovery and mass flux in height bands up to 25 mm, mass-weighted over all saves (needs `--x`). `--check` prints, per save, the plane's mass flux, reversed-flow mass, cells below 600 K, the largest cell total pressure relative to the inflow, and the recovery of the cells without reversed flow or outlier total pressure. |
| `pocket <case> <t>` | Liquid behind the jet (x = 49.5–80 mm, y < 3 mm): mass, parcels, mass-weighted diameter, droplet temperature, and the temperature and C7H16 fraction of the gas around the droplets; mass loading and liquid volume fraction over the region and over the cells that hold liquid |
| `liquid <case> <t...>` | Liquid mass per 10 mm of x in three height bands (y < 1, 1–5, > 5 mm) |
| `guo <case> <t> --phi 1\|0.2` | Post-shock wall temperature and initiation length (by heat-release peak, and by T > 1.1 × post-shock) against arXiv:2202.04987 |

## Theory

These use `mechanisms/nHeptane.yaml` with Cantera.

| Command | Output |
|---|---|
| `theory shock` | Frozen-composition oblique-shock state (with temperature-dependent thermo) for the engine inflow (air, and stoichiometric vapour) and for the Guo cases |
| `theory cj` | Chapman–Jouguet speed, pressure ratio and temperature for the post-shock mixture |
| `theory ignition` | Constant-pressure ignition delays, taken at the heat-release peak, at 2.8 bar |
| `theory timescales [--T --p --u --fuel --o2]` | Ignition delay of the gas approaching the jet, and the state and ignition delay behind a normal shock at its Mach number. Defaults are the `nearjet` values from `paper_j1`. |
| `theory thermo` | Worst cp and h mismatch between `template/constant/speciesThermo` and Cantera |

## Paper figures

`digitize <png>` extracts the ODW front heights from paper Fig. 3c. Produce the input with:

```
pdftoppm -f 6 -l 6 -r 170 -png resources/2506.15247v1.pdf fig
```

The panel covers x = 0–0.209 m (not the full 0.25 m domain) and y = 0–0.1 m. The front is the top of the red region, which is about T > 1900 K on the paper's colour map. The result is stored in `pulswave/reference.py`.

## Checks

One-off checks behind statements in [experiments.md](experiments.md), kept so they can be rerun:

| Script | Checks |
|---|---|
| `scripts/checks/total_pressure_cantera.py <case> <t> <x_mm>,<y_mm>...` | The cell total pressure of `performance` against Cantera's isentropic stagnation at frozen composition. Needs Cantera (`nix develop`). |
| `scripts/checks/tracker_compare.py <case>...` | The front base from the current tracker against the earlier largest-rise tracker, for every save from 70 µs |
