# Research context

> Working notes from the runs. Where they differ from the manuscript, the manuscript holds.

## Question

How does an oblique detonation held by a transverse liquid jet respond when the jet is interrupted or pulsed, and what sets how long it stays anchored without the jet?

1. **Memory.** After the jet stops, how long does the front base hold, what holds it, and how does that time scale with the jet?
2. **Frequency.** For a pulsed jet, at what frequency does the front stop being held (a critical frequency f_cri, as for pulsed energy deposition), and does the memory time predict it?
3. **What holds the front.** At equal mean jet fuel, which matters: the jet's momentum ratio J while it is on, or its mean fuel flow?

### Revision of 2026-10-06

The original question was whether pulsing stabilizes the detonation at lower total-pressure loss and fuel flow than continuous injection. The runs to date answer it:

- Pulsed jets at 50% duty hold the front at control-level recovery with half the jet fuel. They do not lower the total-pressure loss.
- A steady jet of half the width at the same J (`large_narrow`) does the same at the same mean fuel. In this 2D model, pulsing therefore has no advantage over a properly sized steady jet at 50% fuel.
- A half-velocity steady jet (J = 0.25, below the paper's J ≥ 0.4) at the same mean fuel does not hold the front.

So the front is held by J while the jet is on, with the jet's liquid residue bridging short gaps, and not by mean fuel flow. The study is reframed around that memory and its time scale. Whether pulsing can beat a steady jet at lower fuel, where an equal-fuel steady jet may become too small, is an open option (see [experiments.md](experiments.md#where-a-stronger-result-could-come-from)).

## Gap

Searches in English and Chinese, last checked on 2026-10-09, found no published work combining pulsed or intermittent actuation with a liquid transverse jet for ODW initiation or stabilization, and none that measures how an ODW responds when its jet is switched off. The 2025 Chinese review of confined ODW initiation ([references.md](references.md) 24) lists no such work either. The search indexes reach to about mid-2026, so arXiv listings from July 2026 on should be checked by hand before submission. The adjacent work is:

- Continuous liquid-jet ODW control (Wang, Hu & Zhang, both papers below).
- Pulsed energy deposition for gas-phase ODW initiation (Jiang et al.). It shows pulsing can match continuous actuation at 2.3–6.5% of the power, and it defines f_cri. This is the methodology template.
- A continuous liquid jet holding an ODW in a confined combustor under sinusoidal inlet-pressure oscillation at 4 and 8 kHz (Wang, Hu & Zhang, arXiv:2605.27871, Sec. 3.2). The wave system stays phase-locked to the forcing inside a finite window of J and forcing amplitude, and is lost at large J. There the flow is unsteady and the jet steady; here the jet is unsteady and the flow steady.
- Bump-forced initiation, a fixed bump on the wedge that ignites the mixture at its stagnation point (Liu, arXiv:2609.02515). It is how kerosene ODWs are initiated in the Chinese shock-tunnel engine tests. It needs no fuel but cannot be switched off or adapted. The liquid pocket that anchors the front in step 2 of [experiments.md](experiments.md) acts like a fluidic bump, which a pulsed jet can turn on and off.
- A gas sweeping jet on the wedge (Fan et al., Combust. Flame 2024). It is the closest unsteady-jet work: the periodically redirected jet shortens initiation and holds it steadier than a steady jet. Its jet is never off, it is gaseous, and it has no switch-off or frequency threshold. A reviewer will raise it, so the paper must say how this work differs.
- ODW hysteresis (Liu et al., Combust. Flame 2018): the final front depends on its history in a wedge-angle sweep. It is the precedent for describing the front as having memory, here measured in time rather than in parameter space.

The Wang, Hu & Zhang group has steady jets in both an open and a confined geometry and has already forced the confined case with oscillating inflow. A pulsed-jet study is the natural next step for them, so the gap is likely to close; it should be checked again just before submission.

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
