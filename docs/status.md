# Status

Last updated 2026-10-13.

## Where things stand

The simulations are finished and the manuscript is drafted: [paper/manuscript.tex](../paper/manuscript.tex), written against [paper/requirements.md](../paper/requirements.md). The run log and every number in the paper are in [experiments.md](experiments.md); validation is in [validation.md](validation.md).

- **Validation:** the solver, chemistry and setup reproduce theory, two published cases, and the open-wedge paper's vapour, no-jet and J = 1 cases. Near the jet the J = 1 front lies within 2 mm of the published one.
- **Jet off:** the detonation survives at least 130 µs. Its base holds for about 10 µs, then retreats at 0.12–0.13 mm/µs and does not settle. It stays within 1 mm of the upstream end of the wall liquid layer, which slides downstream without losing mass; with that liquid removed, the base retreats 2.3 times sooner.
- **Jet width:** a 1 mm jet holds for the same 10 µs, then retreats at about half the speed, as its layer does.
- **Pulsing at 50% duty:** 80 and 40 kHz match the continuous jet in recovery and burnt fuel with half the fuel; 20 kHz does not. The critical frequency lies between 20 and 40 kHz.
- **25% duty at 80 kHz:** the base retreats as with the jet off, so a minimum duty between 25 and 50% is needed as well.
- **Equal fuel:** a half-width steady jet matches pulsing in recovery, but its base drifts 2.2 mm downstream by 145 µs. A jet throttled to J = 0.25 settles about 10 mm downstream.
- **Main caveat:** the wall liquid layer is about 30% liquid by volume in its cells, far outside the point-particle model's dilute limit. All runs are 2D, single realizations, with a slip wall and no turbulence model.
- **Confined baseline** (arXiv:2605.27871): not started; see [case-spec-confined.md](case-spec-confined.md).

## Compute and data

All runs used the container in `container/` (OpenFOAM-8 `a86b07b9dabb`, detonationFoam `02ed90db0a17`, two-phase branch) on one AWS c7a.4xlarge, about $101 in total. The instance was terminated on 2026-10-11. The fields of every run in the paper, the logs and settings of every case, and the instance scripts are archived off-instance (7.4 GB compressed, checksums verified). The figure data in `paper/data` are enough to regenerate every figure.

## Next steps

1. Ask Huangwei Zhang for feedback on the draft.
2. Deposit the field archive and container images (e.g. Zenodo) and cite the DOI under data availability.
3. Before submission, check arXiv listings from July 2026 by hand for new work on the gap ([research.md](research.md#gap)), and obtain the sweeping-jet (Combust. Flame 2024) and on-wedge trip (Combust. Flame 2023) papers.
4. Post to arXiv and submit to Aerospace Science and Technology.
