# PREFLIGHT.md: component and switch checks before the main runs

Speculative modeling / architecture testbed only. No clinical claims.

Run 2026-11-26 10:20 PM PT on parameter set `data/calibration/params_FULL_anchored.json`. Result: **50 PASS, 0 FAIL**.

| Area | Check | Result | Detail |
|---|---|---|---|
| core | Genesis root identity registered; Nexus recombined every day | PASS | recombinations 730 / days 730 |
| core | Levy ledger total equals sum of per-person weighted events | PASS | Levy total 255364 |
| core | all five Levy event kinds occur (clear/detach/fail/colonize/exit) | PASS | {'clear': 108689, 'detach': 10895, 'fail': 7463, 'colonize': 3390, 'exit': 2006} |
| core | census (active+quiescent+cleared+held foci = all foci) | PASS | 1102 foci |
| core | mesh consensus (Levy ledger == heat-trace == daily seizure matrix, every focus) | PASS |  |
| core | Transcriber/Dictator chronicle records critical events | PASS | 119 entries, e.g. [(2, 'seizure x3', 2, 0), (11, 'seizure x1', 2, 3)] |
| core | salience gate + homeostasis (post-ictal refractoriness) active: switching it off changes runs | PASS |  |
| delta reconciliation | whole vs 2 independent parts bit-identical (sponge ON, all layers ON) | PASS |  |
| delta reconciliation | whole vs 2 independent parts bit-identical (sponge OFF, all layers ON) | PASS |  |
| delta reconciliation | whole vs 3 independent parts bit-identical (sponge ON, all layers ON) | PASS |  |
| delta reconciliation | whole vs 3 independent parts bit-identical (sponge OFF, all layers ON) | PASS |  |
| background | 4 background processors + bookkeeping sponge attached leave the run unchanged | PASS | bg_diag_fail=0, bg_stagnant_max=3, bg_memory_digest=8ec6e95a9d59, bg_memory_grown=730, bg_offdominant_seizure_share=0.2890855457227139, bg_corr_discharge_levy=0.916806026689746 |
| sponge (bookkeeping) | conservation (inflow = released + squeezed + spill) and reconciled Levy stream = model Levy | PASS | spill 0.0 |
| sponge (biological) | conservation absorbed = released + squeezed + held (Levy units) | PASS | absorbed [7840.0, 4072.0], released [7546.0, 3864.0] |
| layer | all switches False == layers absent (core model) | PASS |  |
| layer | sponge toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | materials toggle (sponge OFF): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| layer | materials toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | physics toggle (sponge OFF): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| layer | physics toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | heat toggle (sponge OFF): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| layer | heat toggle (sponge ON): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| layer | inhibition toggle (sponge OFF): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | inhibition toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | hpa toggle (sponge OFF): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | hpa toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | kindling toggle (sponge OFF): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | kindling toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | network toggle (sponge OFF): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | network toggle (sponge ON): disabled==absent; enabled changes runs; whole-vs-parts OK | PASS | changed=True |
| layer | shading toggle (sponge OFF): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| layer | shading toggle (sponge ON): disabled==absent; enabled neutral (expected); whole-vs-parts OK | PASS | changed=False |
| cell shading | whole-brain shade = reconciled aggregate of the parts every day; Levy by shade band sums to Levy total | PASS | recon mismatches 0 |
| cell shading | shade raster, band raster and Levy-by-band bit-identical whole vs 3 parts | PASS |  |
| cell shading | coupled variant (feedback 0.5 -> sponge) changes runs; observational default does not | PASS |  |
| cell shading | coupled variant is neutral with the sponge OFF (it acts only through the sponge) | PASS |  |
| instance | SSRI neutral (mult 1.0, no stress relief): bit-identical to baseline (neutral by construction) | PASS | changed=False |
| instance | SSRI observational OR 1.48: changes runs | PASS | changed=True |
| instance | stimulant HR 0.73: changes runs | PASS | changed=True |
| instance | NSAID neutral on illness: bit-identical to baseline (neutral by construction) | PASS | changed=False |
| instance | psilocybin high exacerbation: changes runs | PASS | changed=True |
| instance | recreational drug x5: changes runs | PASS | changed=True |
| instance | stress OFF: changes runs | PASS | changed=True |
| instance | musicogenic cohort: changes runs | PASS | changed=True |
| update sequence | six steps: staged quick fix, UPDATE ALL, hash-verified undo, PT timestamp, identical re-apply, torch->autocorrect | PASS | corrections 2 (numeric string -> number, clamp 1.2 -> 1.0), timestamp 2026-11-26T22:20:09-08:00 |
| update sequence | non-finite update rejected (not committed) | PASS | committed=False |
| update sequence | active inside calibration (every accepted best-iterate passed the sequence, all verified) | PASS | 146 iterate records |
| stop rule | adaptive batches stop on CI half-width (test target 0.06) | PASS | batches 2, persons 400, recon_bad 0, obs_bad 0 |
| stop rule | cap honoured (cap 3 batches) | PASS | reason cap |
| stop rule | configured for main runs | PASS | target half-width 0.01 on P(seizure-free 12 m), P(residual risk), P(eliminated); batch 2000 persons; min 3 batches; cap 20 batches |
