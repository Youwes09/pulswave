# open_wedge case

Reproduction target: Wang/Hu/Zhang (2025/2026), arXiv:2506.15247 --
J = 1.0 reactive C7H16 jet, oblique detonation wave (ODW) formation.

Numeric sourcing for every value in the case files: `docs/sourcing.md`.
Case spec summary: `../../docs/case-spec-open-wedge.md`.

## Directory guide

Three `chemkin*` directories exist and are not interchangeable:

- `chemkin/` -- reserved for the real 44-species/112-reaction n-heptane
  mechanism (Liu, Hewson, Chen & Pitsch 2004). Not yet sourced; see
  `chemkin/README.md`. This is the only directory whose output should
  feed a result compared against the paper.
- `chemkin_placeholder/` -- LLNL's 159-species reduced mechanism.
  Abandoned: didn't match OpenFOAM chemkinReader's fixed-column NASA-7
  format. Kept as a record, not deleted.
- `chemkin_smoketest/` -- currently active. Copied from OpenFOAM-8's
  aachenBomb tutorial (5 species, 1 global reaction). Proves the
  pipeline runs; has no relation to the paper's chemistry.

## Status

- [x] Mesh: blockMesh + checkMesh clean, 625,000 cells, 0.2 mm
- [x] Jet patch cut via topoSet/createPatch (x = 0.05 m; actual width
      0.4 mm vs. nominal 0.5 mm -- see `docs/sourcing.md`)
- [x] 0/U, 0/T, 0/p -- jet patch is slip (droplets enter via
      Lagrangian injection, not Eulerian inflow)
- [x] 0/Ydefault + per-species Y fields, values are smoke-test
      placeholders, not paper-sourced
- [x] constant/g, momentumTransport (laminar), solverTypeProperties
      (NSSpray_Sutherland)
- [x] constant/combustionProperties (laminar closure model)
- [x] constant/chemistryProperties, thermophysicalProperties --
      structurally matches detonationFoam's createFields.H and the
      aachenBomb reference case; points at chemkin_smoketest/
- [x] constant/reactions, speciesThermo -- generated via chemkinToFoam
      from chemkin_smoketest/ (see `docs/sourcing.md` for parser
      gotchas)
- [x] constant/sprayCloudProperties -- patchInjection + PilchErdman +
      RanzMarshall + liquidEvaporation + sphereDrag
- [x] fvSchemes / fvSolution -- verified against
      solverTypeNSSpray_Sutherland/*.H
- [ ] Mid-debug: sprayCloudProperties submodel Coeffs subdicts. B1/B2
      was the first missing mandatory coefficient; RanzMarshallCoeffs,
      liquidEvaporationCoeffs, standardWallInteractionCoeffs not all
      individually verified yet.

## Known limitations

- Jet patch is 0.4 mm (2 cells at 0.2 mm resolution), not the paper's
  0.5 mm -- not an integer multiple of the cell size at this
  resolution. sprayCloudProperties massTotal uses the actual 0.4 mm
  width, so it's internally consistent but not an exact geometric
  match. Revisit with local mesh refinement if results prove sensitive
  to this.
- chemkin_smoketest/ mechanism has no relation to the paper's
  chemistry; no result from this mechanism is comparable to the paper.
- OpenFOAM v7 (paper's solver) vs. v8 (this build) equivalence is
  unverified.

Full list of unreconciled items: `docs/sourcing.md`.

## How to use

1. Copy `cases/open_wedge/` into the running `detonationfoam.sif`
   container.
2. From the case directory:

   ```
   blockMesh
   checkMesh
   ```

3. Cut the jet patch (already done once; from scratch):

   ```
   topoSet
   createPatch -overwrite
   checkMesh
   ```

4. Generate chemistry files from the active mechanism
   (chemkin_smoketest/ currently; swap to chemkin/ once sourced):

   ```
   chemkinToFoam chemkin_smoketest/chem.inp chemkin_smoketest/therm.dat \
                 chemkin_smoketest/transportProperties \
                 constant/reactions constant/speciesThermo
   ```

5. Run:

   ```
   detonationFoam_V3.1
   ```

   As of this writing, this reaches submodel construction (mesh,
   thermo, chemistry, injection, distribution model all initialize)
   before failing on a missing mandatory coefficient in
   sprayCloudProperties' Coeffs subdicts. Read the first error message;
   it names the missing/wrong keyword.

6. Inspect results:

   ```
   foamToVTK
   paraFoam
   ```