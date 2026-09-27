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
- **Numerical settings:** the flux scheme is read from `fluxScheme` in `fvSchemes` (Kurganov, Tadmor, HLL, HLLC, HLLCP, AUSMPlus or AUSMPlusUp). The species and energy transport uses `div(rhoPhi,Yi_h)`, and every other `div` term uses the default scheme.

## Pitfalls

- **Energy setting:** with `energy sensibleEnthalpy` the solver runs without error, but shocks come out about 15% too cold. A published validation case exposes it immediately.
- **No active injectors:** an empty `injectionModels` list, or an injector with a near-zero mass flow, fails with a floating-point exception while the cloud is set up. Gas-only cases need a dormant injector.
- **Mapping drops droplets:** `mapFields -parallelSource` maps the gas fields but drops almost all Lagrangian parcels (it kept 35 of about 30,000). A mapped spray case starts droplet-free near the jet for about 25 µs, and across the full domain for about 110 µs. Check `grep parcels log.mapFields` after any mapping, or start from uniform freestream.
- **Process matching over SSH:** `pgrep -f "detonationFoam_V3.1 -parallel"` also matches the remote shell running the command, so killing its matches ends the SSH session. Match `^/usr/bin/mpirun` or `^detonationFoam_V3.1 -parallel` and filter by `readlink /proc/<pid>/cwd`.
- **Detached launch:** `scripts/run.sh` starts the solver with `setsid nohup ... < /dev/null &` so the run survives a dropped SSH session.
- **Parcel-rate limit:** `parcelsPerSecond` must stay below about 2.1e9 per injector (the 32-bit label limit).
