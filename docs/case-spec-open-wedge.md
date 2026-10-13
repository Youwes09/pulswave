# Open-wedge baseline specification

Transcribed from Wang, Hu & Zhang, *Liquid-fueled oblique detonation waves induced by reactive and non-reactive transverse liquid jets*, Aerosp. Sci. Technol. 168 (2026) 111293, arXiv:2506.15247, Sections 2.1–2.3. Values this project had to choose are in [assumptions.md](assumptions.md).

## Geometry

- Single 27° wedge, standing in for the two-stage inlet (following Teng et al., the paper's ref. [27])
- Domain 0.25 m long and 0.1 m high, with the wedge leading edge at x = 0
- Jet, or on-wedge strip, at x = 0.05 m

## Inflow

The authors derive the inflow from shock relations for Mach 9 flight at 30 km, after two 10° forebody wedges.

- p1 = 2.855e4 Pa, T1 = 697.0 K, u1 = 2535.0 m/s
- n-heptane droplets distributed randomly in the air: 10 µm, 300 K, stoichiometric, 10 droplets per parcel
- Pre-evaporation neglected: the flight time to the shock (~0.05 ms) is short compared with the evaporation time (~0.5 ms)

## Boundaries

- Outflow: zero gradient for p, T and u (supersonic)
- Wall: slip; the boundary layer is neglected

## Jet

- Diameter 0.5 mm, normal to the wall
- Rosin–Rammler droplet sizes, mean 10 µm
- J = ρ_j u_j² / (ρ_2 u_2²), where state 2 is behind the wedge shock
- n-heptane jet: J = 0.1, 0.5, 1, 2 give u_j = 19.24, 43.01, 60.83, 86.02 m/s
- Water jet: J = 0.1, 0.5, 1 give u_j = 15.92, 35.60, 50.35 m/s
- Alternative trigger: an on-wedge strip of 0.5 mm diameter at the same position

## Mesh

Uniform grids of 0.15, 0.2, 0.4 and 0.8 mm (1.11e6, 6.25e5, 1.56e5 and 3.91e4 cells). The two finest agree. 0.2 mm is used for production runs.

## Models and numerics

- Chemistry: 44-species, 112-reaction n-heptane mechanism (Liu, Hewson, Chen & Pitsch 2004)
- Droplets: Abramzon–Sirignano evaporation, Pilch–Erdman breakup, Ranz–Marshall heat transfer (the paper); C_d = 0.424 for Re_p > 1000 is not in this paper but in the authors' solver paper, arXiv:2404.03170
- Gas: Sutherland viscosity
- Numerics: KNP fluxes, Gauss limited-linear spatial scheme, first-order Euler time stepping, CFL 0.3
- Condensed species tracked: C7H16 and H2O
- Solver: the authors' rhoCentralFoam-based two-phase solver on OpenFOAM v7 (arXiv:2404.03170). This project uses detonationFoam on OpenFOAM-8; see [solver.md](solver.md).

## Reported results

| Case | Outcome |
|---|---|
| Vapour inflow, no jet (Fig. 3a) | A secondary ODW forms near x = 0.05 m and turns the wedge shock into an ODW |
| Droplet inflow, no jet (Fig. 3b) | No ODW forms |
| Droplet inflow, J = 1 (Fig. 3c) | The shock the jet creates couples to combustion at the jet, and the main ODW follows |
| J = 0.1–0.3 | Weaker shock at the jet, not coupled. The jet enriches the mixture and low- and intermediate-temperature chemistry leads to an ODW downstream (about x = 0.08 m). The flame front fluctuates around x = 0.1 m. |
| J ≥ 0.4 | The jet triggers detonation directly, acting mainly as an obstacle. The paper calls J = 0.4 adequate for direct formation under these conditions; J = 0.1–0.3 also form an ODW, downstream. |
| J = 2 | The shock detaches to about x = 0.04 m, with a Mach reflection at the wall |
| Water jet at J = 0.1 | Cyclic and unstable |
| On-wedge strip | Reproduces the obstacle mechanism of high-J jets |

The paper's future work is breakup-model effects and a confined combustor; the confined combustor is arXiv:2605.27871. Neither paper mentions pulsed injection.
