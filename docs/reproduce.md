# Reproducing the results

## Environment

- **Local machine:** `nix develop` provides Apptainer, Python with Cantera 3.2.0 and Pillow (in `.venv`), and `pdftoppm`.
- **Compute host:** needs only Singularity/Apptainer, Python 3.8+ and this repository. The validated runs used an AWS c7a.4xlarge (16 vCPU, 32 GB, us-east-1, about $0.82/h on demand) with Ubuntu and Singularity.

## Container

The container is built in two stages. Every source commit is pinned:

- OpenFOAM-8 `a86b07b9dabb`
- ThirdParty-8 `686040d3c082`
- detonationFoam `02ed90db0a17` (branch `detonationFoam-dev(two-phase)`)

```
cd container
apptainer build openfoam8-base.sif openfoam8-base.def
apptainer build detonationfoam.sif detonationfoam.def
```

The image the validated runs used had sha256 `b02193347a146d11d8605703c55e3c71c68f83139e84c6c82f074411de94ac34`. Every solver log prints `Build : 8-a86b07b9dabb`.

## Mechanism

`template/constant/reactions` and `template/constant/speciesThermo` are committed. Their regeneration command is in [mechanisms/README.md](../mechanisms/README.md), and it reproduces them byte for byte.

## Cases

Each case is generated from `template/` plus the parameters in `pulswave/build.py`:

```
python -m pulswave build <preset> cases/<name>
scripts/run.sh cases/<name>
```

| Preset | Domain (mm) | Inflow | Fuel | Jet | End (µs) | Ranks | Reproduces |
|---|---|---|---|---|---|---|---|
| `paper_j1` | 250 × 100 | 697 K, 0.2818 atm, 2535 m/s at 27° | 10 µm droplets, φ = 1 | J = 1, 60.83 m/s | 250 | 16 | arXiv:2506.15247 Fig. 3c |
| `paper_nojet` | 250 × 100 | same | droplets | none | 150 | 16 | Fig. 3b (full domain; not run yet) |
| `crop_jet` | 80 × 15 | same | droplets | J = 1 | 50 | 8 | Near-jet anchoring test |
| `crop_nojet` | 60 × 15 | same | droplets | none | 60 | 8 | Fig. 3b near-wall state |
| `crop_vapor` | 100 × 16 | same | premixed vapour, φ = 1 | none | 150 | 8 | Fig. 3a |
| `box_small` | 90 × 35 | same as `paper_j1` | droplets | J = 1 | 80 | 8 | Screening domain ([experiments.md](experiments.md)) |
| `box_large` | 120 × 45 | same | droplets | J = 1 | 80 | 8 | Screening domain containing the subsonic part of the wall wake |
| `crop_grid` | 100 × 25 | same | droplets | J = 1 | 50 | 8 | Grid-check crop at 0.2 mm ([experiments.md](experiments.md#step-4-grid-check-of-the-memory)) |
| `crop_grid_fine` | 100 × 25 | same | droplets | J = 1 | 50 | 8 | The same crop at 0.15 mm (667 × 167 cells; the jet patch is three faces, 0.45 mm) |
| `crop_grid_d1` | 100 × 25 | same | droplets | J = 1, 1 mm jet | 50 | 8 | Memory scaling with jet width: twice the jet width and fuel at the same J |
| `guo_phi1` | 60 × 20 | 298 K, 1 atm, 2900 m/s at 30° | premixed, φ = 1 | none | 80 | 8 | arXiv:2202.04987, φ = 1 |
| `guo_phi02` | 60 × 20 | same | premixed, φ = 0.2 | none | 80 | 8 | arXiv:2202.04987, φ = 0.2 |

The cell size is 0.2 mm, the paper's production resolution, everywhere except `crop_grid_fine`.

Ignition-delay cases run serially:

```
python -m pulswave ignition cases/ign_1400 --T 1400
cd cases/ign_1400 && singularity exec <sif> chemFoam
```

## Run time

On 16 vCPU, `paper_j1` (625,000 cells) takes about 20 minutes per simulated microsecond at first. This rises to about 58 minutes once the domain holds about 155,000 parcels and 160,000 burning cells. Reaching 100 µs takes about 3 days, roughly $60 on demand.

The crop and Guo cases have 22,500–40,000 cells, so two of them run on the host at once.

## Analysis

See [tools.md](tools.md). A typical check of a running full case:

```
python -m pulswave health cases/paper_j1 1e-4
python -m pulswave anchor cases/paper_j1 1e-4
python -m pulswave wave cases/paper_j1 8e-05 9e-05 1e-4
python -m pulswave streamline cases/paper_j1 1e-4
```

## Differences from the runs recorded in validation.md

- **Inflow velocity:** the validated spray runs (`paper_j1`, `crop_jet`, `crop_nojet`) used a hand-rounded vector (2258.3, −1150.9) m/s, which is 2534.7 m/s. The builder writes the exact vector for 2535 m/s at 27°, (2258.702, −1150.866). The premixed validation cases already used the exact vector.
- **Freestream parcel rates:** the builder computes them from the inflow state, and they differ from the hand-derived values used in the runs by at most 0.1%.
- **Initial state of the validated `paper_j1` run:** it did not start from uniform freestream. It was mapped from a settled `crop_jet` state at 36 µs, which was itself mapped from `crop_nojet`. `mapFields -parallelSource` kept only 35 of about 30,000 droplet parcels, so that run started almost droplet-free and spent roughly its first 25 µs near the jet, and about 110 µs across the whole domain, re-loading droplets from the boundaries. The builder starts from uniform freestream, with droplets entering through the boundaries.
- **Run-to-run variation:** droplet injection positions are random per processor, so results depend on the decomposition. Runs reproduce statistically, not bit for bit. The validated runs used scotch decomposition on 16 ranks (full domain) and 8 ranks (crops and Guo cases).
