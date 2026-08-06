# baseline case

Reproduction attempt of Wang/Hu/Zhang (2026), continuous jet, confined
combustor. See docs/case-spec-confined.md for source values.

## Status

- [x] first-pass blockMeshDict (2-block, ramp geometry)
- [ ] transverse jet inlet patch (50 mm downstream of lip, R_j = 5 mm) --
      not yet added to blockMeshDict, needs a third block or a patch
      split on lowerWall
- [ ] thermophysicalProperties (n-heptane/air, 44-species mechanism)
- [ ] chemistry mechanism file (Liu, Hewson, Chen & Pitsch 2004)
- [ ] injection properties (Rosin-Rammler, 10 micron mean, Abramzon-
      Sirignano evaporation, Pilch-Erdman breakup)
- [ ] initial/boundary field files (0/)
- [ ] fvSchemes / fvSolution (KNP scheme, first-order Euler, CFL < 0.3)
- [ ] controlDict

## Mesh notes

Cell count at 0.3 mm spacing: ~367x440 + 906x440 = ~561,000 cells. Same
order of magnitude as the ~625k reported for the related open-wedge case
(Wang/Hu/Zhang, arXiv:2506.15247) -- consistency check only, not a match
to this paper's actual mesh, which is not stated as a cell count.

Upper wall (cowl) shape downstream of the ramp is assumed parallel to the
ramp at constant channel height. This is not given in the paper (see
docs/case-spec-confined.md, Open items) and is the single largest source
of geometric uncertainty in this mesh.
