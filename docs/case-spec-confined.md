# Case specification: Wang, Hu & Zhang (2026) confined-combustor baseline

Source: Wang, W., Hu, Z., Zhang, P. Liquid-fueled Oblique Detonation
Stabilized by a Transverse Jet. arXiv:2605.27871. All values transcribed
directly from Section 2.1-2.3 and Fig. 1/3 unless noted.

## Geometry (Section 2.2, Fig. 1)

- Ramp angle: 25°, inflow Mach 9
- Two 12.5° forebody compression stages ahead of computational domain
- Jet location: 50 mm downstream of combustor lip
- Jet radius R_j: 5 mm, normal to wall
- Domain lengths (Fig. 1b): upstream wall 110 mm, far-field/inlet height
  132 mm, outflow height 40 mm, lower wall 300 mm, downstream outflow
  height 60 mm
- Origin at ramp leading edge, x downstream, y normal to lower wall

Fig. 1(b) is a schematic; the values above are the only explicit lengths
given. No other dimension is stated in the paper.

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

In-house two-phase solver, rhoCentralFoam framework, **OpenFOAM v7**.
pulswave targets OpenFOAM 8 (detonationFoam public repo). Not verified
to be numerically equivalent.

## Mesh (Section 2.3)

Grid-independence study at 0.2/0.3/0.4 mm, all with the above mechanism.
0.3 mm used for production runs.

## Open items

1. Fig. 1(b) dimensions are schematic-derived, not a dimensioned drawing.
2. u_j not given directly; must be back-calculated from target J.
3. Air composition not stated; standard 21/79 O2/N2 assumed.
4. OpenFOAM v7 vs v8, see Solver above.
