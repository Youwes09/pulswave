# Status

Last updated 2026-10-26.

## Where things stand

The manuscript is final for submission to Physics of Fluids: [paper/manuscript.tex](../paper/manuscript.tex), with the cover letter in [paper/cover_letter.md](../paper/cover_letter.md). Every number in it is reproduced by [scripts/analysis/claims.py](../scripts/analysis/claims.py). [experiments.md](experiments.md) and [research.md](research.md) are the working notes from the runs; where they differ from the manuscript, the manuscript holds.

- **Validation:** the solver, chemistry and setup reproduce theory, two published cases, and the open-wedge paper's vapor, no-jet and J = 1 cases. Near the jet the J = 1 front lies 0.5–2.8 mm below the published one.
- **Jet off:** the detonation survives the 130 µs simulated. The base holds for 11.5–20 µs, about one flow-through time behind the front, then retreats at 0.07–0.10 mm/µs. About 10 µs of the hold remains with no jet liquid.
- **Duty cycle:** at an off-time of 6.25 µs, 50% duty holds the base and 25% duty does not.
- **Frequency at 50% duty:** 80 kHz holds the base within 1.2 mm of the continuous jet; 20–40 kHz oscillate by 3–4 mm. No critical frequency can be defined from these runs.
- **Equal fuel:** the 80 kHz pulse holds the base, the jet throttled to J = 0.25 loses it, and the half-width jet holds or loses it depending on the injection model.
- **Main caveats:** single realizations, 2D and laminar, a dense near-wall spray where the vapor mass fraction exceeds 1, and about 40% grid sensitivity in the displacement after switch-off.

## Compute and data

All runs used the container in `container/` (OpenFOAM-8 `a86b07b9dabb`, detonationFoam `02ed90db0a17`, two-phase branch) on AWS c7a instances. The fields, logs and settings of every run are archived off-instance. The figure data in `paper/data` are enough to regenerate every figure.

## Next steps

1. Done: release archived on Zenodo, doi:10.5281/zenodo.23676003.
2. Submit to Physics of Fluids.
