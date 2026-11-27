# ITERATION_LOG.md: what was adjusted, why, and what it did

Speculative modeling / architecture testbed only. Times are PT, 26 Nov 2026.

## Build phase
1. **Port of the v4 architecture.**
   - Copied from v4 (read only) and re-mapped to brains and foci: counter-based RNG, Genesis/Nexus/Transcriber/Levy, sponge (both layers), layer interface, background processors, update sequence, stop rule.
   - The v3/v4/v5 directories were not modified.
2. **Attribution fix (R2).**
   - First version: a trigger counted as "reported" whenever a seizure fell in its exposure window.
   - Result: attribution of high-frequency exposures was absurd (weather about 45%, music about 89%), and catamenial and missed medication were too high.
   - Fix: added the **perceived-excess rule** (seizure-day share ≥ 1.5 × background share; the ratio is an assumption) and used it for calibration.
   - The naive rule is kept as `attrN_*` to show misattribution.
3. **No clusters.**
   - The first version produced almost no ≥3-per-day days.
   - Fix: added same-day cluster branching (`cluster_b`, up to 6 generations). Motivated by seizure self-triggering (Osorio 2010) and SeizeIT2 over-dispersion.
4. **Observer-dependent dynamics bug.**
   - Yesterday's discharge count (used by the inhibition layer) was only computed when observers were attached, so runs with and without observers diverged.
   - Fix: it is now always computed. Preflight checks that observers change nothing.
5. **Infrastructure fixes.**
   - pyarrow missing: switched to pickle (`.pkl.gz`).
   - Shell noclobber: used `>|`.
   - WHO page fetch timed out: retrieved with curl.

## Calibration phase (22:00–22:15 PT, 26 Nov)
6. **Four scenarios** (FULL/CORE × anchored/free multipliers): Nelder–Mead, 200 evaluations each, n = 3,000, seed 101.
   - Every proposal passed through the torch (syntax autocorrect, i.e. clipping of probabilities and positive keys).
   - Each new best iterate (146 in total) ran the full update sequence.
   - Each final set was written with `apply_update` (4 writes).
   - The same log also records 57 harness registrations.
   - All 207 records in `data/update_sequence_log.jsonl` verified (exact undo; identical redo; 0 corrections needed).
7. **Weak identifiability.** resp_frac and cluster_b stayed at 0.500 and 1.000 in all scenarios. Other parameters (base rate, exposures) absorbed the fit.
8. **Target tension.** MAIN is in band for 5 of 9 targets.
   - Seizure freedom ends about 1.4 pt above its band.
   - Stress attribution ends about 1 pt below its band.
   - Missed medication and illness attribution end above their bands.
   - Kept and reported, not forced.
9. **Choice of MAIN.** FULL_anchored was chosen because the brief is to exercise the full architecture, and its stress and sleep multipliers are tied to the Haut diary ORs.
   - CORE scenarios fit more targets (7/9).
   - On validation seeds, only CORE_free scored better than MAIN (0.282 vs 0.353); CORE_anchored was worse (0.385).
   - Reported honestly in RESULTS_SUMMARY §2.

## Steering: cell shading (requested 22:13 PT, 26 Nov)
10. **Search for an existing definition.**
    - Searched Caitlyn's GitHub (code search "shading", "cel shading", "shade") and the local workspace.
    - Only graphics-shader mentions were found; no transcript record.
    - A **provisional** cel-shading definition was therefore added as a switchable layer (CELL_SHADING.md).
11. **Placement.** Added *after* calibration as an **observational** layer (feedback 0).
    - Preflight proves outcomes are bit-identical with it on or off, so the calibration stays valid.
    - Shade reconciliation (`_sig_shade`, `shade_recon_bad`) was added to every condition's verification.
    - Coupled variants (feedback 0.25 / 0.5 / 1.0, sponge-off control, coarse bands) were added to the experiment list.
12. **Preflight re-run** (22:20 PT): 50/50 PASS, including the shading checks.

## Main runs (26 Nov, ~22:20–22:30 PT)
13. **Main conditions.** 117 conditions, 7 processes, about 210 s; all stopped on precision; 1.13 million person-runs; 0 reconciliation failures.
14. **No-history psilocybin cohort.**
    - The base rate was found by pilots (20,000-person batches) to match 61.44 per 100k per year. Achieved 75 per 100k [58, 97].
    - Then 6 arms, 80,000–120,000 people each.
15. **Post-processing.**
    - Ran `contrasts.py` (paired contrasts and synergy), `charts.py` (charts 01–09) and `final_observables.py` (observables with CIs vs bands).

## Known limitations / possible next iterations
- No ASM switching, age, syndrome, or mortality.
- Trigger magnitudes for drugs, psilocybin and photic/music are assumptions.
- The no-history SSRI+psilocybin arm lacks an SSRI-only control.
- Attribution depends on the assumed perceive_ratio.
- Cell shading should be replaced with Caitlyn's own definition if she has one.

## Gate reexamination (27 Nov 2026, PT)
16. **Balabandian et al. 2025 verified** against Europe PMC full text (PMC11851161). All of the user's
    mechanistic points confirmed: 3 mg/kg i.p. anticonvulsant (PTZ CST + MES), a 3–5 mg/kg *window* (10–20
    ineffective), 5-HT1A up / 5-HT2A unchanged / IDO & CB1 downregulated, and five blockers (AM-251, 1-MT,
    L-NAME, sildenafil, naltrexone). No contradictions; only additions (dose window, the CB1 expression-vs-
    antagonist subtlety, IDO downregulation). `PUBLIC_DATA_INPUTS.md` line 68 was already correct; enriched it.
17. **Mapped to a candidate on/off `gate` layer** (`GATE_NOTE.md`): engages in a dose window with all pathways
    intact and a 9-day latch; channels = `rec_mult` (CST/recruitment threshold), `dorm_mult` (relapse gate),
    `perm_mult` (persistence). Off by default. Deliberately plugs into the **relapse gate**, the lever the
    completed run already identified as the sponge's dominant channel. Test plan = toggle + per-pathway ablation
    (reproducing each antagonist) + dose sweep (inverted-U) + sponge on/off, under the existing adaptive
    precision stop rule and exact delta reconciliation. Illustrative micro-check only; full run not executed.
    Publication text left in `paper_addendum_gate.md` (paper/ not touched).
