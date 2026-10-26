# Campaign scripts

How the second-instance runs (Oct 2026) were built and launched. Cases live in `$BOXES` (default `~/PULSWAVE/cases/boxes`).

| Script | Does |
|---|---|
| `build_new.py <case>...` | Branches the listed cases from their parents with `pulswave.build.branch` (pulse trains phase-locked to the parent's) |
| `build_mapped.py <case>...` | Cases on a new mesh (0.1 mm crop, patch half-width): builds the mesh, maps the parent state with mapFields, carries the injector state over |
| `audit.py <case>` | Checks a built case before launch: injector names and saved state, parcel rates, decomposition |
| `queue.sh <case>...` | Launches the cases in order as cores free up, dropping any that fail the audit |

`crop_off_np1` was changed by hand after `build_new.py`: its first build overflowed the injector's int32 parcel rate (a floating-point exception at startup), so the jet was split into two injectors (`jet0`, `jet0b`, each `parcelsPerSecond` 1.442e9) and the freestream injectors run at 3x parcels with `nParticle` 3.333333. Cases from before this campaign were built with `python -m pulswave branch`. Each case's exact settings are in its archived `setup.json` and `constant/sprayCloudProperties`.
