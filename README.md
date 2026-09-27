# pulswave

Numerical study of pulsed transverse liquid-jet actuation for initiating and stabilizing oblique detonation waves (ODW) in liquid-fuelled oblique detonation engine combustors, benchmarked against published continuous-jet baselines.

## Layout

| Path | Contents |
|---|---|
| `container/` | Apptainer definitions for OpenFOAM-8 and detonationFoam, with every source commit pinned |
| `mechanisms/` | n-heptane chemistry: the Chemkin inputs and the Cantera YAML |
| `template/` | Static OpenFOAM dictionaries shared by every case |
| `pulswave/` | Python package: case builder, analysis and theory checks (`python -m pulswave`) |
| `scripts/run.sh` | Meshes, decomposes and launches a case |
| `docs/` | Research context, reproduction steps, validation record and tool reference |
| `resources/` | Source papers (not tracked) |
| `cases/` | Generated cases (not tracked) |

## Quick start

```
nix develop
python -m pulswave build paper_j1 cases/paper_j1
scripts/run.sh cases/paper_j1
python -m pulswave wave cases/paper_j1 1e-4
```

## Documentation

- [docs/research.md](docs/research.md): the research question, the literature gap and the key papers
- [docs/reproduce.md](docs/reproduce.md): environment, container, and how to build, run and analyse every validated case
- [docs/validation.md](docs/validation.md): known answers compared with our results
- [docs/tools.md](docs/tools.md): command reference
- [docs/assumptions.md](docs/assumptions.md): input values the papers do not state
- [docs/solver.md](docs/solver.md): solver internals and known pitfalls
- [docs/status.md](docs/status.md): current state and next steps
- [docs/references.md](docs/references.md): every paper and code this work uses
- [docs/case-spec-open-wedge.md](docs/case-spec-open-wedge.md), [docs/case-spec-confined.md](docs/case-spec-confined.md): the two baseline papers' specifications

## Acknowledgements

Built on the published work and open-source code listed in [docs/references.md](docs/references.md). Developed with assistance from Claude Opus 5.5 (Anthropic).
