# Gas-speed criterion: out-of-sample predictions (written 2026-10-25 before extraction)

Statistic: median over all saves of a case of the mean gas ux in x 50-52 mm, y < 1 mm (as in rule_extract2 / rule_gas2).
Fitted on the 24 rule2 cases. Thresholds fixed now: HOLD if median <= 450 m/s, FAIL if >= 520 m/s, GREY between.
Outcome (judged separately from the front): HOLD if base y4 stays within ~1 mm of its jet-on reference to the end; FAIL if it retreats beyond that.

Test cases, jet on throughout (pulsed or steady), not used in fitting:
- crop_grid_d1 (1 mm jet, steady): expect HOLD
- large_half, large_half_long (half velocity, J = 0.25): expect FAIL
- large_reon (jet off then back on): judge on the re-on segment
- crop_grid_f80k_q, large_f80k_q (25% duty pulsing): expect FAIL
- earlier segments of chains already fitted (large_f80k, large_f80k_long, large_f40k, large_f20k, large_narrow): consistency check only, not independent
- box_small: whatever it shows, reported

Jet-off drains (crop_grid_d1_off, large_off*, crop_grid_off, crop_grid_fine_off) are trivially FAIL with high late gas speed; they test nothing and are reported only.

## Result (2026-10-25)
Correct: large_half 710 FAIL (front 51.3 -> 60.5 mm), crop_grid_f80k_q 539 FAIL (-> 55.3), crop_grid_d1 131 HOLD (50.3).
Partial: large_reon 268 HOLD, retreat halts but the front stays ~3 mm back.
Missed: early segments large_f40k 369, large_f20k 232, large_narrow 377 call HOLD while the front drifts 2-3 mm.
The per-case median depends on how many saves precede the perturbation, so it is not a usable criterion.
Instantaneous plug gas speed rising above ~500 m/s leads every retreat (half 90 us, cone 135 us, 25% duty 65 us), but pulsed cases also spike transiently and recapture.
Use: a diagnostic time series beside the front, not a threshold rule.
