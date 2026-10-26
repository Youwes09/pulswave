# Experiments

> Working notes from the runs. Where they differ from the manuscript, the manuscript holds.

The jet-off and pulsed-jet questions are screened in reduced domains ("boxes"), and the grid check and the follow-up options in a smaller crop around the jet. A setting is run on the full domain only once a box shows it works.

## Ladder

| Step | Case | Purpose | Status |
|---|---|---|---|
| 0 | Theory and full-run measurements | Timescales that bound the hold time and the frequency range | done |
| 1 | `box_small` (90 × 35 mm), `box_large` (120 × 45 mm) | Continuous J = 1 in each box, checked against the settled `paper_j1` front near the jet | done: `box_large` chosen |
| 2 | Jet-off branch of `box_large` at 70 µs | Hold time Δt: how long the jet-induced ODW stays anchored after injection stops | done, to 130 µs |
| 2a | Jet-off branch with droplets removed at the wall (`escape`) instead of `rebound` | Checks whether Δt depends on the wall liquid reservoir, which the paper does not specify | stopped at 80.9 µs: the pocket barely touches the wall, and the wall model also changes the upstream state |
| 2b | Jet-off branch with all jet liquid deleted at 70 µs (`--drop-jet-liquid`) | Gas-dynamic hold time without the liquid pocket; compared with step 2, it separates the two anchors | stopped at 90 µs, answered: base retreats 2.3× sooner without the liquid |
| 2c | `large_off` at 95 µs with the jet on again (`--jet-on`), to 130 µs | Recovery rate of the retreated base; together with step 2, the net drift per pulse cycle | done, to 130 µs |
| 2d | `large_off_long`: `large_off` continued from 130 to 200 µs | Does the jet-off front eventually fail, or settle at a new position? | done: the detonation still stands at 200 µs (130 µs off) but its base keeps creeping downstream; it neither fails nor settles. `large_half_long` is therefore not run |
| 3 | Pulsed branches of `box_large` at 70 µs | Frequency and duty-cycle sweep at peak J = 1. `large_f40k`: 40 kHz, 50% duty, three cycles to 145 µs. `large_f80k`: 80 kHz, 50% duty, to 120 µs, continued to 145 µs as `large_f80k_long`. `large_f20k`: 20 kHz, 50% duty (25 µs off, longer than the retreat delay), one full off/on cycle to 145 µs. `large_f80k_q`: 80 kHz, 25% duty (9.4 µs off), to 145 µs | `large_f40k` done: control-level performance at half the jet fuel. `large_f80k` and `large_f80k_long` done: control-level performance verified at 125–145 µs. `large_f20k` done: excursion 3.8 mm, inside the prediction, with no recovery within the 25 µs on-phase and recovery 8% below the control; `large_f80k_q` deferred; its crop version is option A (step 5) |
| 3a | `large_half`: `box_large` at 70 µs with a continuous jet at half the velocity (30.4 m/s, J = 0.25), to 145 µs | Same mean jet fuel as a 50% duty pulse: is pulsing better than a weaker continuous jet? J = 0.25 is below the paper's J ≥ 0.4 for direct initiation, in its regime where the jet only enriches the mixture | done to 145 µs: holds the base no better than no jet, as the paper's J = 0.1–0.3 regime predicts; recovery above the control. Its front slides downstream at 3–15 mm (0.06–0.1 mm/µs), faster than the jet-off front at 9 mm. `large_half_long` (145 to 200 µs) queued 2026-10-09: does the slide continue towards the paper's low-J mode, initiation about 80 mm downstream? |
| 3b | `large_narrow`: `box_large` at 70 µs with a continuous jet of half the width (one wall face instead of two) at full velocity (J = 1), to 145 µs | Same mean jet fuel as a 50% duty pulse, at the pulse's J. It keeps J = 1 and halves the mass flow, where `large_half` keeps the mass flow per face and halves J. Two confounds: the 0.2 mm jet is one cell wide, and it uses `coneInjection` instead of the `patchInjection` of the two-face jet | done: holds the base within 0.8 mm of the control at 3 mm to 120 µs, then drifts to 2.2 mm behind at 145 µs; control-level recovery |
| 4 | `crop_grid`, `crop_grid_fine` (100 × 25 mm crops) and their jet-off branches `crop_grid_off`, `crop_grid_fine_off` | Grid check of the memory at 0.2 and 0.15 mm; `crop_grid_off` against `large_off` also checks the crop | done: at 3 mm the grids agree within 0.1 mm and crop and box within 0.2 mm over 40 µs after switch-off ([result](#result-2026-10-10)) |
| 5 | Option A: `crop_grid_f80k_q` (80 kHz, 25% duty). Option B: `crop_grid_d1` (1 mm jet) and `crop_grid_d1_off` | Can pulsing at full J cut the jet fuel by 75% and still hold the front? Does the memory scale with jet width? See [below](#where-a-stronger-result-could-come-from). `crop_grid_quarter` (steady quarter-fuel jet) was dropped on 2026-10-09: it could not be an equal-J comparison | done (`crop_grid_d1_off` stopped at 80 µs) |
| 6 | `paper_j1` branches | Full-domain confirmation at the best one or two settings, with total-pressure loss and fuel use | deferred: the box matches `paper_j1` near the jet and on the x = 100 mm plane, so this is argued as a limitation unless a reviewer requires it |

Every branch restarts from a save of its parent case (`python -m pulswave branch`) rather than from a mapped state, so the droplet cloud carries over. Branches of the same parent start at the same time, so they share the same liquid inventory. The continuous parent run past the branch time is the control, so any remaining drift of the parent front is separated from the effect of the branch.

## Step 0: timescales

All values come from `paper_j1` and were checked across the 85, 90 and 95 µs saves (`python -m pulswave nearjet`), and against Cantera (`python -m pulswave theory timescales`).

| Quantity | Value |
|---|---|
| Near-wall gas upstream of the jet | 1134 K, 2.75 atm, 2083 m/s (Mach 3.4), C7H16 0.093 |
| Its ignition delay | 2385 µs, against 24 µs to reach the jet |
| Shock at the jet foot, 1–4 mm from the wall | pressure ratio 6.5–8.5, foot fixed at x = 49.7–51.5 mm across all three saves |
| Ignition delay behind that shock (frozen state 1920–2150 K) | 0.13–0.44 µs |
| Gas speed through the first 20 mm behind the front, 3–15 mm from the wall | 1100–1800 m/s (11–18 µs) |
| Fuel-rich wall layer behind the jet (C7H16 > 0.2, y < 1 mm) | x = 50–182 mm, 748 K, 3.7 atm, 703 m/s, C7H16 0.45, O2 0.013 |
| Subsonic part of that layer | x = 50–65 mm, 157 m/s |
| Jet liquid within 30 mm of the jet | 4.1 mg in 68,000 parcels (median 5.2 µm) |

The gas approaching the jet cannot ignite on its own within the domain, so the detonation depends entirely on the shock the jet creates. Once that shock forms, ignition is effectively immediate. Once the jet stops, the front is lost when that shock decays.

Two timescales bound the hold time:

- **Lower bound, about 10–20 µs:** the hot gas behind the front is replaced this quickly.
- **Upper bound, about 100–200 µs:** the jet leaves a reservoir that lingers this long. It has two parts: the subsonic pocket (15 mm at 157 m/s, about 95 µs) and the fuel-rich layer (130 mm at about 700 m/s, about 190 µs).

For a duty cycle D, the off-time is (1 − D)/f, so the jet must switch back on within Δt: f ≥ (1 − D)/Δt. At 50% duty this gives roughly 2.5–50 kHz. This range is our estimate. The only comparable number in the literature is the 8.5–9.4 kHz critical frequency of Jiang et al. (arXiv:2508.08943), for pulsed energy deposition in premixed H2/air at Mach 7, which is a different actuator and mixture.

## Step 1: box check

Both boxes start from uniform freestream. The validated `paper_j1` run started from a mapped, developed state (see `docs/reproduce.md`), so the boxes are compared with its settled front, not at equal times. Shock x position [mm] per height above the wall (`python -m pulswave wave`):

| Height | `box_small` 65 µs | `box_large` 50 µs | `box_large` 60 µs | `box_large` 70 µs | `paper_j1` 95–100 µs |
|---|---|---|---|---|---|
| 1–4 mm | 49.7–51.5 | 49.9–51.5 | 49.9–51.5 | 49.9–51.5 | 49.7–51.5 |
| 9 mm | 53.3 | 53.9 | 53.5 | 53.1 | 52.4 |
| 12 mm | 56.1 | 57.1 | 56.5 | 55.9 | 55.0 |
| 15 mm | 60.1 | 61.7 | 60.5 | 59.7 | 58.4 |
| 18 mm | 65.1 | 67.9 | 65.7 | 64.5 | 62.6 |
| 22 mm | 73.7 | 83.1 | 74.9 | 72.5 | 69.4 |

- At the jet (1–4 mm), both boxes hold the `paper_j1` position from 35 µs onward.
- The two boxes agree within 0.4 mm at equal times, so the box size does not affect the front up to 26 mm.
- Above 9 mm the box front still approaches `paper_j1` by 0.2–1 mm per 5 µs at 70 µs, from a cold start.
- The `paper_j1` front at 30–34 mm sits at x = 86–97 mm, at or beyond the end of `box_small`, so only `box_large` can hold the upper front.

`box_large` at 70 µs (`python -m pulswave nearjet`) against `paper_j1`:

| Quantity | `box_large` 70 µs | `paper_j1` 95 µs |
|---|---|---|
| Near-wall gas upstream of the jet | 1156 K, 2.74 atm, 2081 m/s, C7H16 0.086 | 1134 K, 2.75 atm, 2083 m/s, C7H16 0.093 |
| Subsonic part of the fuel-rich wall layer | x = 50–63 mm, 167 m/s | x = 50–65 mm, 157 m/s |
| Jet shock at 3 mm | x = 50.9 mm | x = 50.9 mm |
| Outflow minimum Mach | 1.74 | – |

`box_large` is used from here on. `box_small` was stopped at 66.7 µs. Both boxes run at about 35 min per simulated µs on 8 cores.

## Step 2: jet off

`large_off` restarts `box_large` at 70 µs with the jet stopped. `large_off_escape` does the same but removes droplets that reach the wall. `box_large` is the jet-on control.

The tables of steps 2, 2b, 2c and the cycle notes of step 3 were recorded with the earlier largest-rise tracker. Re-run with the current tracker (2026-10-09), detonation base x [mm] at 3 mm after switch-off:

| After switch-off (µs) | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `large_off`, 3 mm | 50.7 | 50.7 | 50.9 | 51.3 | 51.9 | 52.7 | 53.3 | 53.9 | 54.5 | 55.1 | 55.7 | 56.3 | 56.7 |
| `large_off`, 9 mm | 52.9 | 52.9 | 52.7 | 52.9 | 53.1 | 53.5 | 53.9 | 54.1 | 54.5 | 54.9 | 54.9 | 54.9 | 54.9 |
| `large_off_dry`, 3 mm | 50.7 | 51.1 | 52.5 | 53.9 | 55.3 | | | | | | | | |

The control holds 50.7 mm at 3 mm and 52.3–51.9 mm at 9 mm over 95–145 µs. At 3 mm the base holds for about 10 µs and then retreats at 0.12–0.13 mm/µs (20–60 µs after switch-off). Without the jet liquid it retreats at once, at about 0.28 mm/µs, and reaches 53.9 mm 15 µs after switch-off against 35 µs with the liquid (2.3 times sooner). The 0.16–0.2 mm/µs below is the old tracker's value at 1 mm, a height no longer used.

Earlier record, shock x position [mm] (`wave`, old tracker):

| Height | Jet on, 80 µs | Jet off, 75 µs | Jet off, 80 µs | Jet off, 85 µs |
|---|---|---|---|---|
| 1 mm | 49.9 | 49.9 | 50.1 | 50.7 |
| 2 mm | 50.3 | 50.3 | 50.5 | 51.1 |
| 3 mm | 50.9 | 50.9 | 51.1 | 51.5 |
| 4 mm | 51.5 | 51.5 | 51.7 | 52.1 |
| 9–26 mm | 52.9–80.5 | as jet on | as jet on | as jet on, within 0.4 |

Jet off, the jet-foot shock moves downstream at about 0.05 mm/µs, while the detonation above 6 mm stays in place. The subsonic pocket behind the jet moves from x = 50.1–63.1 mm to x = 51.3–63.9 mm. On the x = 100 mm plane, recovery is 0.139 with the jet off at 85 µs, against 0.140 with the jet on at 80 µs.

### Update: 35 µs after switch-off, and step 2b

Shock x position [mm] at 1 mm and 9 mm height, against time after switch-off. The jet-on control holds 49.9 and 53.1.

| After switch-off | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 µs |
|---|---|---|---|---|---|---|---|---|
| Step 2, 1 mm | 49.9 | 49.9 | 50.1 | 50.7 | 51.5 | 52.3 | 53.1 | 54.1 |
| Step 2, 9 mm | 53.1 | 53.1 | 52.9 | 53.1 | 53.3 | 53.7 | 54.1 | 54.3 |
| Step 2b, 1 mm | 49.9 | 50.7 | 52.3 | 54.1 | | | | |
| Step 2b, 9 mm | 53.1 | 53.1 | 53.1 | 53.9 | | | | |

- There is no abrupt loss of the front. With the jet off, the base of the front retreats downstream while the detonation above it barely moves: at 15 mm it stays at 59.7–60.1 mm over 35 µs. By 35 µs (step 2) or 15 µs (step 2b), the 1–6 mm part has straightened into one front at about x = 54 mm.
- In step 2 the base holds for about 10 µs, then retreats at about 0.16–0.2 mm/µs. The fuel-rich layer now starts at x = 60.1 mm instead of 50.1 mm, and the liquid pocket still holds 2877 µg at 105 µs.
- In step 2b, without the jet liquid, the base retreats at once and reaches x = 54 mm 2.3 times sooner. The vapour layer the jet left still holds the front at first.
- The x = 100 mm plane is unaffected at first: recovery 0.122 (step 2, 105 µs) and 0.139 (step 2b, 85 µs).

So the hold time is not a single blow-off time. It is set by how far the base retreats while the jet is off, against how fast it returns once the jet is back on. Step 2c measures the return.

### Step 2c: jet back on, and step 2 to 55 µs off

Shock x position [mm]. `large_reon` restarts `large_off` at 95 µs with the jet on again.

| Time | 1 mm, on again | 1 mm, still off | 3 mm, on again | 3 mm, still off | 9 mm, both |
|---|---|---|---|---|---|
| 95 µs | 52.3 | 52.3 | 52.7 | 52.7 | 53.7 |
| 100 µs | 52.9 | 53.1 | 53.5 | 53.5 | 54.1 |
| 105 µs | 52.7 | 54.1 | 53.9 | 54.1 | 54.3 |
| 110 µs | 50.5 | 54.7 | 54.1 | 54.7 | 54.5 on, 54.7 off |

- Within 5 µs of the jet returning, the fuel-rich layer and the subsonic pocket re-form at the jet (x = 50.1 mm, against 57.9 mm with the jet still off).
- A new jet shock forms at 1 mm 15 µs after the jet returns, at 50.5 mm. It is still weak: a pressure ratio of 4.1, against about 8.5 with the jet on continuously. At 3–6 mm the retreat slows but has not reversed after 15 µs. Recovery builds from the wall upward and takes longer than 15 µs.

With the jet still off at 125 µs, 55 µs after switch-off:

- The detonation still stands (pressure ratio 33 at 9 mm), with its base at x = 56.5 mm.
- The liquid pocket has broken up: 977 µg, against 2877 µg at 105 µs. The subsonic wall region now spans x = 65.5–95.1 mm.
- The upper front moves upstream: at 26 mm it goes from 79.3 mm (100 µs) to 75.1 mm (125 µs). The detonation is getting steeper.
- Recovery on the x = 100 mm plane falls from 0.140 (jet on) to 0.122 (105 µs) and 0.086 (125 µs).

At 130 µs, the end of both runs (shock x [mm]):

| Height | Jet on again since 95 µs | Jet off since 70 µs | Jet on, 80 µs |
|---|---|---|---|
| 1 mm | 50.5 | 56.9 | 49.9 |
| 3 mm | 56.1 (weak, 3.4×) | 56.9 | 50.9 |
| 9 mm | 53.9 | 55.1 | 52.9 |
| 15 mm | 58.5 | 59.5 | 59.1 |
| 26 mm | 72.3 | 72.9 | 80.5 |

The step 2c values above come from the earlier largest-rise tracker, which follows the leading shock. The current tracker (see [Verified performance](#verified-performance)) requires burning behind the rise. At 3 mm it agrees (55.9 mm at 130 µs). At 1–2 mm it skips the re-formed jet shock, which has no burning behind it, and finds the first burning 54–62 mm downstream, beyond the re-formed liquid pocket (`scripts/checks/tracker_compare.py`). Statements about the jet shock at 1–2 mm below therefore refer to the shock, not to the detonation base.

After 35 µs back on, the wall shock is re-established at 1–2 mm, the detonation at 9 mm is 1.2 mm ahead of the jet-off run, and the 3–6 mm region is still weak and retreated. In both runs the front at 22–26 mm moved 7–9 mm upstream between 100 and 130 µs. The jet-on control had stopped at 80 µs, while the box front was still converging upstream towards `paper_j1` (69.4 mm at 22 mm, 77.1 mm at 26 mm), so this upper drift cannot yet be attributed to the jet. `box_large` was therefore continued from 80 µs to 145 µs as the control for steps 2, 2c and 3.

Total-pressure loss on that plane comes mostly from the detonation itself, not from the jet. With the jet off, recovery falls as the upper front moves upstream and steepens. Whether that steepening is caused by removing the jet, or is the box front still converging, is open until the extended control is compared. Until then a pulsed jet is not assumed to lower total-pressure loss, and the fuel saving is the clearer benefit.

The front is held by the liquid the jet left, not by the jet itself. Liquid injected during the last 10 µs forms only a 0.6 mm column, since the jet speed is 60.8 m/s. The accumulated cloud stays at 3.1 mg (`nearjet`: 3107 µg at 80 µs, 3123 µg at 85 µs). That cloud has cooled its own gas pocket:

| Near the jet (x = 50–80 mm, y < 3 mm) | Jet off, 85 µs | Jet on, 80 µs |
|---|---|---|
| Liquid | 3123 µg, d 5.0 µm | 3522 µg, d 5.8 µm |
| Droplet temperature | 399 K | 382 K |
| Gas temperature at the droplets | 418 K | 410 K |
| Gas C7H16 mass fraction at the droplets | 0.62 | 0.59 |
| Liquid in gas above 800 K | 0% | 0.8% |

The droplets are within 20 K of the surrounding gas, which is 60% fuel vapour by mass. Their evaporation has almost stopped: between 75 and 95 µs the liquid at x = 49.5–80 mm, y < 3 mm stays at 3089–3137 µg while breakup reduces its mass-weighted diameter from 5.6 to 4.2 µm (`pocket`), so evaporation removes less than 2% in 20 µs, a depletion time above 1 ms. For comparison, arXiv:2506.15247 estimates about 0.5 ms for a 10 µm droplet in the 697 K inflow, about 125 µs for 5 µm by the d² law. (An earlier note here gave a 700–900 µs depletion time and about 30 µs for an isolated droplet; neither was traceable to a calculation.) Averaged over the region (x = 49.5–80 mm, y < 3 mm), the liquid volume fraction is 2.5% and the mass loading about 8 kg of liquid per kg of gas (`python -m pulswave pocket`). The liquid is not spread over that region, however: it sits in 194 cells next to the wall, where it is about 30% of the volume and 20 times the gas mass. That is far outside the dilute-spray assumption behind the point-particle model, which treats each parcel as a point in a gas-filled cell. The pocket is in effect a wall film represented by parcels, so the hold time it produces is the least certain result of the study.

The slow evaporation follows from the local state and is not a solver fault. At the pocket's conditions (droplet 399 K, gas 418 K and 4.45 atm, gas C7H16 0.62), the n-heptane vapour pressure is 2.13 bar (NIST Antoine fit) and the surface mass fraction is 0.76. That gives a Spalding mass-transfer number B_M = 0.59, and a d²-law lifetime of about 230 µs for a 5 µm droplet. A droplet stays cold and slow to evaporate for as long as its pocket stays sealed off from hot gas. How long that lasts depends on mixing into the pocket. The simulation, like the paper, is laminar with a slip wall and no turbulence model, so that mixing is only what the 2D grid resolves.

arXiv:2506.15247 (Sec. 3, J = 1 near-wall streamline) reports the same cooling behind the jet: after atomization the temperature "drops to around 700 K due to evaporation", and low-temperature chemistry follows. The fuel-rich wall layer here is at 704–748 K (`nearjet`). The paper does not report the colder inner pocket (418 K) or how much liquid it holds.

With the `escape` wall, the pocket keeps 2947 µg, against 3107 µg with `rebound` at 80 µs, and the front is unchanged. The escape wall also removes freestream droplets upstream of the jet, which changes the incoming near-wall gas: 1171 K against 1143 K, and C7H16 0.083 against 0.090. So step 2a does not isolate the pocket.

### Step 2d: jet off to 200 µs

`large_off_long` continues `large_off` (jet off since 70 µs) from 130 to 200 µs. Detonation base x position [mm]:

| Height | 130 µs | 150 µs | 170 µs | 190 µs | 200 µs |
|---|---|---|---|---|---|
| 3 mm | 56.7 | 58.3 | 59.1 | 60.3 | 61.5 |
| 9 mm | 54.9 | 55.3 | 55.9 | 57.3 | 58.3 |
| 15 mm | 59.3 | 59.3 | 59.9 | 61.3 | 62.3 |
| 26 mm | 72.7 | 69.5 | 69.3 | 71.1 | 72.3 |

- The detonation does not fail. 130 µs after switch-off it still stands, with a pressure ratio of about 30 at 9–15 mm.
- It does not settle either. The base keeps moving downstream at about 0.07 mm/µs at 3 mm, and at 9–15 mm the drift speeds up after 170 µs (0.1 mm/µs over 190–200 µs).
- The x = 100 mm performance metric is unusable in this run after 130 µs. Cold (< 600 K), fuel-rich gas from the decaying liquid pocket crosses the plane at heights up to 25 mm. The mass flux through the plane swings between 28 and 91 g/s (the control holds about 37 g/s), and single cells reach up to 54 times the inflow total pressure. Even with the suspect cells removed, recovery jumps between 0.04 and 0.17 from save to save. Whether the jet-off loss is a transient is therefore still open.

## Step 3: pulsed jet

Recovery values and front positions quoted in the cycle notes below were taken while the runs progressed, with the earlier five-species metric and the earlier front tracker. The corrected values are in [Verified performance](#verified-performance), the tables of the 80 kHz and equal-fuel sections, and the table below.

`large_f40k` with the current tracker (2026-10-09), base x [mm]; the control holds 50.7 at 3 mm and 52.1–52.3 at 9 mm:

| Time (µs) | 95 | 100 | 105 | 110 | 115 | 120 | 125 | 130 | 135 | 140 | 145 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 mm | 51.1 | 51.7 | 52.3 | 53.1 | 53.9 | 51.5 | 51.9 | 52.7 | 53.7 | 54.5 | 51.5 |
| 9 mm | 52.5 | 52.7 | 53.1 | 53.5 | 53.7 | 54.1 | 53.7 | 53.5 | 53.5 | 53.7 | 53.9 |

`large_f40k`: 40 kHz, 50% duty, from `box_large` at 70 µs. The jet is on at 70–82.5, 95–107.5 and 120–132.5 µs. Shock x position [mm] at 1 mm height:

| Time | Jet on (control) | 40 kHz, 50% | Jet off since 70 µs |
|---|---|---|---|
| 85 µs | 49.9 | 49.9 (off) | 50.7 |
| 90 µs | 49.9 | 49.9 (off) | 51.5 |
| 95 µs | 49.7 | 50.5 (end of off) | 52.3 |
| 100 µs | | 51.3 (on) | 53.1 |
| 105 µs | | 52.5 (on, pressure ratio 2.1) | 54.1 |

- The base barely moves during the first off-phase, consistent with the ~10 µs delay before retreat in step 2.
- The retreat that starts late in the off-phase continues into the next on-phase, because the returning jet takes more than 10 µs to rebuild its shock (step 2c). By 105 µs the base has retreated 2.6 mm, against 4.2 mm with the jet off.
- At 9–15 mm the detonation stays within 0.6 mm of the control.
- On the x = 100 mm plane at 95 µs, the 40 kHz case matches the control: recovery 0.132 in both, burnt fuel 2.44 against 2.43 g/s. It has injected half the jet fuel since 70 µs.

Second cycle, with the extended jet-on control. Shock x position [mm]:

| Height | Time | Jet on | 40 kHz, 50% | Jet off since 70 µs |
|---|---|---|---|---|
| 3 mm | 95 µs | 50.9 | 51.3 | 52.7 |
| 3 mm | 105 µs (pulse on) | 50.9 | 52.5 | 54.1 |
| 3 mm | 115 µs (pulse off) | | 53.9 | 55.3 |
| 9 mm | 95 µs | 52.5 | 52.7 | 53.7 |
| 9 mm | 105 µs | 52.3 | 53.3 | 54.3 |
| 9 mm | 115 µs | | 53.9 | 54.9 |
| 1 mm | 110–115 µs | 49.7 | 50.5–50.7 | 54.7–55.3 |

- At 40 kHz and 50% duty the base is not held. From 95 µs on, the 2–9 mm part of the front drifts downstream at the same rate as with the jet off, about 0.13 mm/µs at 3 mm. It stays about 1.4 mm behind the jet-off run, because the first ~10 µs of each off-phase cost nothing.
- Each on-phase re-forms the shock at 1 mm (50.5–50.7 mm) but does not slow the drift above it.
- The liquid pocket persists (4098 µg at 115 µs, against 4652 µg in the control at 105 µs). It delays the retreat but does not stop it.
- On the x = 100 mm plane the 40 kHz case matches the control at half the jet fuel: recovery 0.127 at 115 µs against 0.126 at 105 µs, burnt fuel 2.38 against 2.39 g/s.

The control also moves: between 80 and 105 µs its front at 26 mm goes from 80.5 to 77.9 mm, and its recovery from 0.132 (95 µs) to 0.126 (105 µs). Most of the upper-front movement and recovery drop seen with the jet off is therefore the box still converging. At 105 µs the jet-off recovery (0.122) is close to the control's (0.126).

Third cycle. Shock x position [mm]:

| Time | Jet on, 3 mm / 9 mm | 40 kHz, 3 mm | 40 kHz, 9 mm | Jet off, 3 mm | Jet off, 9 mm |
|---|---|---|---|---|---|
| 115 µs | 50.9 / 52.3 | 53.9 | 53.9 | 55.3 | 54.9 |
| 120 µs (end of off) | 50.9 / 52.3 | 51.7 | 54.3 | 55.9 | 55.1 |
| 125 µs (on) | | 52.1 | 53.9 | 56.3 | 55.1 |
| 130 µs (on) | | 52.9 | 53.7 | | |

The drift reverses. The second on-phase (95–107.5 µs) moves the base at 1–3 mm back upstream, but only by 120 µs, during the following off-phase. The 9 mm front turns around after it (54.3 to 53.7 mm). The front responds to each pulse with a lag of about 10–20 µs. So far it oscillates about 2 mm peak to peak at 3 mm, 1–2 mm behind the jet-on position, while the jet-off front keeps retreating. The reading after the second cycle, that the base drifts at the jet-off rate, was taken before the delayed recovery arrived.

On the x = 100 mm plane at 120 µs, recovery is 0.128 for 40 kHz, 0.126 for the jet-on control and 0.107 for the jet-off run; burnt fuel crossing is 2.41, 2.37 and 2.25 g/s. At 130 µs the 40 kHz case gives 0.133 and 2.57 g/s. At equal times, the jet-off run now falls clearly below the control, so part of its recovery loss is real.

If the third cycle repeats this pattern, 40 kHz at 50% duty stabilizes the front dynamically: a bounded oscillation at control-level performance with half the jet fuel. The 135–145 µs saves decide it.
### Result: 40 kHz, 50% duty, three cycles

Shock x position [mm] at 3 mm height, old tracker (current values in the table above: extremes 51.5 and 53.9 / 54.5 mm, control 50.7). The jet-on control holds 50.9.

| Cycle | Furthest back | Furthest upstream |
|---|---|---|
| 2 | 53.9 (115 µs) | 51.7 (120 µs) |
| 3 | 54.7 (140 µs) | 51.7 (145 µs) |

- The base oscillates with the 25 µs pulse period. The upstream extreme repeats exactly, and the downstream extreme moves 0.8 mm further in cycle 3.
- At 9 mm the detonation stays at 53.7–54.3 mm over cycles 2 and 3, 1.5–2 mm behind the jet-on control (52.1–52.3 mm), with no drift. At 15 mm it is about 1 mm behind.
- The jet-off front is at 56.9 mm at 3 mm by 130 µs and still retreating.

Performance is given in [Verified performance](#verified-performance). Over cycles 2 and 3 the 40 kHz case matches the jet-on control in total-pressure recovery and burnt fuel with half the jet fuel, while removing the jet costs about 30% of the recovery by 50 µs after switch-off. The front is stabilized dynamically: it oscillates in a bounded band phase-lagged to the pulses. This rests on three cycles; the 0.8 mm growth of the downstream extreme needs a longer run to rule out a slow drift.

### 80 kHz, 50% duty

`large_f80k` (6.25 µs off, shorter than the ~10 µs retreat delay) ran from 70 to 120 µs. Detonation base x position [mm] at 3 mm height:

| Time | Jet on | 80 kHz | 40 kHz | Jet off |
|---|---|---|---|---|
| 95 µs | 50.7 | 51.3 | 51.1 | 52.7 |
| 100 µs | 50.7 | 51.3 | 51.7 | 53.3 |
| 105 µs | 50.7 | 51.5 | 52.3 | 53.9 |
| 110 µs | 50.7 | 51.1 | 53.1 | 54.5 |
| 115 µs | 50.7 | 51.3 | 53.9 | 55.1 |
| 120 µs | 50.7 | 51.3 | 51.5 | 55.7 |

At 80 kHz the base stays 0.4–0.8 mm behind the jet-on position at 2–4 mm and 0.4–1.4 mm behind at 6–9 mm, at every save from 95 to 120 µs. `large_f80k_long` continues this: at 3 mm 51.1, 51.5, 51.1, 51.3 and 51.3 mm at 125–145 µs. Doubling the frequency at the same duty removes most of the 40 kHz oscillation.

### Equal-fuel continuous jets

`large_half` (half velocity, J = 0.25) ran from 70 to 145 µs. Detonation base x position [mm] at 3 mm height:

| Time | Jet on | Half velocity | Jet off |
|---|---|---|---|
| 100 µs | 50.7 | 51.9 | 53.3 |
| 115 µs | 50.7 | 54.9 | 55.1 |
| 130 µs | 50.7 | 56.7 | 56.7 |
| 145 µs | 50.7 | 58.1 | 58.3 |

The half-velocity jet holds the base no better than no jet at all, and by 145 µs it is still retreating at about 0.1 mm/µs. This is what the paper reports for J = 0.1–0.3, below its J ≥ 0.4 threshold for direct initiation, so it is not by itself evidence for pulsing. Its performance does not follow the base: over 125–145 µs its recovery is 0.137 against 0.116 for the control, and its burnt fuel 2.48 against 2.37 g/s (recomputed on 2026-10-06). At equal mean fuel, the pulsed jets hold the base and the half-velocity jet does not, but the half-velocity jet has the higher recovery at x = 100 mm. With the jet off, the base also retreats but recovery falls by about 30%; why a retreating base costs recovery in one case and not the other is examined below.

Recovery by height on the x = 100 mm plane, averaged over 120, 125 and 130 µs (mass flux per 2 mm depth, recovery against the inflow):

| y (mm) | Control: mass, recovery | Half velocity | Jet off |
|---|---|---|---|
| 0–3 | 6.01 g/s, 0.124 | 6.73 g/s, 0.168 | 6.36 g/s, 0.124 |
| 3–6 | 5.67 g/s, 0.183 | 5.84 g/s, 0.209 | 4.31 g/s, 0.104 |
| 6–10 | 7.17 g/s, 0.178 | 6.67 g/s, 0.174 | 3.87 g/s, 0.076 |
| 10–15 | 5.81 g/s, 0.080 | 5.98 g/s, 0.079 | 4.38 g/s, 0.048 |
| 15–20 | 5.64 g/s, 0.059 | 5.78 g/s, 0.060 | 5.43 g/s, 0.060 |
| 20–25 | 6.66 g/s, 0.073 | 6.71 g/s, 0.073 | 6.54 g/s, 0.075 |

- Above 15 mm the three cases agree. Every difference comes from the lowest 15 mm.
- The half-velocity jet gains only in the lowest 6 mm: the stream next to the wall passes a weaker jet shock.
- With the jet off, the loss is at 3–15 mm, and 6 g/s less mass crosses the plane below 25 mm, so the flow there is displaced away from the wall. At 125 µs the subsonic wall region left by the broken-up liquid pocket spans x = 65.5–95.1 mm, just upstream of the plane. The likely reading is that the jet-off loss comes from that region approaching the plane, not from the retreat of the base itself. If so, it is a transient. `large_off_long` could not settle this, because after 130 µs the decaying pocket makes the metric unusable on this plane (step 2d).

### Half-width jet (`large_narrow`)

`large_narrow` (one 0.2 mm face at J = 1, half the jet fuel) ran from 70 to 145 µs. Detonation base x position [mm]:

| Height | Control, 145 µs | Half width, 125 µs | 135 µs | 145 µs |
|---|---|---|---|---|
| 3 mm | 50.7 | 51.7 | 51.9 | 51.9 |
| 9 mm | 51.9 | 53.5 | 53.7 | 54.1 |
| 15 mm | 58.1 | 59.3 | 59.5 | 59.9 |
| 26 mm | 75.7 | 76.9 | 76.3 | 75.7 |

Over 125–145 µs its recovery is 0.123 against 0.116 for the control, and its burnt fuel 2.44 against 2.37 g/s.

Re-run with the current tracker (2026-10-13), the base at 3 mm is 50.7–51.5 mm to 120 µs, then 51.7, 51.9, 52.1 and 52.9 mm at 130–145 µs: it creeps downstream at about 0.06 mm/µs over 120–145 µs, at 2–4 mm alike. The 145 µs value in the table above (51.9) is from the old tracker.

At equal mean jet fuel, the half-width steady jet holds the base as well as the 80 kHz pulse (0.4–0.8 mm behind at 3 mm) up to 120 µs and then drifts, better than the 40 kHz pulse (oscillating 1–4 mm behind), and far better than the half-velocity jet (7.4 mm behind). Its recovery is at least the control's. **In this 2D model, a narrower steady jet at the same J matches the pulsed jets in performance; whether its base settles was not determined.** Two caveats: the jet is one cell wide, and it uses a different injector model (see the ladder). A narrower slot is also not the same as a smaller round jet in 3D.

## Memory model and the 20 kHz prediction

The jet-off and pulsed runs suggest one simple picture of the front base at 3 mm:

- After the jet stops, the base holds for a delay τ ≈ 10 µs (step 2).
- It then retreats at v_r ≈ 0.12–0.13 mm/µs (current tracker, step 2 table above).
- When the jet returns, the retreat continues for a lag before recovery starts: 10–20 µs after the 12.5 µs off-phases of `large_f40k`, more than 25 µs after a 25 µs off-time (step 2c, `large_f20k`).

If the delay and the lag cancel, the excursion per cycle is about v_r × T_off, where T_off = (1 − D)/f. On 2026-10-06, before `large_f20k` ran, this estimate was written down with v_r = 0.13–0.2 mm/µs, giving 3.3–5 mm at 20 kHz. The upper part of that range came from the old tracker's 1 mm values. With the 3 mm retreat speed:

| Case | T_off | v_r × T_off (0.12–0.13 mm/µs) | Pre-run estimate | Observed at 3 mm |
|---|---|---|---|---|
| 80 kHz, 50% | 6.25 µs (< τ) | small offset | small offset | 0.4–0.8 mm offset, no oscillation |
| 40 kHz, 50% | 12.5 µs | 1.5–1.6 mm | 1.6–2.5 mm | about 3 mm peak to peak (51.5–54.5) |
| 20 kHz, 50% (`large_f20k`) | 25 µs | 3.0–3.3 mm | 3.3–5 mm | 3.8 mm at 145 µs, still growing |

The estimate has the right order and trend but is low by a factor 1.2–2, because the lag after switch-on exceeds the hold after switch-off and grows with the distance retreated. The 20 kHz result fell inside the pre-run range, but partly because the faster 1 mm retreat speed in that range offset the longer lag; it is not a clean test of the model. The front stays held, with only a small offset, while T_off < τ, which gives f_min ≈ (1 − D)/τ: about 50 kHz at 50% duty and 75 kHz at 25% duty for this 0.5 mm jet.

### Result: 20 kHz, 50% duty

The jet is off from 95 to 120 µs and on from 120 to 145 µs. The base position at 3 mm is shown below; the control stays at 50.7 mm throughout.

| Time (µs) | 95 | 100 | 105 | 110 | 115 | 120 | 125 | 130 | 135 | 140 | 145 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `large_f20k` (mm) | 50.7 | 50.7 | 50.9 | 51.5 | 51.9 | 52.5 | 53.1 | 53.5 | 53.5 | 53.7 | 54.5 |

- The base held for about 10 µs after switch-off, as τ predicts.
- It then retreated at about 0.1 mm/µs, the same as `large_off` over the same interval after switch-off (step 2 table).
- After the jet returned, the base kept moving back, slowing over 130–140 µs. At 145 µs it was 3.8 mm behind the control and still moving back, inside the pre-run range of 3.3–5 mm and above the 3.0–3.3 mm that v_r × T_off gives with the 3 mm retreat speed. At 3 mm the shock had weakened to a pressure ratio of 3, against 6.8 in the control.
- Above 9 mm the front matches the control throughout.

Unlike at 40 kHz, the base did not start to return within the 25 µs on-phase. One cycle cannot show whether a second cycle would oscillate about a new position or ratchet further back. Recovery over 125–145 µs is 0.107 against 0.116 for the control (see [Verified performance](#verified-performance)). A 25 µs gap therefore costs performance where a 12.5 µs gap does not. This places the critical frequency for this jet at 50% duty between 20 and 40 kHz, below the 50 kHz estimate from f_min ≈ (1 − D)/τ. The likely reason is the retreat lag, which lets short excursions recover before they cost anything.

τ ≈ 10 µs is close to d_j/u_j = 0.5 mm / 60.8 m/s = 8.2 µs, the time the jet takes to inject one jet width of liquid. If τ scales with jet width at fixed J, a jet of width d has f_min ≈ (1 − D) u_j / d. At 50% duty this gives about 30 kHz for a 1 mm jet, 15 kHz for 2 mm, and 3 kHz for the 10 mm jet of the confined combustor (arXiv:2605.27871), which is within reach of real pulsed injectors. That scaling is a hypothesis, which `crop_grid_d1` would test.

## Step 4: grid check of the memory

The memory (delay and retreat rate after switch-off) is the main result, so it is the quantity checked for grid dependence. A full box at 0.15 mm costs about 2.4 times a 0.2 mm box per µs, so the check uses a crop:

- Domain 100 × 25 mm, the near-jet region of `box_large` (the jet at x = 50 mm, the subsonic wall region to x ≈ 65 mm, and the base up to 15 mm). The upper boundary cuts the ODW near x = 70 mm; that affects both grids alike.
- `crop_grid` (0.2 mm, 500 × 125 cells) and `crop_grid_fine` (0.15 mm, 667 × 167 cells), each run from uniform freestream to 50 µs. The near-jet front in `box_large` was settled from 35 µs.
- At 50 µs each branches with the jet off to 90 µs (`crop_grid_off`, `crop_grid_fine_off`). The jet-on state at 50 µs is the reference, since the jet-on base at 3 mm drifts by less than 0.2 mm over 70–145 µs in `box_large`.
- Compared: the jet-on base at 1–15 mm, the delay, and the retreat rate. `crop_grid_off` against `large_off` also checks that the crop reproduces the box.

Measured rates on 8 ranks: `crop_grid` 4.3 µs/h and `crop_grid_fine` 2.3 µs/h when sharing the host with a box run, about half that when the two crops share it.

### Result (2026-10-10)

Detonation base x [mm] against time after switch-off (`wave`; the tracker windows keep their physical length on the 0.15 mm grid; `large_off` switches off at 70 µs, the crops at 50 µs):

| After switch-off (µs) | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| `large_off` (box, 0.2 mm), 3 mm | 50.7 | 50.7 | 50.9 | 51.3 | 51.9 | 52.7 | 53.3 | 53.9 | 54.5 |
| `crop_grid_off` (0.2 mm), 3 mm | 50.7 | 50.7 | 50.9 | 51.5 | 52.1 | 52.7 | 53.3 | 54.1 | 54.7 |
| `crop_grid_fine_off` (0.15 mm), 3 mm | 50.7 | 50.7 | 51.0 | 51.6 | 52.1 | 52.7 | 53.3 | 54.0 | 54.8 |
| `large_off`, 9 mm | 52.9 | 52.9 | 52.7 | 52.9 | 53.1 | 53.5 | 53.9 | 54.1 | 54.5 |
| `crop_grid_off`, 9 mm | 53.7 | 53.5 | 53.3 | 53.5 | 53.7 | 54.1 | 54.3 | 54.5 | 54.7 |
| `crop_grid_fine_off`, 9 mm | 53.9 | 53.7 | 53.4 | 53.6 | 53.9 | 54.2 | 54.5 | 54.8 | 54.8 |

- At 3 mm the two grids agree within 0.1 mm at every save over 40 µs, and the crop agrees with the box within 0.2 mm. The hold (about 10 µs) and the retreat speed (0.13 mm/µs over 15–40 µs) do not depend on the grid or on the crop.
- At 9 mm the grids agree within 0.3 mm. The crops sit 0.8–1.0 mm downstream of the box at switch-off and converge to it by 40 µs. The crops switch off at 50 µs and the box at 70 µs, and the box's upper front was still moving upstream at that age (step 1), so this offset is the crops' younger front, not the switch-off response.
- The jet-on base at 50 µs is the same on both grids (50.7 mm at 3 mm).
- The crop reproduces the box response, so options A and B (step 5), which run in the crop, can be compared with the box runs.
- Per-area jet momentum flux differs between the grids (0.45 mm patch on 0.15 mm against 0.4 mm on 0.2 mm, a factor 1.11) with no visible effect.

## Where a stronger result could come from

### Fixed-injector turndown (2026-10-09)

The equal-fuel comparison (step 3b) used a narrower steady jet, which is a different injector. An engine's injector is fixed once built, and its fuel flow can then be cut only by throttling (lower velocity at the same width) or by pulsing. Throttling a liquid jet of fixed width scales its mass flow with u_j and J with u_j², so J = (fuel fraction)². The paper's J ≥ 0.4 for direct initiation at the jet is reached at 63% of the full jet fuel. Below that, the paper's cold-start cases (J = 0.1–0.3) initiate the ODW about 80 mm downstream instead of at the jet (x = 50 mm).

The runs so far, measured as the base position at 3 mm (the initiation point of the anchored front):

| Mean jet fuel | Throttled (fixed width) | Pulsed at J = 1 |
|---|---|---|
| 100% | 50.7 mm (control) | – |
| 71% (J = 0.5) | at the jet, in the paper's cold-start runs | – |
| 50% | 58.1 mm at 145 µs and sliding (`large_half`, J = 0.25) | 51.1–51.5 mm at 80 kHz, oscillating 51.5–54.5 mm at 40 kHz |
| 25% | J = 0.06, below every case the paper ran | `crop_grid_f80k_q`, queued |

At 50% fuel, pulsing keeps initiation at the jet and throttling does not. That is the comparison in which pulsing is the more efficient way to cut jet fuel with a given injector: it is a turndown result, not a total-pressure one (the throttled jet's recovery is higher, 0.137 against 0.116). Two runs decide how strong it is:

- `large_half_long` continues the throttled jet to 200 µs. If its front keeps sliding towards the paper's low-J mode, throttling loses the anchored mode at 50% fuel; if it settles near the jet, the anchored mode survives throttling and the advantage of pulsing is only the base offset.
- `crop_grid_f80k_q` tests whether pulsing still holds the front at 25% fuel.

The comparison is between an anchored front that is throttled and one that is pulsed, both starting from the full jet. This matches engine operation (start with the full jet, then turn down), and it matters, because the anchored front shows hysteresis: without a jet the spray never ignites from a cold start (validation §5), yet an anchored front survives 130 µs without the jet (step 2d).


The reframed study rests on the memory and the frequency sweep. Two further experiments could make it considerably stronger. Both are cheap as crop runs, and both are queued (step 5). They are only valid if `crop_grid_off` shows that the crop reproduces `large_off`; check that before reading them.

**A. Does pulsing beat a steady jet at low fuel?** At 50% fuel a half-width steady jet matches pulsing in performance. A steady jet carrying less fuel at the same J gets smaller still, and at some point it should be too small to hold the front. A pulsed jet keeps its full size while it is on. So pulsing may win below some fuel fraction. Test at 25% fuel, both branched from `crop_grid` at 50 µs to 90 µs:

- 80 kHz, 25% duty (T_off = 9.4 µs, just under τ): `--pulse 80000 0.25`
- a steady jet with a quarter of the fuel on one face, at the J = 1 velocity: `--jet-on --half-width --jet-scale 0.5`. `--jet-scale` keeps the velocity but halves the mass flow through the face, so the momentum flux per unit area is half that of the full jet (about J = 0.5 by flux). An equal-J quarter-fuel jet would be 0.1 mm wide, below the grid. This is therefore not an equal-J comparison: if the steady jet holds the front, pulsing has no advantage at 25% fuel; if it loses it, size and flux are confounded.

If the steady jet loses the front and the pulsed jet holds it, pulsing has a clear advantage at low fuel, which is the result the original question asked for. If both hold, the fuel can be cut further with a steady jet and pulsing has no advantage. Cost: two 40 µs crop branches, about 11 h each at 8 ranks.

**B. Does the memory scale with jet width?** `crop_grid_d1` (a 1 mm jet at J = 1, twice the fuel) run to 50 µs and branched with the jet off. If τ doubles to about 20 µs, the f_min scaling above holds and pulsing is practical at engine-scale jet sizes. Cost: about 25 h at 8 ranks.

### Results (2026-10-11)

Base x [mm] at y = 3 mm (`wave`). The crops switch at 50 µs; `crop_grid_off` and the jet-on base at 50 µs are from step 4. Option A's steady quarter-fuel jet was not run (it is not an equal-J test; see above).

| t (µs) | 50 | 55 | 60 | 65 | 70 | 75 | 80 | 85 | 90 |
|---|---|---|---|---|---|---|---|---|---|
| `crop_grid_off` (0.5 mm jet off) | 50.7 | 50.7 | 50.9 | 51.5 | 52.1 | 52.7 | 53.3 | 54.1 | 54.7 |
| `crop_grid_f80k_q` (80 kHz, 25% duty) | 50.7 | 50.7 | 50.9 | 51.1 | 51.7 | 52.7 | 53.5 | 54.3 | 55.7 |
| `crop_grid_d1_off` (1 mm jet off) | 49.9 | 49.9 | 50.1 | 50.5 | 50.7 | 51.1 | 51.3 | stopped | stopped |

**25% duty (option A, pulsed half).** The jet is on for 3.1 µs and off for 9.4 µs per 12.5 µs period, with on-phases starting at 50, 62.5, 75 and 87.5 µs. The base retreats as with the jet off and ends 1.0 mm further downstream (55.7 against 54.7 mm at 90 µs, 2.5 µs into an on-phase). At y = 1 mm the reaction separates from the shock from 75 µs (burn gap 7.2 mm at 75 µs, 11.8 at 85 µs, 13.6 at 90 µs; pressure ratio 2.7–6.0 against 8.3–9.7 with the jet off). At y = 3 mm the gap is 2.2, 6.4 and 13.6 mm at 80, 85 and 90 µs (shock pressure ratio 3.5 at 90 µs). The front at y = 9–15 mm stays within 1.6 mm of the jet-off case. An off-time shorter than τ does not hold the base when each on-phase is this short. The fixed-injector turndown advantage of pulsing therefore does not extend to 25% fuel at 80 kHz.

**Throttled jet to 200 µs (`large_half_long`, J = 0.25, box).**

| t (µs) | 145 | 150 | 155 | 160 | 165 | 170 | 175 | 180 | 185 | 190 | 195 | 200 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 mm | 58.1 | 58.5 | 58.9 | 59.3 | 59.7 | 59.9 | 60.1 | 60.3 | 60.5 | 60.7 | 60.7 | 60.9 |
| 15 mm | 61.9 | 62.1 | 62.3 | 62.7 | 62.7 | 62.9 | 63.1 | 63.3 | 63.3 | 63.5 | 63.5 | 63.7 |
| jet off (`large_off_long`), 3 mm | 58.3 | | | 58.7 | | | 59.3 | | | 60.3 | | 61.5 |
| jet off, 15 mm | 59.1 | | | 59.5 | | | 60.1 | | | 61.3 | | 62.3 |

The throttled base slows from 0.08 mm/µs (145–160 µs) to 0.02 mm/µs (190–200 µs) and is settling near x ≈ 61 mm, about 10 mm behind the J = 1 control; the shock at 3 mm weakens from pressure ratio 6.0 to 3.4. The jet-off base speeds up over the same interval (0.03 to 0.12 mm/µs). It does not slide towards the paper's low-J initiation point (about 80 mm) within 200 µs. Throttling to 50% fuel keeps an anchored front, displaced about 10 mm; pulsing at 50% keeps it within 0.8 mm (80 kHz). The turndown comparison at 50% fuel is therefore a 10 mm offset, not a lost mode.

**1 mm jet (option B, `crop_grid_d1`, `crop_grid_d1_off`).** The 1 mm patch is five faces carrying ρ_l u_j d_j, so its momentum flux per unit area is the nominal one (1.0×, against 1.25× for the 0.5 mm jet's 0.4 mm patch). Jet on at 50 µs the base sits at 49.9 mm at 3 mm, 51.5 mm at 9 mm and 58.3 mm at 15 mm (0.5 mm jet: 50.7, 53.7, 60.7). After switch-off the base moves 0.2 mm by 10 µs, the same as the 0.5 mm jet, and then retreats at 0.067 mm/µs over 60–75 µs, against 0.12 mm/µs for the 0.5 mm jet. After 25 µs it has moved 1.2 mm against 2.0 mm, and after 30 µs 1.4 mm against 2.6 mm (0.04 against 0.12 mm/µs over the last 5 µs). The hold time does not double with jet width; the retreat speed halves. The run was stopped at 80 µs (30 µs after switch-off) on 2026-10-11: the last 10 µs would have cost about 7 h and could not change the conclusion.

### The base follows the wall liquid (2026-10-11)

Liquid in x = 49.5–100 mm, y < 3 mm, from `scripts/checks/liquid_edge.py`: total mass, mass within 3 mm downstream of the jet (x < 52.5 mm), and the x below which 5%, 25% and 50% of that liquid lies.

| Case, t (µs) | Liquid (µg) | Within 3 mm of jet (µg) | x5 | x25 | x50 | Base, 3 mm |
|---|---|---|---|---|---|---|
| `crop_grid` 50 (jet on) | 2201 | 1233 | 50.1 | 50.7 | 51.9 | 50.7 |
| `crop_grid_off` 55 | 2214 | 1055 | 50.3 | 51.1 | 52.5 | 50.7 |
| 60 | 2228 | 814 | 50.7 | 51.7 | 53.1 | 50.9 |
| 65 | 2246 | 587 | 51.5 | 52.3 | 53.9 | 51.5 |
| 70 | 2250 | 300 | 52.3 | 52.9 | 54.7 | 52.1 |
| 75 | 2215 | 0 | 53.3 | 53.7 | 55.7 | 52.7 |
| 80 | 2125 | 0 | 54.3 | 54.5 | 56.5 | 53.3 |
| 85 | 1879 | 0 | 55.3 | 55.5 | 56.7 | 54.1 |
| 90 | 1376 | 0 | 56.3 | 57.1 | 60.3 | 54.7 |
| `crop_grid_f80k_q` 55 | 2343 | 1184 | 50.1 | 50.9 | 52.3 | 50.7 |
| 60 | 2356 | 950 | 50.5 | 51.5 | 52.9 | 50.9 |
| 65 | 2473 | 827 | 50.9 | 51.7 | 53.5 | 51.1 |
| 70 | 2508 | 647 | 50.5 | 52.3 | 54.1 | 51.7 |
| 75 | 2478 | 133 | 51.5 | 53.1 | 54.9 | 52.7 |
| 80 | 2527 | 190 | 50.5 | 53.7 | 55.5 | 53.5 |
| 85 | 2441 | 137 | 51.3 | 54.7 | 56.5 | 54.3 |
| 90 | 2484 | 207 | 51.9 | 55.7 | 57.1 | 55.7 |
| `crop_grid_d1` 50 (jet on) | 4327 | 3304 | 49.9 | 50.3 | 51.3 | 49.9 |
| `crop_grid_d1_off` 55 | 4352 | 2841 | 50.1 | 50.7 | 51.7 | 49.9 |
| 60 | 4376 | 2423 | 50.5 | 50.9 | 52.1 | 50.1 |
| 65 | 4412 | 2130 | 50.7 | 51.3 | 52.5 | 50.5 |
| 70 | 4456 | 1806 | 51.3 | 51.7 | 53.1 | 50.7 |
| 75 | 4499 | 1413 | 51.7 | 52.1 | 53.7 | 51.1 |
| 80 | 4526 | 909 | 52.3 | 52.5 | 54.3 | 51.3 |

- After switch-off the liquid mass does not fall for 30 µs (2.2 mg from 50 to 80 µs; evaporation is slow, as found in step 2). What changes is its position: the layer slides downstream as a whole, x50 at 0.16 mm/µs and x25 at 0.14 mm/µs over 55–80 µs, and the liquid within 3 mm of the jet drains to zero in 25 µs.
- The base at 3 mm stays 0–1.0 mm upstream of x25 in all three runs through 75 µs (jet off 0–1.0, 25% duty 0–0.6, 1 mm jet 0.8–1.0), including both jet-on states. After 75 µs with the jet off, as the layer washes out of the region (1.4 mg at 90 µs), the base lags it by up to 2.4 mm.
- The 25% duty pulses keep a little liquid at the jet (x5 stays at 50.5–51.9 mm) but do not stop the bulk of the layer from sliding (x25 moves at 0.14 mm/µs, as with the jet off), and the base follows the bulk. More liquid near the wall (2.5 against 2.2 mg) does not hold the front; liquid at the jet does.
- The 1 mm jet's layer has twice the mass and slides at about half the speed (x25 at 0.08 mm/µs over 60–75 µs), and its base retreats at about half the speed.
- Reading: the front base is pinned to the upstream end of the wall liquid layer. The hold time is the time the layer's upstream end takes to start moving, and the retreat speed is the speed at which the gas drags the layer downstream. The dry run of step 2b (all liquid removed, base retreats at once) is the causal test; this table is a correlation across three runs. The layer is in the dense regime (about 30% volume fraction in its cells), so its drag and motion are where the point-particle model is least reliable.

## Performance metric and continuous-jet baseline

Pulsed and continuous cases are compared on a fixed plane through the stream the jet processes: x = 100 mm, y < 25 mm (`python -m pulswave performance <case> <t...> --x 100 --ymax 25`). The reported values are:

- Total-pressure recovery: the mass-flux-weighted total pressure crossing the plane divided by that entering the domain.
- Burnt fuel: the fuel-equivalent carbon in CO2 and CO crossing the plane. Carbon in intermediates (C2H2, C2H4 and others, about 7% of the mass of the fuel-rich burnt gas near the wall) is not counted, so this is a lower bound on the fuel that has reacted.

Total pressure is the isentropic stagnation pressure at frozen composition, over all 44 species of the mechanism, from the solver's JANAF tables. It matches Cantera to 0.005% for the freestream, burnt gas, fuel-rich burnt gas next to the wall and cold, heptane-rich gas. An earlier version kept five species and counted the rest as N2. In fuel-rich burnt gas, where C2H2, H2 and C2H4 make up 7% of the mass, that overestimated the cell total pressure by 27% and the plane recovery by 0.004–0.012. All values in this file use the full composition.

The metric is not used where the plane cuts evaporating jet liquid. Evaporation cools heptane-rich gas to about 350 K, and stagnating that gas isentropically gives up to 18 times the inflow total pressure (x = 80 mm in `large_off` at 125 µs). No cell on the x = 100 and 110 mm planes exceeds 0.5 of the inflow total pressure, and no cell has reversed flow, in any save used in the tables below (`performance --check`); `large_off_long` after 130 µs is the exception (step 2d). The metric is for the gas phase only. Its denominator is the total pressure entering through the left and top boundaries; it stays at 191.5–192.1 atm in every case, close to the freestream value (191.5 atm), so shocked cells on the top boundary do not affect it by more than 0.3%.

The domain outflow is not used for comparing cases, for two reasons:

- In the unshocked freestream, spray evaporation cools the gas from 697 K to 589 K. At Mach 4.8 this raises the gas-phase total pressure up to 348 atm, against 191 atm entering. The liquid-phase share is not included.
- In `paper_j1` the upper front is still unsteady where it reaches the outflow. The outflow recovery there varies between 0.92 and 1.19 over 85–100 µs.

| Case | Save | Recovery | Burnt fuel crossing the plane |
|---|---|---|---|
| `paper_j1` | 95, 100 µs | 0.123, 0.115 | 2.52, 2.39 g/s |
| `box_large` | 95, 100 µs | 0.123, 0.121 | 2.43, 2.38 g/s |

Rates are per 2 mm depth. The continuous jet injects 41.4 g/s. The freestream spray supplies 9.7 g/s over the whole `paper_j1` boundary.

In the continuous-jet case, the jet-processed stream loses about 88% of its total pressure by x = 100 mm. The fuel crossing the plane burnt equals at most 6% of the fuel the jet injects, and part of it is freestream fuel. In `box_large` both values match `paper_j1` at equal times.

## Verified performance

All values: x = 100 mm, y < 25 mm, full-composition total pressure, averaged over five saves 5 µs apart. Five saves span one 25 µs period at 40 kHz and two at 80 kHz, at evenly spaced phases. Each pulsed case is compared with the jet-on control over the same window.

| Case | Jet fuel | Window | Recovery | Control | Burnt fuel | Control |
|---|---|---|---|---|---|---|
| 40 kHz, 50% (`large_f40k`) | 50% | 125–145 µs | 0.116 | 0.116 | 2.41 g/s | 2.37 g/s |
| 40 kHz, 50% (`large_f40k`) | 50% | 120–140 µs | 0.119 | 0.117 | 2.45 g/s | 2.37 g/s |
| 80 kHz, 50% (`large_f80k`) | 50% | 95–115 µs | 0.120 | 0.120 | 2.41 g/s | 2.40 g/s |
| 80 kHz, 50% (`large_f80k_long`) | 50% | 125–145 µs | 0.116 | 0.116 | 2.41 g/s | 2.37 g/s |
| 20 kHz, 50% (`large_f20k`) | 50% | 125–145 µs | 0.107 | 0.116 | 2.32 g/s | 2.37 g/s |
| Half velocity (`large_half`) | 50% | 100–110 µs | 0.120 | 0.119 | 2.40 g/s | 2.38 g/s |
| Half velocity (`large_half`) | 50% | 125–145 µs | 0.137 | 0.116 | 2.48 g/s | 2.37 g/s |
| Jet off (`large_off`) | 0% | 120–130 µs | 0.082 | 0.118 | 2.10 g/s | 2.38 g/s |

Checks on these values:

- **Noise floor.** Save-to-save scatter of the control about its trend is ±0.002 in recovery and ±0.04 g/s in burnt fuel. Differences below about 0.003 and 0.08 g/s are not resolved. This is the scatter within one run; the run-to-run scatter from random injection positions was not measured.
- **Common window.** The 40 kHz row was first computed over 120–140 µs. Over 125–145 µs, the window of every other case, it also matches the control (0.116 against 0.116). Its 145 µs save alone is low (see below).
- **Plane choice.** With y < 20 mm, y < 30 mm, or at x = 110 mm, the ordering is unchanged. Pulsed cases stay within 0.002 of the control, and the jet-off loss at 120–130 µs stays between 22% and 34%.
- **Injected fuel.** The cloud reports match the nominal jet mass to 0.1%: 1.550 mg for `large_f40k` (nominal 1.551), 1.034 mg for `large_f80k` (1.034), and 20.67 g/s for `large_half` (20.68).
- **Solver logs.** No NaN, Inf or warnings in any run. The time step stays at 17 ns.
- **Front tracker.** The detonation base at each height is the first pressure rise of at least 30% of the largest one along the line that has CO2 > 0.02 within 1 mm behind it. The earlier tracker took the largest rise and, with a weakened or pulsed jet, sometimes picked the jet bow shock or a downstream compression instead (up to 14 mm off at 6 mm in `large_off_long`). Re-running every save (`scripts/checks/tracker_compare.py`) changed values at 2–9 mm by at most 0.6 mm, apart from those misidentified saves and the 2 mm values after the jet returns in step 2c, where the earlier tracker followed a jet shock with no burning behind it. At 1 mm the jet bow shock and the base are within a few cells of each other, so 1 mm positions are not used.
- **Control drift.** The control recovery falls from 0.137 at 70 µs to 0.113 at 145 µs. The liquid within 30 mm of the jet grows from 3.5 mg at 80 µs to 6.2 mg at 140 µs (`nearjet`), about 44 g/s against the 41 g/s the jet injects, so all of the jet liquid stays and some freestream liquid collects with it. It lies in a wall layer under 1 mm thick that reaches 70–80 mm at 100 µs and 80–90 mm at 145 µs (`liquid`). At 140 µs the pulsed, half-velocity and half-width jets hold 4.1–4.5 mg, and the 20 kHz jet 3.2 mg. The control is therefore not stationary, and every comparison is made at equal times.
- **Discriminating window.** Recovery responds to the jet only 35–50 µs after a change. Over 95–115 µs the jet-off run is still at 0.114 against the control's 0.120, a gap of only twice the noise floor; over 120–130 µs the gap is 0.036. So only windows from about 120 µs on can show whether a jet setting matters. The `large_f40k`, `large_f80k_long`, `large_f20k` and 125–145 µs `large_half` rows pass this test; the `large_f80k` row (the run ended at 120 µs) and the 100–110 µs `large_half` row do not.
- **End of `large_f40k`.** Its last save (145 µs) has the lowest recovery of the run, 0.104 against 0.113 for the control, about four times the noise floor. Over three cycles the downstream extreme of the base moved 0.8 mm further back. A bounded oscillation is not yet established.

The 40 and 80 kHz jets match the control within the noise floor at half the jet fuel, and both matches are verified in a window that separates jet on from jet off. They are not better than the control. At 20 kHz recovery falls by 8%, and without the jet by about 30%.

## Finding: jet liquid accumulates near the jet

Between 85 and 95 µs, the liquid within 30 mm of the jet grew by 219–223 µg every 5 µs. The jet injects 207 µg per 5 µs. The 4.1 mg present at 95 µs equals everything the jet has injected since the run started, and no parcels were found near the wall beyond x = 80 mm. The jet liquid breaks up into droplets of about 5 µm, collects in the cold, oxygen-depleted wall layer, and barely evaporates or moves downstream within 95 µs.

This has three consequences:

1. **The near-wall liquid is not yet steady,** even though the gas-phase front has been steady for over 50 µs. The residence estimate above (about 95–190 µs) is longer than the run.
2. **Paper Fig. 3c shows jet droplets along the whole wall downstream of the jet.** Ours stay within 30 mm of it. The likely cause is the droplet–wall interaction model (`rebound`), which the paper does not state.
3. **After the jet stops, this reservoir may keep blocking the flow,** so the measured hold time could depend on a modelling choice. Step 2a tests that directly.

## Reproducing

```
python -m pulswave build box_large cases/box_large
scripts/run.sh cases/box_large
python -m pulswave wave cases/box_large 7e-05
python -m pulswave nearjet cases/box_large 7e-05
python -m pulswave performance cases/box_large 7e-05 --x 100 --ymax 25

python -m pulswave branch cases/box_large cases/large_off 7e-05 --end 1.3e-4 --jet-off
python -m pulswave branch cases/box_large cases/large_off_escape 7e-05 --end 1.3e-4 --jet-off --wall escape
python -m pulswave branch cases/box_large cases/large_off_dry 7e-05 --end 1.3e-4 --jet-off --drop-jet-liquid
python -m pulswave branch cases/large_off cases/large_reon 9.5e-05 --end 1.3e-4 --jet-on
python -m pulswave branch cases/box_large cases/large_f40k 7e-05 --end 1.45e-4 --pulse 40000 0.5
python -m pulswave branch cases/box_large cases/large_f80k 7e-05 --end 1.2e-4 --pulse 80000 0.5
python -m pulswave branch cases/box_large cases/large_half 7e-05 --end 1.45e-4 --jet-on --jet-u 30.415
python -m pulswave branch cases/box_large cases/large_narrow 7e-05 --end 1.45e-4 --jet-on --half-width
python -m pulswave branch cases/box_large cases/large_f20k 7e-05 --end 1.7e-4 --pulse 20000 0.5
python -m pulswave branch cases/box_large cases/large_f80k_q 7e-05 --end 1.45e-4 --pulse 80000 0.25
python -m pulswave branch cases/large_half cases/large_half_long 0.000145 --end 2e-4 --jet-on
python -m pulswave branch cases/large_off cases/large_off_long 0.00013 --end 2e-4
python -m pulswave branch cases/large_f80k cases/large_f80k_long 0.00012 --end 1.45e-4 --pulse 80000 0.5
python -m pulswave build crop_grid cases/crop_grid
python -m pulswave build crop_grid_fine cases/crop_grid_fine
scripts/run.sh cases/crop_grid
scripts/run.sh cases/crop_grid_fine
python -m pulswave branch cases/crop_grid cases/crop_grid_off 5e-05 --end 9e-05 --jet-off
python -m pulswave branch cases/crop_grid_fine cases/crop_grid_fine_off 5e-05 --end 9e-05 --jet-off
python -m pulswave build crop_grid_d1 cases/crop_grid_d1
scripts/run.sh cases/crop_grid_d1
python -m pulswave branch cases/crop_grid cases/crop_grid_f80k_q 5e-05 --end 9e-05 --pulse 80000 0.25
python -m pulswave branch cases/crop_grid cases/crop_grid_quarter 5e-05 --end 9e-05 --jet-on --half-width --jet-scale 0.5
python -m pulswave branch cases/crop_grid_d1 cases/crop_grid_d1_off 5e-05 --end 9e-05 --jet-off
scripts/run.sh --restart cases/<branch>
```

The analysis behind each table:

```
python -m pulswave wave cases/<case> <t...>                                  # base positions, pressure ratios
python -m pulswave performance cases/<case> <five saves> --x 100 --ymax 25 --duty <D>   # Verified performance
python -m pulswave performance cases/box_large 0.00012 0.000125 0.00013 --x 100 --ymax 25 --by-height   # recovery by height
python -m pulswave performance cases/large_off_long <t...> --x 100 --ymax 25 --check     # step 2d plane validity
python -m pulswave nearjet cases/<case> <t>                                  # step 0, liquid near the jet
python -m pulswave pocket cases/box_large 8e-05                              # pocket state, loading, volume fraction
python -m pulswave liquid cases/box_large 0.0001 0.000145                    # wall-layer extent
python scripts/checks/liquid_edge.py cases/<crop case> <t...>                # base follows the wall liquid
```

The manuscript figures: `figdata` extracts the data behind every figure into JSON (pure Python, run where the cases are, about 15 min on 8 processes), and `paper/figures.py` plots it (needs matplotlib and numpy). The case root holds `open_wedge_J1_paper` and `boxes/`.

```
python -m pulswave figdata <case root> paper/data            # --only <case> --force to redo one case
python paper/figures.py                                      # writes paper/figures/*.pdf
```

The jet-on control continues `box_large` itself past its 80 µs preset end: set `endTime` to `1.45e-4` in `cases/box_large/system/controlDict`, then run `scripts/run.sh --restart cases/box_large`. `large_off_escape` was stopped at 80.9 µs and `large_off_dry` at 90 µs, once each had answered its question.

Each branch writes its parameters to `setup.json`.
