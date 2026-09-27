# Tools

Everything runs through `python -m pulswave <command>`.

The analysis commands (`wave`, `anchor`, `profile`, `streamline`, `health`, `guo`) use only the Python standard library, so they run directly on the compute host. They read decomposed cases, and need the cell centres that `scripts/run.sh` writes to `processor*/0/C`. Times are given as the time-directory names, for example `9e-05`.

The `theory` command needs Cantera, and `digitize` needs Pillow. Both are provided by `nix develop`.

## Building cases

| Command | Result |
|---|---|
| `build <preset> <dest> [--J 0.1\|0.5\|1\|2] [--jet-u U] [--end T] [--write T] [--nproc N]` | Writes a complete detonationFoam case. Presets are listed in [reproduce.md](reproduce.md). |
| `ignition <dest> --T T [--p P] [--phi PHI]` | Writes a chemFoam constant-pressure ignition case for the same mechanism |

`scripts/run.sh <case>` then meshes the case, cuts the jet patch if there is one, decomposes it, writes the cell centres and launches the solver detached. Set `SIF` to the container image when it is not at `~/PULSWAVE/container/detonationfoam.sif`.

## Analysis

| Command | Output |
|---|---|
| `wave <case> <t...>` | Front height at the x positions digitized from paper Fig. 3c, both the top of the region above 1900 K and the leading shock, next to the paper's values. Also, per height above the wall: the jet-front shock position, the pressure ratio across it, and the gap between the shock and the start of burning (CO2 > 0.02). |
| `anchor <case> <t...>` | Upstream edge of burning near the wall, and the upstream near-wall temperature, maximum CO2 and number of cells above 1500 K. These separate an anchored front from upstream flashback or startup pockets. |
| `profile <case> <t> [--heights mm...] [--x0 mm] [--x1 mm] [--step n]` | Rows of T, p, CO2, C7H16, ux and Mach at fixed heights |
| `streamline <case> <t> [--y0 mm] [--every mm]` | RK2 streamline from (0, y0), the same construction as paper Figs. 3 and 6 |
| `health <case> <t>` | Minimum Mach at the outflow, the state along the top boundary, the leading-shock height and angle along x, and droplet parcels per 1000 cells in fixed regions compared with the fully loaded freestream value |
| `guo <case> <t> --phi 1\|0.2` | Post-shock wall temperature and initiation length (by heat-release peak, and by T > 1.1 × post-shock) against arXiv:2202.04987 |

## Theory

These use `mechanisms/nHeptane.yaml` with Cantera.

| Command | Output |
|---|---|
| `theory shock` | Frozen-composition oblique-shock state (with temperature-dependent thermo) for the engine inflow (air, and stoichiometric vapour) and for the Guo cases |
| `theory cj` | Chapman–Jouguet speed, pressure ratio and temperature for the post-shock mixture |
| `theory ignition` | Constant-pressure ignition delays, taken at the heat-release peak, at 2.8 atm |
| `theory thermo` | Worst cp and h mismatch between `template/constant/speciesThermo` and Cantera |

## Paper figures

`digitize <png>` extracts the ODW front heights from paper Fig. 3c. Produce the input with:

```
pdftoppm -f 6 -l 6 -r 170 -png resources/2506.15247v1.pdf fig
```

The panel covers x = 0–0.209 m (not the full 0.25 m domain) and y = 0–0.1 m. The front is the top of the red region, which is about T > 1900 K on the paper's colour map. The result is stored in `pulswave/reference.py`.
