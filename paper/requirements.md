# Manuscript requirements

Derived from the papers this one sits beside, read in full:

- **[W25]** Wang, Hu & Zhang, arXiv:2506.15247, Aerosp. Sci. Technol. 168 (2026). The baseline we reproduce.
- **[W26]** Wang, Hu & Zhang, arXiv:2605.27871, submitted to Aerosp. Sci. Technol. The confined, oscillating-inflow follow-up.
- **[J25]** Jiang et al., arXiv:2508.08943. Continuous against pulsed energy deposition; defines f_cri.

Skimmed for conventions: Wang et al., Combust. Flame 271 (2025) (arXiv:2407.17714); Guo et al., arXiv:2212.07550 and 2201.03934.

## Venue

Aerospace Science and Technology (Elsevier, `elsarticle`). Both Wang papers went there, the readership knows the J = 1 case, and AST takes numerical parametric studies of this length. The fallback is Physics of Fluids. Combustion and Flame would want a stronger mechanism result than a 2D, single-geometry study can give.

AST asks for 3–5 highlights of at most 85 characters each, keywords, CRediT roles, a competing-interest statement and a data-availability statement. [W25] also carries a novelty-and-significance statement (a Combustion and Flame habit); AST does not require one, so it is omitted.

## Structure

The genre is rigid, and every comparable paper follows it:

1. **Title.** A noun phrase naming the system and what is varied. No question, no colon, no "towards" or "insights into". Pattern: [W25] "Liquid-fueled oblique detonation waves induced by reactive and non-reactive transverse liquid jets".
2. **Abstract.** One paragraph of 200–250 words. Order: what was computed and with what solver; the main findings in the order of the paper, each with its mechanism; the one quantitative headline; what it implies for the actuator. No citations, no undefined symbols beyond J, and at most one hedge.
3. **Introduction**, five or six paragraphs:
   - ODWE promise, then the initiation and anchoring problem;
   - a control taxonomy (geometric, energy deposition, fluidic), with citations grouped by type ([W26] uses exactly this split);
   - the extra difficulty of liquid fuels;
   - the transverse liquid jet and what is known about it ([W25], [W26]);
   - the gap: all liquid-jet work uses a steady jet, while unsteady actuation has been studied only for energy deposition ([J25]) and a gaseous sweeping jet (Fan et al.);
   - "The present study ..." with what is done, then a one-paragraph roadmap ("The rest of the paper is organized as follows.").
4. **Computational methodology:**
   - 2.1 governing equations and sub-models, compact, with equations numbered and citing [W25] for the identical set;
   - 2.2 configuration and conditions, with a table;
   - then whatever is specific to this study: the reduced domain, the branching and pulsing protocol, and the diagnostics;
   - a grid-independence subsection is mandatory. Every paper has one, and it uses profiles along a fixed streamline at 2–4 spacings.
5. **Results and discussion**, numbered 3.x, in the order phenomenon, then parameter effect, then mechanism. Each subsection opens by saying what it tests and why.
6. **Conclusions.** One paragraph restating the setup in a sentence, then the findings (paragraphs or a numbered list; Guo et al. number them), then a closing paragraph of limitations and extensions. [W26] opens that paragraph with "Three extensions merit investigation."
7. **Back matter:** CRediT, declaration of competing interest, acknowledgments, data availability, then references in Elsevier numbered style with DOIs where known.

## Language

Observed in all three papers, and required here:

- **Abbreviations.** Define each once, in the abstract and again in the text: ODW, OSW, ODWE, J. Use the field's own terms: "jet-inflow momentum ratio", "jet-induced OSW", "initiation length", "standing ODW", "wave structure", "anchored", "dynamically stabilized".
- **Tense.** Methods in the past or passive ("was performed", "is employed"); observations in the present ("Figure 4 shows ...", "the base retreats ..."). "We" is acceptable ([W26] uses it); use it sparingly and never as "we believe".
- **Figures.** Refer to them as "Fig. 3(a)" mid-sentence and "Figure 3" at the start of a sentence. Captions are long and self-contained: what is plotted, at which conditions, and every abbreviation used in the panel. [W26] and [J25] captions run three to six lines.
- **Result paragraphs.** Each one follows the same pattern: what the figure shows, then the observation with numbers and units, then the interpretation, then the bridge to the next question. [W26] Sec. 3.2 is the model.
- **Positions and times.** Give them as numbers with units ("x = 50.7 mm", "10 µs after switch-off"), not as "slightly downstream".
- **Hedging.** Hedge only where the data are thin, and say why. [W26] calls its stability map "an indicative regime diagram, not ... a sharply resolved neutral boundary". That is the register to use for the one-cycle 20 kHz run and the critical-frequency bracket.
- **Mechanism.** Name a mechanism only when a run isolates it. Here the dry-liquid run isolates the residual liquid's role, and the half-velocity and half-width runs separate J from fuel flow. Anything else is "consistent with" or "suggests".

## What makes it slop, and is banned

- **Unanchored intensifiers.** Words like "significantly", "substantially", "markedly", "dramatically" or "drastically" are banned unless a number follows in the same sentence.
- **Filler words.** These are banned outright: "crucial", "pivotal", "paves the way", "sheds light", "novel insights", "comprehensive", "robust", "holistic", "intricate interplay", "delve", "landscape", "underscores", "it is worth noting", "plays a vital role", "in the realm of".
- **Novelty claims.** "For the first time" appears in [W25] and [J25] but is not used here. The gap is stated as what the literature does not contain, with the search date.
- **Adjective triplets, and sentences that restate the previous one.**
- **Summary sentences** that close a paragraph by repeating its first sentence.
- **Generic future work** ("further studies are needed"). Each extension names the specific run or model that would answer it.
- **Numbers without a source.** Every number must trace to `docs/experiments.md`, `docs/validation.md`, `docs/assumptions.md` or a cited paper. If it does not, it is not in the paper.
- **Results promoted beyond their evidence.**
  - The 20 kHz result is one cycle.
  - The box is a reduced domain.
  - The 25% duty and 1 mm jet results are three cycles and one switch-off in the crop.
  - The narrow jet is one cell wide.
  - All of this is 2D, with a slip wall and no turbulence model.
  
  Each caveat sits next to the result it limits, not only in the conclusions.
- **Hidden negative results.** The finding that a half-width steady jet matches the pulsed jets at equal fuel goes in the abstract. It is what makes the frequency result honest.

## Content requirements

- **Contribution sentence.** The paper must state its contribution in one sentence that the abstract, the introduction's last paragraph and the conclusions all repeat in substance. That sentence is: the front base of a jet-anchored liquid ODW follows the liquid layer the jet leaves on the wall, so it holds for about 10 µs after the jet stops and then retreats as the layer slides downstream (more slowly for a wider jet); pulsing holds the base only when the off-time is short (critical frequency between 20 and 40 kHz at 50% duty) and each pulse is long enough to keep the layer at the jet (25% duty fails at 80 kHz); and at equal mean fuel a narrower steady jet at the same J matches pulsing in performance, though its base drifts by the end of the run, while a throttled jet settles about 10 mm downstream.
- **Prediction.** The 20 kHz estimate was made before the run. Say so, with the range and the outcome, and say why it is not a clean test (its upper range came from the 1 mm retreat speed, and the lag was longer than assumed).
- **Comparison with [J25].** Compare the critical frequency with their f_cri (8.5–25.6 kHz for pulsed energy deposition, falling with pulse energy), and explain why the two are not the same quantity.
- **Comparison with [W26].** Compare with their oscillating-inflow result (forcing the flow with a steady jet, against forcing the jet in a steady flow). Their 3–5 mm triple-point excursion at A = 0.5 is the right order to compare with ours.
- **Comparison with Fan et al.** Compare with the sweeping jet: theirs is never off and is gaseous.
- **Reproducibility.** The code, case setup and analysis are open (`pulswave`, detonationFoam commit). Say so in data availability.

## Figures planned

Each needs a script in `pulswave/` that produces it from the saved fields, so every figure can be regenerated.

1. **Schematic:** the domain, wedge, jet, reduced box, x = 100 mm measurement plane and the heights used for the base position.
2. **Reproduction:** front height against x, `paper_j1` and `box_large` against [W25] Fig. 3c.
3. **Jet-anchored baseline near the jet:** temperature with droplets, numerical schlieren, the subsonic pocket outlined.
4. **Base position after switch-off at 3 and 9 mm:** jet off, jet off without residual liquid, jet back on at 95 µs, and the control.
5. **Snapshots of the near-jet region:** 0, 10, 25 and 55 µs after switch-off.
6. **Base position at 3 mm against time:** 80, 40 and 20 kHz, with the jet-off windows shaded, plus the control and jet off.
7. **Excursion per cycle against off-time:** model band, observations, and the f_cri bracket.
8. **Recovery and burnt fuel over 125–145 µs for every case:** a bar chart with the noise floor marked, plus the recovery-by-height profile.
9. **Equal-fuel comparison:** base position against time for the half-velocity jet, the half-width jet and the pulsed jets.
10. **Grid check:** base position after switch-off at 0.2 and 0.15 mm.
11. **Mechanism schematic:** jet on, jet off within τ, jet off beyond τ, jet returning.
12. **Base and wall liquid:** base position against the 5/25/50% mass points of the wall liquid, for the 0.5 mm jet off, the 1 mm jet off and the 25% duty pulse.
13. **Jet width:** base position after switch-off for the 0.5 and 1 mm jets.

## Length

[W25] is about 8,600 words including references, and [W26] about 10,000. Target 7,000–8,500 words, 10–11 figures and 3–4 tables.
