# Status

Last updated 2026-09-27.

## Where things stand

- **Validation:** the solver, chemistry and setup are checked against theory, two published cases, and the open-wedge paper's vapour and no-jet cases. See [validation.md](validation.md).
- **Full J = 1 run:** the open-wedge baseline (`paper_j1`, arXiv:2506.15247 Fig. 3c) is running on AWS, reached 91 µs on 2026-09-27, and reproduces the paper's mechanism. Near the jet the front sits 1–2 mm below the paper's; the upper front is still converging.
- **Confined baseline:** the confined-combustor baseline (arXiv:2605.27871) is not started. Its specification is in [case-spec-confined.md](case-spec-confined.md).

## Next steps

1. Finish `paper_j1` at 100 µs, and at 130 µs if the upper front is still converging. Copy the key saves off the instance.
2. Compute the continuous-jet baseline metrics from `paper_j1`: total-pressure loss across the domain, and the jet fuel flow against the freestream fuel flow. The pulsed study is measured against these.
3. Re-check the literature gap, last checked on 2026-09-07.
4. Choose the next route:
   - a pulsed-jet pilot on the validated open wedge, screened in crops and confirmed on the full domain at selected frequencies; or
   - reproduce the confined-combustor baseline first, as originally planned.
