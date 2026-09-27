# Assumptions

Values the source papers do not state, and changes needed for this solver. Everything else follows arXiv:2506.15247 as transcribed in [case-spec-open-wedge.md](case-spec-open-wedge.md). The values are set in `pulswave/build.py` and `template/`.

## Domain and inflow

- **Frame:** the domain is aligned with the wedge surface. x runs along the wall from the leading edge, and the freestream enters at −27°. The freestream therefore crosses both the left patch (`inflow`) and the top patch (`upperBoundary`), and both carry the same fixed freestream state.
- **Depth:** the case is 2-D with a depth of 2 mm, one cell. Every mass flow is per 2 mm of depth.
- **Air:** dry, O2 0.232 and N2 0.768 by mass.
- **Premixed mixtures** (Guo cases and `crop_vapor`): n-C7H16 : O2 : N2 = φ : 11 : 41.36 by moles.

## Freestream droplets

- **Loading:** stoichiometric, AFR = 15.139. The fuel mass flow through each patch is ρ_air · u_n · L · depth / AFR, with ρ_air = p/(287 T).
- **Droplets:** 10 µm, 300 K, 10 droplets per parcel (fixed basis). These values are stated by the paper. The parcel rate follows from the mass flow, with a liquid density of 680 kg/m³.
- **Timing:** injection starts at t = 0 and lasts max(300 µs, end time).

## Jet

- **Jet width:** the paper's jet is D = 0.5 mm. On a 0.2 mm mesh the jet patch is two faces, which is 0.4 mm wide. The injected mass flow is the paper's, ρ_l · u_j · D · depth, so the mass and momentum flux per unit depth match the paper.
- **Velocity:** normal to the wall, at the paper's value for each J. J is defined against the post-shock state: 19.24, 43.01, 60.83 and 86.02 m/s for J = 0.1, 0.5, 1 and 2.
- **Droplet sizes:** Rosin–Rammler with a mean of 10 µm (the only value the paper gives), spread n = 3, range 1–30 µm. Mass basis, 7.21e8 parcels/s, 300 K.

## Spray models

The paper cites Abramzon–Sirignano evaporation, which OpenFOAM-8 does not provide. The spray settings follow the authors' published solver case (arXiv:2404.03170, github.com/MiaoYangFluid/detonationSprayFoam):

- `liquidEvaporationBoil` evaporation
- Pilch–Erdman breakup with B1 = 0.75 and B2 = 0.348
- Ranz–Marshall heat transfer with Bird correction
- `sphereDrag` (C_d = 0.424 above Re = 1000, as the paper states)
- explicit two-way coupling sources, which is the paper's PSI-CELL method

The paper does not specify droplet–wall interaction; `rebound` is used.

## Numerics

- **Stated by the paper and followed:** Kurganov (KNP) fluxes, limited-linear reconstruction, first-order Euler time stepping, Courant number 0.3, and a slip wall with no boundary layer or turbulence model.
- **Chemistry:** seulex ODE solver at its default tolerances, with an initial chemical step of 1e-9 s. It is checked against Cantera through chemFoam in [validation.md](validation.md).
- **Gravity:** (0, −9.81, 0). The cloud needs this field to exist, but gravity is negligible at these speeds.
- **Gas-only cases:** they keep one dormant injector (it starts at t = 1 s, so it never fires) because this solver fails with a floating-point exception when the injector list is empty or holds a near-zero mass flow.
