# Solver notes

The solver is detonationFoam, branch `detonationFoam-dev(two-phase)` at commit `02ed90db0a17`, built on OpenFOAM-8 `a86b07b9dabb`. The executable is `detonationFoam_V3.1`, with `solverType NSSpray_Sutherland`.

## Internals

- **Energy variable:** `createFields.H:19` uses `thermo.he()` as the internal energy e, so the case must set `energy sensibleInternalEnergy`.
- **Time step:** `detoCellular.H` is the only place that calls `setDeltaT`. Growth is limited to 1.2× per step, and it uses the Courant number from the previous step. `calculateDt.H` only computes and prints that Courant number.
- **Time-step loop** (`solverTypeNSSpray_Sutherland.H`), in order:
  1. `detoCellular.H`
  2. `runTime++`
  3. `mesh.update()`
  4. `calculateDt.H`
  5. `parcels.evolve()`
  6. flux update
  7. solve rho, rhoU, rhoY, rhoE
  8. transport correction
  9. write
  10. shock-position scan (it stops the run when the shock passes `SW_position_limit`)
- **Chemistry integration:** `seulex` with `absTol` and `relTol` from `constant/chemistryProperties` (`odeCoeffs`). The solver's defaults (about 1e-15 and 1e-4) make chemistry about 97% of the step time. The revision runs use absTol 1e-10 and relTol 1e-3 (`scripts/campaign/revision_settings.py`). With these settings the base was unchanged and the fields stayed within 0.4% over 75–85 µs, and `r_crop_off_tolctl` repeats the check over the hold at the default tolerances.
- **Numerical settings:** the flux scheme is read from `fluxScheme` in `fvSchemes` (Kurganov, Tadmor, HLL, HLLC, HLLCP, AUSMPlus or AUSMPlusUp). The species and energy transport uses `div(rhoPhi,Yi_h)`, and every other `div` term uses the default scheme.

## Pitfalls

- **Species convection built with the wrong flux:** in `rhoYEqn_NSSpray_Sutherland.H` the species convection scheme is constructed with the volumetric flux `phi` but transports the mass flux `rhoPhi`. In the Kurganov–Noelle–Petrova flux the two can differ in sign on a face, so the upwind weighting points the wrong way and the implicit species update is unbounded.
  - Symptoms: the n-heptane mass fraction exceeds 1 in dense near-wall spray cells (up to 7.2 in the original runs), and N₂, the inert remainder, is clipped at 0.
  - Fix: construct the scheme with `rhoPhi` ([container/patches](../container/patches/README.md)). With the fix, ΣY stays at or below 0.963 and the base is unchanged.
  - The same mismatch exists in the NS_Sutherland, Euler and NS_mixtureAverage species equations.
- **Energy setting:** with `energy sensibleEnthalpy` the solver runs without error, but shocks come out about 15% too cold. A published validation case exposes it immediately.
- **No active injectors:** an empty `injectionModels` list, or an injector with a near-zero mass flow, fails with a floating-point exception while the cloud is set up. Gas-only cases need a dormant injector.
- **Mapping drops droplets:** `mapFields -parallelSource` maps the gas fields but drops almost all Lagrangian parcels (it kept 35 of about 30,000). A mapped spray case starts droplet-free near the jet for about 25 µs, and across the full domain for about 110 µs. Check `grep parcels log.mapFields` after any mapping, or start from uniform freestream.
- **Mapping a spray case without losing droplets:** map from the reconstructed parent (`reconstructPar`, then `mapFields -consistent`) as `scripts/campaign/build_mapped.py` does; every parcel is kept. Between different domains (non-consistent `mapFields`) two more problems appear:
  - Only fields that already exist in the target are mapped. A new case has only the main species, so the minor species (CO, OH and the other radicals) would start at zero. Give the target a placeholder for every source field first.
  - Every parcel outside the target triggers a search of the whole mesh, which takes hours. Filter those parcels out of a scratch copy of the source.
  `build_revision.py` (`mapped_box`) does both and checks the mapped fields by name and the parcel mass.
- **Changing a patch on a decomposed case with parcels:** `createPatch` renumbers boundary faces and rotates processor faces. Saved parcels store the label of a face of their cell, so the run fails on its first step with "The search for an edge-connected face and tet-point failed". To change a boundary condition along part of a patch, keep the mesh and use a `mixed` condition with a per-face `valueFraction`.
  - Every processor must get the same patch type, including processors with no faces on that patch (with empty lists), because the `mixed` constructor calls a collective.
- **Process matching over SSH:** `pgrep -f "detonationFoam_V3.1 -parallel"` also matches the remote shell running the command, so killing its matches ends the SSH session. Match `^/usr/bin/mpirun` or `^detonationFoam_V3.1 -parallel` and filter by `readlink /proc/<pid>/cwd`.
- **Detached launch:** `scripts/run.sh` starts the solver with `setsid nohup ... < /dev/null &` so the run survives a dropped SSH session.
- **Parcel-rate limit:** `parcelsPerSecond` must stay below about 2.1e9 per injector (the 32-bit label limit).
