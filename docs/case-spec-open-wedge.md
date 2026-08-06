# Case specification: Wang, Hu & Zhang (2025/2026) open-wedge baseline

Source: Wang, W., Hu, Z., Zhang, P. Liquid-fueled oblique detonation waves
induced by reactive and non-reactive transverse liquid jets. Aerosp. Sci.
Technol. 168 (2026) 111293. arXiv:2506.15247. All values transcribed
directly from Section 2.1-2.3 unless noted.

Fully specified, unlike the confined-combustor case (case-spec.md): no
schematic-only dimensions, no upper-wall ambiguity. Recommended as the
first reproduction/validation target before attempting the confined case.

## Geometry (Section 2.2)

- Single wedge, angle 27° (simplification of the two-stage inlet, per
  Teng et al., cited as ref [27])
- Domain length: 0.25 m
- Domain height: 0.1 m
- Wedge leading edge at domain origin (x = 0)
- Jet / on-wedge-strip location: x = 0.05 m (50 mm downstream of leading
  edge)

## Inflow conditions (Section 2.2)

Derived by the authors from shock relations for Mach 9 / 30 km altitude
ambient, post two 10° forebody wedges:

- Pressure p1 = 2.855e4 Pa
- Temperature T1 = 697.0 K
- Velocity u1 = 2535.0 m/s
- n-heptane droplets: randomly distributed in inflow air, diameter 10
  micron, temperature 300 K, stoichiometric ratio 1
- Droplet parcels: 5e4 to 1e5, 10 droplets per parcel
- Pre-evaporation over the flow's ~0.1 m travel to the OSW found
  negligible by the authors (flight time ~0.05 ms vs. evaporation time
  ~0.5 ms) -- stated justification, not an independent check.

## Boundary conditions (Section 2.2)

- Outflow: zero-gradient Neumann for p, T, u (flow is supersonic)
- Wall: slip-reflecting. Boundary layer explicitly neglected (thin at
  the stated Reynolds number, per the authors); no wall function used.

## Jet parameters (Section 2.2)

- Jet diameter: 0.5 mm (note: different from the confined-combustor
  paper's R_j = 5 mm radius -- these are two different papers/cases, do
  not conflate)
- Position: x = 0.05 m, normal to wedge surface
- Rosin-Rammler droplet size distribution, mean diameter 10 micron
- Momentum ratio J = rho_jet*u_jet^2 / (rho_2*u_2^2), rho_2/u_2 = post-
  wedge-OSW density/velocity
- Reactive (C7H16) jet velocities: J=0.1 -> 19.24 m/s, J=0.5 -> 43.01
  m/s, J=1.0 -> 60.83 m/s, J=2.0 -> 86.02 m/s
- Non-reactive (H2O) jet velocities: J=0.1 -> 15.92 m/s, J=0.5 -> 35.60
  m/s, J=1.0 -> 50.35 m/s
- Alternative control: on-wedge strip, same position, diameter 0.5 mm

## Mesh (Section 2.3)

Four resolutions tested: 0.15, 0.2, 0.4, 0.8 mm, giving cell counts of
1.11e6, 6.25e5, 1.56e5, 3.91e4 respectively (for the full 0.25 x 0.1 m
domain). 0.15 mm and 0.2 mm agreed closely; 0.2 mm selected for
production runs as the accuracy/cost balance.

This confirms the ~625k-cell figure used as a sanity check in
cases/baseline/README.md -- it is this paper's actual reported cell
count at 0.2 mm, not an estimate.

## Governing equations and sub-models (Section 2.1)

Identical to the confined-combustor case (case-spec.md): same 44-species
112-reaction n-heptane mechanism (Liu, Hewson, Chen & Pitsch 2004),
Abramzon-Sirignano evaporation, Pilch-Erdman breakup, Ranz-Marshall heat
transfer, C_d = 0.424 (Re_p > 1000), Sutherland viscosity, KNP shock
capturing, first-order Euler time integration, Gauss-limited Linear
spatial scheme, CFL < 0.3. Two condensed species tracked: C7H16, H2O.

## Solver

Same in-house solver, rhoCentralFoam framework, OpenFOAM v7. Same v7/v8
discrepancy noted in case-spec.md applies here.

## Regimes reported (Section 3.1-3.2, Fig. 3-7)

- Pure vapor/air inflow, no jet: OSW forms, secondary ODW (SODW) forms
  near x = 0.05 m, transitions wedge-induced OSW to ODW.
- Pure droplet/air inflow, no jet: ODW fails to form (droplets evaporate,
  no coupled heat release).
- Droplet/air inflow + reactive jet, J = 1: ODW forms, jet-induced OSW
  couples directly to combustion at the jet location.
- J = 0.1: weaker OSW, not directly coupled to combustion; jet raises
  local fuel fraction, promotes low/intermediate-T chemistry, transition
  to ODW occurs downstream (~x = 0.08 m). Flame front reported unsteady,
  fluctuating around x = 0.1 m (Fig. 5).
- J = 0.5, 1.0, 2.0: jet-induced OSW strong enough to trigger detonation
  directly at/near the jet; jet acts primarily as physical obstacle
  rather than participating chemically.
- J = 0.2, 0.3: behave like J = 0.1 (chemistry-mediated). J = 0.4:
  behaves like J = 0.5 (direct trigger). Authors identify J = 0.4 as the
  minimum sufficient for reliable ODW formation under these inflow
  conditions.
- H2O (non-reactive) jet at low J (0.1) produces a more unstable,
  cyclic flow field (NDW forms, explosion point emerges/disappears,
  repeats) than the C7H16 case at the same J.
- On-wedge strip (R = 0.25 mm, i.e. same 0.5 mm diameter as jet) at high
  J closely reproduces the physical-blocking mechanism seen with H2O and
  high-J C7H16 jets.

## Note on future-work statement

Section 4 (Conclusions) explicitly lists, as future work: (1) effect of
different droplet breakup models on droplet distribution/penetration,
and (2) extending to a confined combustor to address fuel loss, thrust
potential, and formation control -- (2) is what the companion paper
(case-spec.md, arXiv:2605.27871) does. No mention of pulsed/intermittent
jet actuation as future work in either paper.