# open_wedge_smoke

Coarse, short-duration version of `cases/open_wedge`, for validating the
pipeline (mesh -> jet patch -> injection -> evaporation -> chemistry ->
parallel decomposition) before running the real 625,000-cell case.

Mesh: 250 x 100 cells at 1 mm (25,000 cells), same 0.25 x 0.1 m domain
and 2 mm z-depth as the real case. `endTime = 2e-6 s` -- well short of
the ~1e-4 s flow-through time, enough only to confirm the pipeline runs
without crashing.

**Not physics-validated.** Jet patch is 2.5x wider than the real case's
cut patch (coarser mesh forces a wider minimum slot). Don't compare
results here to the paper.

## New/changed vs. the real case

- `system/blockMeshDict` -- coarse mesh, from the spec in
  `docs/case-spec-open-wedge.md`
- `system/topoSetDict` -- selects the lowerWall face nearest x=0.05 m.
  Verify `jetFaces` = 1 face after `topoSet`/`checkMesh`.
- `system/createPatchDict` -- same pattern as the real case
- `system/controlDict` -- short endTime, same adjustTimeStep/maxCo,
  plus a maxDeltaT safety clamp
- `system/decomposeParDict` -- scotch, 16-way
- `constant/sprayCloudProperties` -- same submodels as the real case;
  massTotal/parcelsPerSecond recomputed for this patch's area/duration,
  using the real injection rate (not the 10x diagnostic cut)

## Copy unchanged from cases/open_wedge/

Mesh-independent, same patch names in both meshes:

```
cp -r ../open_wedge/0                                  ./0
cp    ../open_wedge/system/fvSchemes                    ./system/
cp    ../open_wedge/system/fvSolution                    ./system/
cp    ../open_wedge/constant/g                            ./constant/
cp    ../open_wedge/constant/momentumTransport             ./constant/
cp    ../open_wedge/constant/combustionProperties           ./constant/
cp    ../open_wedge/constant/solverTypeProperties             ./constant/
cp    ../open_wedge/constant/chemistryProperties                ./constant/
cp    ../open_wedge/constant/thermophysicalProperties             ./constant/
cp    ../open_wedge/constant/reactions                               ./constant/
cp    ../open_wedge/constant/speciesThermo                             ./constant/
```

## Run

```
apptainer shell detonationfoam.sif
cd cases/open_wedge_smoke

blockMesh
topoSet
checkMesh                    # jetFaces = 1 face
createPatch -overwrite

decomposePar
mpirun -np 16 detonationFoam_V3.1 -parallel
reconstructPar
```

## Checks

- `jetFaces` = 1 face after `topoSet`/`checkMesh`
- `mass introduced` / `number of parcels added` go nonzero within the
  first ~15-20 ramped-up steps
- `min/max(T)`, `min/max(p)` stay bounded (freestream 697 K / 2.855e4 Pa,
  no NaN, no runaway)
- wall-clock/step, to extrapolate real-case cost