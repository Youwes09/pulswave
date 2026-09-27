# Research context

## Question

Can pulsed transverse liquid-jet injection initiate and stabilize a liquid-fuelled oblique detonation wave at lower time-averaged total-pressure loss and fuel flow than continuous injection?

If it can, is there a critical pulse frequency f_cri, analogous to the one found for pulsed energy deposition? Droplet evaporation adds a timescale that a thermal-only actuator does not have, so f_cri may be set by evaporation rather than gas dynamics alone.

## Gap

Searches in English and Chinese, last checked on 2026-09-07, found no published work combining pulsed or intermittent actuation with a liquid transverse jet for ODW initiation or stabilization. The adjacent work is:

- Continuous liquid-jet ODW control (Wang, Hu & Zhang, both papers below).
- Pulsed energy deposition for gas-phase ODW initiation (Jiang et al.). It shows pulsing can match continuous actuation at 2.3–6.5% of the power, and it defines f_cri. This is the methodology template.

Several groups published in this area in 2026, so the gap must be re-checked before writing up.

## Key papers

| Paper | Role |
|---|---|
| Wang, Hu & Zhang, *Liquid-fueled oblique detonation waves induced by reactive and non-reactive transverse liquid jets*, Aerosp. Sci. Technol. 168 (2026) 111293, arXiv:2506.15247 | Open-wedge continuous-jet baseline. Fully specified; reproduced here. See [case-spec-open-wedge.md](case-spec-open-wedge.md). |
| Wang, Hu & Zhang, *Liquid-fueled Oblique Detonation Stabilized by a Transverse Jet*, arXiv:2605.27871 | Confined-combustor baseline. Not started. See [case-spec-confined.md](case-spec-confined.md). |
| Jiang et al., *Numerical Study of Oblique Detonation Initiation Assisted by Local Energy Deposition*, arXiv:2508.08943 | Pulsed-actuation methodology and f_cri |
| Guo, Xu, Zheng & Zhang, arXiv:2202.04987 | Premixed n-heptane ODW on a 30° wedge; independent solver validation |
| Wang, Yang, Hu & Zhang, *A dynamic droplet breakup model for Eulerian–Lagrangian simulation of liquid-fueled detonation*, arXiv:2404.03170 | The baseline authors' solver and spray settings |
| Sun et al., *detonationFoam*, Comput. Phys. Commun. 292 (2023) 108859 | The solver used here |

The full list is in [references.md](references.md).
