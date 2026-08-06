# Liu, Hewson, Chen & Pitsch (2004) n-heptane mechanism

Source: S. Liu, J.C. Hewson, J.H. Chen, H. Pitsch, "Effects of Strain
Rate on High-Pressure Nonpremixed N-Heptane Autoignition in
Counterflow," Combust. Flame 137 (2004) 320-339.

Cited by the reproduction target paper (arXiv:2506.15247, Sec 2.1) as
"a skeletal reaction mechanism comprising 44 species and 112
reactions."

## Files

- `nHeptane_allstarnew_oks.chmech` -- Chemkin gas-phase mechanism
  (elements, species, reactions)
- `nHeptane_allstarnew_oks.chthermo` -- Chemkin NASA-7 thermo data
- `nHeptane_allstarnew_oks.chtrans` -- Chemkin transport data
- `heptane-liu-hewson-chen-pitsch-highT.yaml` -- Cantera YAML, sourced
  from Sandia's Spitfire project, high-T only (38 species / 105
  reactions). Retained for thermo cross-checking only. Not used as
  production chemistry.
- `convert_to_chemkin.py` -- copies the `.chmech/.chthermo/.chtrans`
  triplet to `chem.inp/therm.dat/transportProperties` for
  `chemkinToFoam`.

## Verification (2026-08-04)

Source: professor-provided files, received directly, not the
Spitfire/Cantera route.

- Species: 44, exact match to paper.
- Reactions: 112, exact match to paper.
- All 6 low-T peroxy/hydroperoxide species present and active in
  reactions: `PC7H15O2`, `PHEOOHX2`, `SOO7OOH1`, `PX2HEOOH`, `OC7OOH`,
  `PX2HEPOO`.
- Full chain intact: `PXC7H15/SXC7H15 + O2 -> PC7H15O2 -> PHEOOHX2 ->
  SOO7OOH1 -> PX2HEOOH -> OC7OOH + OH -> PX2HEPOO + OH -> CH2O +
  PXC5H11 + CO`. This is the low-T chain-branching pathway needed for
  the J = 0.1-0.3 regime (case-spec-open-wedge.md Sec 3.3, paper's
  Fig. 6). Species naming differs from the paper's KET/ORO2H labels
  (here: `OC7OOH`/`PX2HEPOO`), not yet cross-checked against the
  paper's SI species table.
- `.chthermo`: 44 complete 4-line NASA-7 records, standard fixed-column
  format (80-char lines, sequence digit in col 80).
- `.chtrans`: 44 species, matches mechanism species list exactly.
- `.chmech` reactions are free-format tokenized; not fixed-column
  sensitive.

This supersedes the earlier Spitfire-derived file as production
chemistry.

## Open items

- Cross-check species naming against paper's SI (or Guo et al.,
  arXiv:2202.04987, ref [15]) to confirm no renaming/merging occurred
  between the paper's mechanism and this copy.
- Run through `chemkinToFoam` against the open_wedge case mesh.