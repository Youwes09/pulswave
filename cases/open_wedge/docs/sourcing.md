# open_wedge case: constant sourcing

Every numeric input used in the case files, traced to its origin.
PAPER = arXiv:2506.15247 (Wang/Hu/Zhang, open-wedge case) unless noted.
Section/quote given for each. NOT IN PAPER = no source in the paper;
value is an assumption, OpenFOAM default, or pipeline-test placeholder,
with rationale given.

## Domain / mesh (system/blockMeshDict)

| Value | Source |
|---|---|
| Domain 0.25 m x 0.1 m | PAPER, Sec 2.2: "The length of the computational domain is 0.25 m, and the height is 0.1 m" |
| 1250 x 500 cells, 0.2 mm | PAPER, Sec 2.3: mesh-independence study selects 0.2 mm as production mesh; cell counts back-calculated from domain size / 0.2 mm |
| Wedge angle 27 deg | PAPER, Sec 2.2: "a single wedge with a 27 deg angle" |
| Flat rectangle + rotated inflow (not sloped mesh) | NOT IN PAPER directly -- standard convention in wedge-induced ODW CFD, cross-checked against Guo et al. 2014, Liu et al. 2024, Guo et al. arXiv:2201.03934, Zhang et al. 2019 |

## Inflow BCs (0/U, 0/T, 0/p)

| Value | Source |
|---|---|
| p1 = 2.855e4 Pa | PAPER, Sec 2.2: "a pressure of p1 = 2.855 x 10^4 Pa" |
| T1 = 697.0 K | PAPER, Sec 2.2: "a temperature of T1 = 697.0 K" |
| \|U1\| = 2535.0 m/s | PAPER, Sec 2.2: "a velocity of u1 = 2535.0 m/s" |
| Ux = 2258.3, Uy = -1150.9 (27 deg decomposition) | NOT IN PAPER directly -- trigonometric decomposition of the stated speed/angle for the rotated-frame mesh convention |
| Droplet diameter 10 micron | PAPER, Sec 2.2: "a droplet diameter of 10 microns" |
| Droplet temperature 300 K | PAPER, Sec 2.2: "a temperature of 300 K" |
| Stoichiometric ratio unity | PAPER, Sec 2.2: "a stoichiometric ratio of unity" |
| Species mass fractions (C7H16/O2/N2/CO2/H2O: 0.02/0.228/0.752/0/0) | NOT IN PAPER -- paper specifies droplet-laden air with fuel vapor from evaporation, not a fixed premixed gas-phase mass fraction. These values only give the smoke-test mechanism a valid composition summing to 1.0. |

## Jet injection (system/topoSetDict, constant/sprayCloudProperties)

| Value | Source |
|---|---|
| Jet position x = 0.05 m | PAPER, Sec 2.2: "positioned 50 mm downstream of the wedge's leading edge" |
| Jet diameter 0.5 mm | PAPER, Sec 2.2: "a diameter of 0.5 mm" |
| Actual cut patch width 0.4 mm | NOT IN PAPER -- 0.5 mm is not an integer multiple of the 0.2 mm cell size; nearest achievable patch is 2 cells = 0.4 mm |
| u_jet = 60.83 m/s (J=1.0, C7H16) | PAPER, Sec 3: J = 1.0 corresponds to jet velocity 60.83 m/s |
| Mean droplet diameter 10 micron (R-R distribution) | PAPER, Sec 2.2: "average droplet diameter set to 10 micron" |
| R-R distribution exponent n = 3 | NOT IN PAPER -- spread exponent not stated; common literature value, matches OpenFOAM's aachenBomb default |
| R-R min/max (1 / 30 micron) | NOT IN PAPER -- bounds not stated; placeholder bracketing the 10 micron mean |
| massTotal = 3.31e-5 kg | NOT IN PAPER directly -- computed from liquid C7H16 density (~680 kg/m3) x u_jet x actual 0.4 mm x 2 mm patch cross-section x 1e-3 s duration |
| parcelsPerSecond = 7.5e7 | NOT IN PAPER as a rate -- paper states total parcel count "5x10^4 to 1x10^5" (Sec 2.2), each parcel = 10 real droplets; rate is mid-range count / controlDict endTime (1e-3 s) |
| Droplet temperature T0 = 300 K | PAPER, Sec 2.2 (same source as inflow droplet temperature) |
| B1 = 0.375, B2 = 0.2274 (PilchErdmanCoeffs) | NOT IN PAPER -- paper names "the Pilch-Erdman model" (Sec 2.1) without constants; values are the published Pilch & Erdman (1987) correlation constants, taken from PilchErdman.C's default member initializers in OpenFOAM-8 |
| rho0 = 680, Cp0 = 2240 (constantProperties) | NOT IN PAPER -- generic liquid n-heptane placeholders, to be overwritten from thermophysicalProperties/liquids once real property data exists |

## Model selection

Model *type* choices, each backed by a specific paper statement or
flagged as inferred:

| Model | Source |
|---|---|
| sphereDrag (particle force) | PAPER, Sec 2.1: sphere drag model, citing Liu/Mather/Reitz (1993) for Cd |
| patchInjection | NOT IN PAPER by class name -- inferred from the paper's wall-mounted transverse injector description (Sec 2.2) |
| RanzMarshall (heat transfer) | PAPER, Sec 2.1: "Nu = 2.0 + 0.6 Re_p^0.5 Pr^(1/3)", named "the Ranz-Marshall model" |
| liquidEvaporation (phase change) | NOT IN PAPER by class name -- paper describes (Sec 2.1) a quasi-steady Sherwood-correlation, Raoult's-law model; matched to LiquidEvaporation rather than LiquidEvaporationBoil, which adds unstated boiling behavior |
| none (atomization) | PAPER, Sec 2.2: "the Rosin-Rammler (R-R) distribution model is employed to substitute the primary atomization process" |
| PilchErdman (breakup) | PAPER, Sec 2.1: "the Pilch-Erdman model is utilized" |
| laminar (combustionModel, momentumTransport) | NOT IN PAPER directly -- inferred from no turbulence model being mentioned plus Sec 2.2: "given the thin boundary layer resulting from the high Reynolds number, its effect is neglected" |
| standardWallInteraction (droplet-wall) | NOT IN PAPER -- Eulerian wall is slip-reflecting but Lagrangian droplet-wall behavior isn't stated; OpenFOAM default used |
| dispersionModel none | NOT IN PAPER -- consistent with laminar momentumTransport (no turbulent KE field to disperse against) |

## Chemistry (constant/thermophysicalProperties, chemistryProperties)

| Value | Source |
|---|---|
| 44 species, 112 reactions (target, not yet in use) | PAPER, Sec 2.1: "a skeletal reaction mechanism comprising 44 species and 112 reactions", citing Liu, Hewson, Chen & Pitsch (2004). Not sourced yet -- see chemkin/README.md |
| 5 species, 1 reaction (in use: chemkin_smoketest/) | NOT IN PAPER -- OpenFOAM-8's aachenBomb tutorial mechanism, used only to prove the solver pipeline runs. Not comparable to the paper. |
| As = 1.67212e-6, Ts = 170.672 (Sutherland transport) | NOT IN PAPER -- generic coefficients, same as OpenFOAM's aachenBomb tutorial default. Paper specifies Sutherland's law (Sec 2.1) but gives no species-specific coefficients. |
| initialChemicalTimeStep = 1e-9 | NOT IN PAPER -- matched to controlDict's gas-phase deltaT so chemistry substeps aren't looser than the flow solver step |

## Not yet reconciled with the paper

- constant/reactions, speciesThermo derive from the 5-species
  smoke-test mechanism, not the paper's 44/112 mechanism.
- Species mass fraction fields (0/C7H16 etc.) reflect the smoke-test
  mechanism's species list, not the paper's composition.
- fvSchemes/fvSolution scheme choices (Euler, Gauss limitedLinear,
  KNP) are paper-sourced from Sec 2.2, but the divSchemes /
  laplacianSchemes / fvSolution keyword structure needed to run them
  was reverse-engineered from detonationFoam's C++ source, not stated
  by the paper.
- phaseChangeModel liquidEvaporation chosen by matching described
  physics, not read directly off the paper.
- sprayCloudProperties parcelsPerSecond, R-R n/min/max -- paper gives
  total parcel count range and mean diameter only.
- 0/ species mass fraction values (field structure is confirmed
  against aachenBomb, values are not) are smoke-test placeholders.
- OpenFOAM v7 (paper's solver) vs. v8 (this build) equivalence
  unverified.

## chemkinToFoam gotchas

Cost real debugging time; likely to recur with a different mechanism
file.

- chemkinToFoam's third argument ("transportProperties" by convention)
  is not raw Chemkin transport polynomial data. It's an OpenFOAM
  dictionary supplying generic Sutherland As/Ts coefficients via
  wildcard match, used because thermophysicalProperties specifies
  `transport sutherland`, not `transport polynomial`.
- The THERMO keyword in a Chemkin thermo file must be exactly
  `THERMO ALL` for OpenFOAM's parser; bare `THERMO` or lowercase
  `thermo` both fail. LLNL's mechanism ships with bare `thermo`.
- OpenFOAM's chemkinReader enforces exact fixed-column NASA-7
  positions (species name, phase flag, temperature ranges, card
  numbers 1-4 in column 80) more strictly than some other tools (e.g.
  Cantera). A file that parses elsewhere isn't guaranteed to parse
  here.
- multiComponentMixture requires a 0/Ydefault field even when every
  species has its own explicit 0/<name> file -- hePsiThermo demands it
  regardless of whether anything falls back to it.
- Coeffs subdicts in sprayCloudProperties (e.g. PilchErdmanCoeffs) can
  have individually mandatory keys with no lookupOrDefault fallback,
  even when the C++ class has default member values -- those defaults
  are overwritten by a mandatory lookup immediately after. Check each
  submodel's .C source for `.lookup(` vs. `.lookupOrDefault(`.