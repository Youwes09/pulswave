# Assumptions

Values the source papers do not state, and changes needed for this solver. Everything else follows arXiv:2506.15247 as transcribed in [case-spec-open-wedge.md](case-spec-open-wedge.md). The values are set in `pulswave/build.py` and `template/`.

## Domain and inflow

- **Frame:** the domain is aligned with the wedge surface. x runs along the wall from the leading edge, and the freestream enters at −27°. The freestream therefore crosses both the left patch (`inflow`) and the top patch (`upperBoundary`), and both carry the same fixed freestream state.
- **Depth:** the case is 2-D with a depth of 2 mm, one cell. Every mass flow is per 2 mm of depth.
- **Air:** dry, O2 0.232 and N2 0.768 by mass in the freestream spray cases. The premixed cases (`premixed()`, n-C7H16 : O2 : N2 = φ : 11 : 41.36 by moles) and `theory.AIR` correspond to O2 0.233; the 0.4% difference in O2 is below every comparison made with them.
- **Premixed mixtures** (Guo cases and `crop_vapor`): n-C7H16 : O2 : N2 = φ : 11 : 41.36 by moles.

## Freestream droplets

- **Loading:** stoichiometric, AFR = 15.139. The fuel mass flow through each patch is ρ_air · u_n · L · depth / AFR, with ρ_air = p/(287 T).
- **Droplets:** 10 µm, 300 K, 10 droplets per parcel (fixed basis). These values are stated by the paper. The parcel rate follows from the mass flow, with a liquid density of 680 kg/m³.
- **Timing:** injection starts at t = 0 and lasts max(300 µs, end time).

## Jet

- **Jet width and mass flow:** the paper's jet is D = 0.5 mm and states no mass flow. The injected mass flow is chosen as that of a solid liquid slot, ρ_l · u_j · D per unit depth (41.4 g/s per 2 mm at J = 1). On a 0.2 mm mesh the jet patch is two faces, 0.4 mm wide, carrying that mass flow at the paper's velocity, so mass and momentum per unit depth are those of the 0.5 mm jet and the momentum flux per unit area is 1.25 times the nominal value. J is quoted by velocity, as in the paper. On the 0.15 mm mesh the patch is three faces (0.45 mm), a factor 1.11. `--half-width` keeps the per-area flux; `--jet-scale F` multiplies it by F at the same velocity.
- **Velocity:** normal to the wall, at the paper's value for each J. J is defined against the post-shock state: 19.24, 43.01, 60.83 and 86.02 m/s for J = 0.1, 0.5, 1 and 2.
- **Droplet sizes:** Rosin–Rammler with a mean of 10 µm (the only value the paper gives), spread n = 3, range 1–30 µm, 300 K: the spread and range are chosen. Parcels are injected on a mass basis (equal mass per parcel), so the distribution applies by mass and the number-mean droplet diameter is below 10 µm.
- **Jet parcel rate:** 7.21e8 parcels/s at J = 1 (`JET_PPS`), scaled with the jet mass flow for other settings. This is a chosen value whose origin was not recorded; it gives about 160 droplets of 10 µm per parcel, against the 10 per parcel the paper states for the freestream spray. It is well below the 2.1e9 parcels/s solver limit.

## Spray models

The paper cites Abramzon–Sirignano evaporation, which OpenFOAM-8 does not provide. The spray settings follow the authors' published solver case (arXiv:2404.03170, github.com/MiaoYangFluid/detonationSprayFoam):

- `liquidEvaporationBoil` evaporation
- Pilch–Erdman breakup with B1 = 0.75 and B2 = 0.348
- Ranz–Marshall heat transfer with Bird correction
- `sphereDrag` (C_d = 0.424 above Re = 1000, as in arXiv:2404.03170 Eq. 2.11 and arXiv:2605.27871)
- explicit two-way coupling sources, which is the paper's PSI-CELL method

The paper does not specify droplet–wall interaction; `rebound` is used, as in the authors' public case.

## Numerics

- **Stated by the paper and followed:** Kurganov (KNP) fluxes, limited-linear reconstruction, first-order Euler time stepping, Courant number 0.3, and a slip wall with no boundary layer or turbulence model.
- **Chemistry:** seulex ODE solver at its default tolerances, with an initial chemical step of 1e-9 s. It is checked against Cantera through chemFoam in [validation.md](validation.md).
- **Gravity:** (0, −9.81, 0). The cloud needs this field to exist, but gravity is negligible at these speeds.
- **Gas-only cases:** they keep one dormant injector (it starts at t = 1 s, so it never fires) because this solver fails with a floating-point exception when the injector list is empty or holds a near-zero mass flow.
