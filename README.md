# pulswave

Pulsed transverse liquid-jet actuation for oblique detonation wave (ODW)
initiation and stabilization in a confined ODWE combustor, benchmarked
against continuous-jet baselines.

## Hypothesis

Pulsed liquid-jet injection can achieve ODW initiation/stabilization at
lower time-averaged pressure loss and fuel flow than continuous injection
at the same reference momentum ratio. A critical pulse frequency f_cri is
expected, set by droplet evaporation timescale rather than gasdynamics
alone.

## Layout

```
container/   Apptainer definitions and built .sif images
docs/        build notes, case specs, project context
cases/       OpenFOAM case directories
resources/   source papers (PDF)
```

## Setup

```
nix develop
```

See docs/CONTEXT.md for full project state and next steps, docs/phase0.md
for the container build sequence, docs/case-spec-open-wedge.md and
docs/case-spec-confined.md for the two reproduction targets.

## References

Wang, W., Hu, Z., Zhang, P. Liquid-fueled Oblique Detonation Stabilized by
a Transverse Jet. arXiv:2605.27871 (2026).

Wang, W., Hu, Z., Zhang, P. Liquid-fueled oblique detonation waves induced
by reactive and non-reactive transverse liquid jets. Combustion and Flame
(2025). arXiv:2506.15247.

Jiang, Z., Chen, Z., Shi, L., Zhang, Z., Hao, J., Wen, C.-Y. Numerical
Study of Oblique Detonation Initiation Assisted by Local Energy
Deposition. arXiv:2508.08943 (2025).

Sun, J., Wang, Y., Tian, B., Chen, Z. detonationFoam: An open-source
solver for simulation of gaseous detonation based on OpenFOAM. Computer
Physics Communications 292, 108859 (2023).