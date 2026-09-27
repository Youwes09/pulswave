# Validation record

Each check compares the setup against a known answer: theory, a published number, or a published case. The commands that produce each number are in [tools.md](tools.md).

## 1. Solver and chemistry

| Check | Reference | Result |
|---|---|---|
| Thermodynamic data, 44 species, 300–2500 K | Cantera | cp and h identical (0.000%) |
| Ignition at 1400 K, 2.8 atm, φ = 1 (chemFoam) | Cantera heat-release peak, 87.9 µs | T passes 1700 K at 84.8 µs |

Cantera ignition delays at 2.8 atm and φ = 1, used to interpret the runs: 1169, 87.9, 32.4, 6.7 and 1.2 µs at 1200, 1400, 1485, 1645 and 1900 K.

detonationFoam treats `thermo.he()` as the internal energy (`createFields.H:19`), so every case uses `energy sensibleInternalEnergy`. With `sensibleEnthalpy`, shocks come out about 15% too cold: the Guo φ = 1 post-shock temperature falls from 1454 K to 1222 K. Runs made before this correction are invalid.

## 2. Shock relations

| Case | Paper | Computed |
|---|---|---|
| Guo φ = 1 post-shock temperature | 1452 K | 1454 K |
| Guo φ = 0.2 post-shock temperature | 1601 K | 1603 K |

Derived values used elsewhere in this record:

| Quantity | Value |
|---|---|
| Engine inflow shock, stoichiometric vapour | 1485 K, 8.73° to the wall |
| Engine inflow shock, air | 1646 K, 10.24° to the wall |
| Chapman–Jouguet state, vapour at 1200 K and 2.8 atm | 1790 m/s, p/p1 = 5.0, 3163 K |

## 3. Premixed ODW on a 30° wedge (arXiv:2202.04987)

| | Paper | This work |
|---|---|---|
| φ = 1 initiation length | 19.8 mm, abrupt transition | 20.5 mm (T > 1.1 × post-shock) and 21.7 mm (heat-release peak), abrupt, at 16 µs |
| φ = 0.2 initiation length | 3.47 mm, smooth transition | 4.1 mm, smooth, steady |

## 4. Open wedge, vapour inflow (`crop_vapor`, paper Fig. 3a)

Wall values, steady between 70 and 85 µs:

| x | Paper | This work |
|---|---|---|
| 10 mm | 1452 K | 1481 K |
| 55 mm | 2295 K | 2345 K |
| 75 mm | 2928 K, 6.91 atm | 2990 K, 6.77 atm |

## 5. Open wedge, droplet inflow without jet (`crop_nojet`, paper Fig. 3b)

The paper reports about 1200 K near the wall, rising fuel vapour and no combustion. Over 60 µs the near-wall gas stays at 1110–1206 K, fuel vapour mass fraction 0.063–0.088, and no ignition.

## 6. Near-jet anchoring (`crop_jet`)

- After the startup transient, burning is anchored at x = 49.5 mm, with the upstream gas at about 1180 K and no CO2.
- Shock and reaction coincide up to about 10 mm off the wall.
- Peak pressure is 8.7 times the pre-jet value, above the Chapman–Jouguet ratio of 5.0.
- The 15 mm domain height is too low to show the main ODW.

## 7. Full J = 1 case (`paper_j1`, paper Fig. 3c)

The case is still running. See [reproduce.md](reproduce.md) for how its initial state differs from a clean build. Values below are at 90 µs.

**Wave structure.** The run shows the mechanism the paper reports for J = 1:
- A jet-induced ODW forms at the jet. Below 6 mm from the wall its shock foot has held at x = 49.7–52.1 mm for 55 µs.
- Burning follows the shock within 0.2–1.8 mm up to 38 mm from the wall.
- The main ODW has formed downstream and extends to x = 200 mm.
- Upstream of the jet the gas stays at about 1130 K with no CO2.
- The shock does not detach from the jet, which is the paper's J = 2 outcome.

**Near-wall streamline** from (0, 1 mm), compared with the paper's Fig. 3c profile:

| | Paper | This work |
|---|---|---|
| Before the jet | ~1200 K, C7H16 rising to ~0.1 | 1030–1130 K, C7H16 0.11 |
| At the jet | spike to >3000 K and ~22 atm | 2989 K, 33 atm (at 50 µs) |
| Behind the jet | cold (~700–1000 K) and fuel-rich (C7H16 0.5–0.8) | 400–960 K, C7H16 0.4–0.97 |

**Front height**, taken as the top of the region above 1900 K:

| x (mm) | 52 | 58 | 60 | 66 | 70 | 75 | 80 | 90 | 100 | 120 | 150 | 200 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Paper (100 µs), mm | 10.4 | 16.3 | 17.0 | 21.5 | 23.7 | 28.1 | 30.4 | 36.3 | 41.5 | 49.6 | 63.0 | 79.3 |
| This work (90 µs), mm | 8.9 | 14.7 | 16.3 | 20.1 | 22.5 | 24.9 | 27.3 | 30.9 | 34.1 | 41.9 | 49.5 | 48.5 |

- x = 52–70 mm: 0.7–2.0 mm below the paper and stationary. The paper values are read from its figure to about ±1 mm.
- x = 75–120 mm: 3–8 mm below the paper and rising by 0.4–0.8 mm per 10 µs.
- x ≥ 150 mm: the main ODW is still developing.

## Open differences

- The front near the jet sits 1–2 mm lower than the paper's. Candidate causes are inputs the paper does not state: the jet droplet size spread, droplets bouncing off the wall, and the 0.4 mm jet patch (see [assumptions.md](assumptions.md)).
- The upper front is still converging at 90 µs. Because the droplets were lost at the start, its effective development time is shorter than the paper's.
- Total-pressure loss and fuel use have not been computed yet. They are the baseline the pulsed study needs.
