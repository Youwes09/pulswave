# Confined-combustor baseline specification

Transcribed from Wang, Hu & Zhang, *Liquid-fueled Oblique Detonation Stabilized by a Transverse Jet*, arXiv:2605.27871, Sections 2.1–2.3 and Figs. 1 and 3.

## Geometry (Section 2.2, Fig. 1)

- Ramp angle: 25°, inflow Mach 9
- Two 12.5° forebody compression stages ahead of computational domain
- Jet location: 50 mm downstream of combustor lip
- Jet radius R_j: 5 mm, normal to wall
- Domain lengths (Fig. 1b): upstream wall 110 mm, far-field/inlet height
  132 mm, outflow height 40 mm, lower wall 300 mm, downstream outflow
  height 60 mm
- Origin at ramp leading edge, x downstream, y normal to lower wall

Fig. 1(b) is a schematic. The lengths above are the only ones the paper gives.

## Inflow / BCs (Section 2.2)

- Two-phase C7H16/air, premixed
- Combustor-entrance T = 814.4 K, u = 2466 m/s
- Steady inlet pressure p0 = 1.963e5 Pa
- Oscillatory: p_in(t) = p0[1 + A_p sin(2*pi*N*t/dt)], dt = 1 ms,
  N = 4 or 8, A_p in {0.1, 0.3, 0.5}
- Jet droplets: Rosin-Rammler, mean diameter 10 micron
- J = rho_j*u_j^2 / (rho_inf*u_inf^2), set via jet velocity u_j
- Reported J sweep (Fig. 3): 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.5, 1.0, 2.0

## Regime map (Section 3.1.1, Fig. 3)

| J | Regime |
|---|---|
| 0.01 | non-ignited |
| 0.02-0.03 | local OSW-NDW-SSW, no ODW branch |
| 0.04-0.5 | standing OSW-ODW-NDW-SSW |
| 1.0 | wall-coupled OSW-ODW-Mach-stem |
| 2.0 | loss of stabilization |

## Sub-models (Section 2.1)

- Chemistry: 44-species, 112-reaction n-heptane mechanism (Liu, Hewson,
  Chen & Pitsch, Combust. Flame 137 (2004) 320-339)
- Evaporation: Abramzon-Sirignano
- Breakup: Pilch-Erdman
- Drag: C_d = 0.424, Re_p > 1000
- Heat transfer: Ranz-Marshall
- Viscosity: Sutherland
- Shock capturing: Kurganov-Noelle-Petrova
- Time integration: first-order Euler, CFL < 0.3
- Spatial scheme: Gauss-limited Linear

## Solver

The authors' rhoCentralFoam-based two-phase solver on OpenFOAM v7. This project uses detonationFoam on OpenFOAM-8.

## Mesh (Section 2.3)

Grid study at 0.2, 0.3 and 0.4 mm. 0.3 mm is used for production runs.

## Not stated by the paper

- The upper-wall shape, and any dimension beyond those in Fig. 1(b)
- The jet velocity, which must be back-calculated from J
- The air composition
