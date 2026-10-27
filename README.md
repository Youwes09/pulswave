# pulswave

Two-dimensional Eulerian-Lagrangian study of an n-heptane spray oblique detonation wave (ODW) anchored by a transverse liquid jet when the jet is switched off, pulsed or throttled: how long the base holds after the jet stops, which pulse frequencies and duty cycles keep it held, and whether pulsing or throttling at half the fuel does. Benchmarked against a published continuous-jet baseline.

## Layout

| Path | Contents |
|---|---|
| `container/` | Apptainer definitions for OpenFOAM-8 and detonationFoam, with every source commit pinned |
| `mechanisms/` | n-heptane chemistry: the Chemkin inputs and the Cantera YAML |
| `template/` | Static OpenFOAM dictionaries shared by every case |
| `pulswave/` | Python package: case builder, analysis and theory checks (`python -m pulswave`) |
| `scripts/run.sh` | Meshes, decomposes and launches a case |
| `scripts/campaign/` | Builds and queues the switch-off, pulsing and equal-fuel runs |
| `scripts/analysis/` | Extractions, the claims ledger (`claims.py`) and the performance scripts behind the numbers in the manuscript |
| `scripts/checks/` | One-off checks behind statements in the docs (tracker comparison, total pressure against Cantera) |
| `docs/` | Research context, reproduction steps, validation record and tool reference |
| `paper/` | Manuscript (`manuscript.tex`), its figures, the data behind them (`data/`) and the script that plots them (`figures.py`) |
| `resources/` | Source papers (not tracked) |
| `cases/` | Generated cases (not tracked) |

## Quick start

```
nix develop
python -m pulswave build paper_j1 cases/paper_j1
scripts/run.sh cases/paper_j1
python -m pulswave wave cases/paper_j1 1e-4
```

Figures: `python paper/figures.py` plots `paper/data` into `paper/figures`; `python -m pulswave figdata <cases> <out>` re-extracts the data from saved fields.

## Documentation

- [docs/research.md](docs/research.md): the research question, the literature gap and the key papers
- [docs/reproduce.md](docs/reproduce.md): environment, container, and how to build, run and analyse every validated case
- [docs/validation.md](docs/validation.md): known answers compared with our results
- [docs/tools.md](docs/tools.md): command reference
- [docs/assumptions.md](docs/assumptions.md): input values the papers do not state
- [docs/solver.md](docs/solver.md): solver internals and known pitfalls
- [docs/status.md](docs/status.md): current state and next steps
- [docs/experiments.md](docs/experiments.md): the jet-off, pulsed-jet and grid-check experiments and their results
- [docs/references.md](docs/references.md): every paper and code this work uses
- [docs/case-spec-open-wedge.md](docs/case-spec-open-wedge.md), [docs/case-spec-confined.md](docs/case-spec-confined.md): the two baseline papers' specifications

## Acknowledgements

Simulations use [detonationFoam](https://github.com/JieSun-pku/detonationFoam) (Sun et al., Comput. Phys. Commun. 292 (2023) 108859) on OpenFOAM-8. The 44-species n-heptane mechanism files were provided by Huangwei Zhang and Tsingyoung Meng. All published work and code this project builds on is listed in [docs/references.md](docs/references.md). Developed with assistance from Claude Opus 5.5 (Anthropic).
