# RESULTS_SUMMARY.md: Oroboro relational testbed adapted to epilepsy / seizure dynamics

**Speculative modeling / architecture testbed only.** Nothing here is a clinical claim, a risk estimate for any real person, or medical advice. The numbers describe a calibrated toy model that exists to exercise Caitlyn Randels' Oroboro architecture (Genesis, Nexus, Transcriber, Levy, state reduction, delta reconciliation, mesh, sponge, update sequence). They are not epidemiology.

Run 26 Nov 2026 (PT).
- **Main configuration (MAIN):** the FULL_anchored calibrated set, with all layers on, the sponge on, and cell shading on (observational).
- **Runs:** 117 conditions, all stopped on the precision rule (Wilson 95% half-width ≤ 0.01 on P(seizure-free 12 m), residual and eliminated), 1.13 million person-runs (730 days each), plus a no-seizure-history psilocybin cohort of 520,000 person-runs.
- **CIs:** all 95%. Contrasts are paired with common random numbers (same people, same random draws).

## 1. Integrity: every component active, reconciliation exact
- **PREFLIGHT.md:** 50/50 checks PASS. Every component is listed active:
  - Genesis, Nexus, Transcriber, Levy;
  - both sponge layers, and the 8 domain layers including shading;
  - the 4 background processors;
  - the update sequence;
  - the stop rule.
- **Delta reconciliation in all 117 conditions.**
  - Each condition was checked whole vs K = 2 parts, plus observer runs.
  - recon_bad 0, obs_bad 0, checks_bad 0, **shade_recon_bad 0**.
  - Whole-brain results are bit-identical to the recombined parts: census, Levy ledger, seizures, sponge fill, and shade.
- **Mesh consensus:** Levy ledger = heat-trace = seizure matrix in every run.
- **Bookkeeping sponge:** conservation OK and Levy matches the model in all 117 conditions. Bookkeeping spill (`bk_spill_levy`) was zero in 113 of 117 conditions. The four exceptions are the extreme musicogenic cohorts (`musicogenic_cohort_emotional0.2`, `musicogenic_cohort_emotional1.0`), the SSRI-for-everyone condition (`ssri_obsOR_all`), and high-dose psilocybin plus SSRI (`psilo_high_exacerb_plus_ssri`). Conservation and Levy-matching still held in those four.
- **Update sequence:** `data/update_sequence_log.jsonl` has 207 records (146 calibration iterates, 4 final writes, 57 harness registrations). All 207 ran quick fix → UPDATE ALL → undo (exact restore) → timestamp → do it again (identical) → syntax autocorrect, all verified; 0 corrections needed.

## 2. Calibration and fit (charts/01)
Four scenarios were run: FULL vs CORE architecture, with stress and sleep multipliers anchored to the Haut 2007 diary or left free. Each used Nelder–Mead, 200 evaluations, n = 3,000. Validation used fresh seeds with n = 10,000.

| Scenario | Calibration score | In band (of 9) | Validation P(SF 12 m) |
|---|---|---|---|
| FULL_anchored (MAIN) | 0.224 | 5 | 0.714 [0.705, 0.723] |
| FULL_free | 0.232 | 5 | 0.714 (+0.1 pt vs MAIN [−0.2, +0.3]) |
| CORE_anchored | 0.338 | 7 | 0.682 (−3.2 pt [−4.0, −2.4]) |
| CORE_free | 0.283 | 7 | 0.688 (−2.6 pt [−3.4, −1.8]) |

**Final reconciled observables (MAIN, 10,000 virtual brains; `data/final_observables.csv`):**

| Observable | Model [95% CI] | Public band | In band? |
|---|---|---|---|
| Seizure-free in last 12 m | **0.714** [0.705, 0.723] | 0.60–0.70 (Chen 2018 63.7%; WHO "up to 70%") | no, about 1.4 pt high |
| Cluster day (≥ 3 in 24 h) given still seizing | 0.282 [0.265, 0.298] | 0.149–0.43 | yes |
| Report stress as a trigger | 0.290 [0.278, 0.303] | 0.30–0.56 | no (just below) |
| Report sleep loss | 0.241 [0.230, 0.253] | 0.18–0.52 | yes |
| Report missed medication | 0.421 [0.408, 0.435] | 0.07–0.41 | no (just above) |
| Report illness/fever | 0.177 [0.167, 0.188] | 0.06–0.14 | no |
| Report catamenial (women) | 0.214 [0.199, 0.230] | 0.12–0.28 | yes |
| Report ≥ 1 trigger | 0.811 [0.800, 0.822] | 0.55–0.89 | yes |
| Report ≥ 2 triggers | 0.474 [0.461, 0.488] | 0.28–0.61 | yes |

Other observables (no public target):
- residual risk 0.688 [0.679, 0.697];
- eliminated (remission analogue) 0.026 [0.023, 0.029];
- seizures per person-year 1.77 [1.62, 1.92] (median 2 among those with any);
- mean Levy 414 per brain.

**Honest fit assessment.**
- The optimiser could not bring seizure freedom down into its band without pushing missed-medication and illness attribution further above theirs. Stress attribution sits just below its floor. These targets are in tension under this structure (see ITERATION_LOG).
- The validation score (0.353) is worse than the calibration score (0.224): some over-fit at n = 3,000.
- Both core scenarios (no sponge or layers) fit more targets (7/9). Only the core model with free multipliers validates better than MAIN (score 0.282 vs 0.353); the core model with anchored multipliers is worse (0.385). **The extra architecture does not uniformly improve the fit to public data.** It changes the mechanics (sections 6–8).
- resp_frac and cluster_b did not move from their starting values: they are not identifiable from these targets.
- The free stress and sleep multipliers converged to 1.237 and 1.256 (CORE_free sleep 1.331), close to the independent Haut anchors (1.26, 1.33). This is a weak but real consistency check.

## 3. Triggers (charts/02): paired removal effects on MAIN
Each row removes one trigger from the whole cohort.

| Trigger | Δ P(SF 12 m), pt | Δ seizures/person-yr |
|---|---|---|
| Missed medication | **+6.98** [6.40, 7.55] | −0.43 [−0.50, −0.36] |
| Stress | +1.77 [1.50, 2.04] | −0.22 [−0.25, −0.19] |
| Catamenial | +1.09 [0.88, 1.30] | −0.15 [−0.18, −0.12] |
| Illness/fever | +0.74 [0.57, 0.91] | −0.06 |
| Binge drinking | +0.68 [0.51, 0.85] | −0.05 |
| Sleep loss | +0.55 [0.40, 0.70] | −0.05 |
| Low pressure | +0.49 [0.35, 0.63] | −0.08 |
| Sensory overload | +0.10 [0.04, 0.16] | −0.01 |
| Photic | +0.02 [−0.02, 0.06] | −0.004 |
| Moderate alcohol | 0 (exactly; multiplier 1.0 from Hamerle 2018) | 0 |
| Generic music | 0 (exactly; multiplier 1.0) | 0 |
| **All triggers** | **+10.4** (paired; unpaired +10.1 from 0.714 → 0.815) | **−0.80** (paired; unpaired −0.89) |

Doubling exposure gives roughly mirror effects: missed medication −5.3 pt / +0.42; stress −1.75 / +0.22.

**Emergent: triggers are not additive.**
- Removing each trigger one at a time and summing gives +12.4 pt. Adding each alone to a trigger-free cohort and summing gives only 8.4 pt. The paired all-off contrast (10.4 pt) sits in between. (The unpaired all-off difference is 10.1 pt.)
- The cause is positive interactions: the HPA cascades (stress → sleep loss, illness/binge → missed dose) and the shared recruitment gate.
- The cost of a trigger therefore depends on what else is present.

**Emergent: self-report misattributes.** The table below compares how often people "report" each trigger under the perceived and naive rules with the trigger's causal effect.

| Trigger | Perceived rule | Naive rule | Causal effect |
|---|---|---|---|
| Generic music (exposure 60% of days) | 0% | 94% | none |
| Low pressure | 28.5% | 61% | +0.5 pt |
| Moderate alcohol | 24.7% | 48.5% | none |
| Photic (only 3% photosensitive) | 12.9% | — | — |
| Missed medication | 42% | — | the only large causal effect |

- With few seizures, chance coincidence passes even the 1.5× "excess" rule; that is why photic attribution reaches 12.9% when only 3% are photosensitive.
- So in this model, trigger-survey percentages mix real causal effects with exposure frequency.
- This matches the published spread: clinic records found triggers in 16% of patients, against 55–89% in checklists.

## 4. Music (charts/03)
- **Realistic musicogenic prevalence** (1.4e-5 of people with epilepsy, from 1 in 10 million overall): no population effect; music_OFF is bit-identical.
- **The request's "up to 1%" upper bound** (no source found): −0.3 pt seizure freedom [−0.4, −0.2], +0.08 seizures/yr.
- **K.448-type protective variant** (× 0.9 on listening days; the evidence is mixed): +1.4 pt [1.1, 1.6], −0.19 seizures/yr.
- **Mechanism test (everyone made musicogenic):**
  - With emotional content 20% of music days: seizure freedom 0.353 (−36.1 pt), +8.8 seizures/yr.
  - Emotional content 0% (neutral music only, × 2): 0.591.
  - Emotional content 100%: 0.106 (+31 seizures/yr vs 20%).
  - The emotional content of the music, not exposure to music itself, drives the effect. This is consistent with case reviews (Maguire 2012).

## 5. Drugs (charts/03, charts/06)
**SSRIs**
- **Neutral version** (epilepsy-specific evidence): identical to baseline.
- **Observational version** (OR 1.48, 2.35 in the first 30 days; general-population, likely confounded):
  - exposed depressed subgroup: −9.4 pt [−10.7, −8.2], +1.76 seizures/yr;
  - population: −2.2 pt;
  - everyone exposed: −10.0 pt.
- Adding stress relief (stress exposure halved):
  - neutral + relief: +0.6 pt in the exposed;
  - observational + relief: −8.4 pt.
- **The two literatures imply opposite conclusions. The model just shows how far apart they are.**

**Stimulants** (whole cohort)
- Observational HR 0.73: +6.8 pt [6.2, 7.4], −0.70 seizures/yr.
- Neutral: 0.
- "Threshold-lowering" × 1.3 (the request's premise, against Brikell 2019): −6.5 pt, **+1.01 seizures/yr (+57%)** from a 30% rate rise.
  - Non-linear amplification: through the recruitment gate, kindling and the sponge, a 30% rate rise gives a 57% rise in seizures.
- Adding doubled sleep loss:
  - to the HR 0.73 version: +6.4 pt;
  - to the threshold version: −7.1 pt;
  - to the neutral version: −0.4 pt.
  - Synergy of threshold × sleep loss: +0.037 seizures/yr [0.013, 0.061].

**NSAIDs** (all variants within ±0.2 pt)
- Neutral: 0.
- Susceptible 10% at × 1.3: −0.0 pt.
- Animal-antiseizure × 0.9 on illness days: +0.2 pt.
- Fever relief: +0.2 pt.
- **Practically null in every version**, because exposure is short.

**Psilocybin in people with epilepsy** (4 sessions in 2 years; every magnitude is an assumption, and no human dose-response data exist)
- Low dose: anti / neutral 0; exacerbation −0.1 pt.
- High dose: anti +0.0; neutral 0; **exacerbation −0.6 pt [−0.8, −0.5], +0.08 seizures/yr**. That is about 4 extra seizures per 100 sessions in this toy.
- High-dose exacerbation + SSRI for everyone + co-use interaction: −11.1 pt. Most of this is the SSRI observational assumption itself (SSRI alone: −10.0 pt). The psilocybin increment on top is about −1 pt (arithmetic, not a paired interaction).
- The antiseizure hypothesis (preclinical, via 5-HT1A/CB1 rather than 5-HT2A as the request said) gives no detectable benefit at 4 sessions.

**Psilocybin with no seizure history** (`code/nohist.py`; 80,000–120,000 people per arm; one latent focus, no ASM)
- Baseline tuned to the incidence of 61.44 per 100k per year (Fiest 2017). Achieved 75 per 100k [58, 97]; the target is inside the CI.
- Low or high dose, neutral or exacerbation: **excess 0 to +1.25 per 100k [−1.2, +3.7]**, not distinguishable from zero.
- High-dose exacerbation + SSRI: +38.75 per 100k [25.1, 52.4]. This arm has no SSRI-only control, so the excess cannot be attributed to psilocybin.
- This is consistent with reviews: no trial showed psychedelics inducing seizures; reported events cluster with co-medication.

**Other recreational drugs** (cocaine/amphetamine-like; × 5 on use days is an assumption)
- Monthly use: −2.9 pt, +0.36 seizures/yr.
- Weekly use: −11.3 pt [−11.9, −10.6], +1.76 seizures/yr.

## 6. Combinations and synergy (charts/09; interaction = combo − A − B + baseline, seizures/yr)
| Combination | Interaction [95% CI] |
|---|---|
| Stress + missed dose | **+0.062** [0.038, 0.086] |
| Illness + missed dose | +0.041 [0.027, 0.055] |
| Stimulant threshold + sleep loss | +0.037 [0.013, 0.061] |
| Stress + sleep, sponge ON | +0.000 [−0.011, 0.011] |
| Stress + sleep, sponge OFF | **+0.018** [0.006, 0.031] |
| Binge + sleep | +0.000 |

All five common triggers doubled: −9.9 pt with the sponge on, −12.7 pt with it off.

**Emergent: the sponge absorbs the stress × sleep synergy.**
- With the sponge on, stress and sleep loss add; with it off, they interact.
- The relapse reservoir soaks the extra reawakening attempts when two triggers coincide.

## 7. Layers: which ones change outcomes (charts/04)
"Minus" = all layers on except this one, vs MAIN. "Only" = all layers off except this one, vs the core (SF 0.531).

| Layer | Minus: Δ SF pt / Δ seizures | Only: Δ SF pt / Δ seizures | Verdict |
|---|---|---|---|
| **sponge** | **−10.2** [−10.8, −9.5] / +1.15 | **+10.5** / −1.38 | major |
| **inhibition** (surround with exhaustion) | **−9.6** [−10.2, −9.1] / +1.22 | **+10.3** / −1.55 | major |
| hpa (cortisol load + cascades) | +1.7 [1.4, 1.9] / −0.18 | −2.5 / +0.40 | moderate; removing it helps |
| kindling (Hawkes) | 0.0 / −0.16 [−0.21, −0.10] | 0.0 / +0.38 | changes frequency, not who is seizure-free |
| network coupling | 0.0 / −0.05 | 0.0 / +0.07 | small |
| materials | −0.2 [−0.4, +0.1] / +0.04 | 0 alone; +0.3 pt on top of the sponge | minor; needs the sponge |
| physics | 0.0 / +0.06 [−0.00, 0.13] | 0 alone; about 0 with the sponge | negligible |
| heat | 0 / 0 | 0 | observational (as in v4) |
| **shading** (default) | 0 / 0 | 0 | observational; changes nothing |

All layers off vs MAIN: −18.3 pt (core seizure freedom 0.531, 3.88 seizures/yr).

## 8. Cell shading (PROVISIONAL definition; CELL_SHADING.md; charts/07–08)
No definition of "cell shading" exists in Caitlyn's GitHub or past transcripts, so a provisional cel-shading definition was used:
- each focus gets a continuous shade (state tone + energy highlight), quantised into 4 flat bands: dark, quiescent, active, ictal;
- every Levy event is booked to its band;
- the whole-brain shade is the exact reconciled aggregate of the parts.

**Results**
- **Reconciliation:** whole-brain shade = aggregate of the parts on every day of every run (1.13 million person-runs, 0 mismatches). Bit-identical across 2- or 3-part partitions.
- **Band occupancy vs Levy (MAIN):**
  - brain-days by band: dark 4.9%, quiescent 73.1%, active 19.0%, ictal 3.0%;
  - Levy weight by band: dark 1.7%, quiescent 0.1%, active 17.7%, **ictal 80.5%**.
  - The ictal tone holds 3% of the time but four-fifths of all Levy weight.
  - Without the sponge: ictal 5.1% of days, 82.9% of Levy.
- **Separation:** mean shade over the last 12 months is 0.255 [seizure-free] vs 0.339 [still seizing]; cohort mean 0.279 [0.278, 0.281].
  - Sponge off brightens the cohort to 0.317.
  - With every trigger removed it is 0.264.
- **Around seizures (7,091 events):**
  - whole-brain shade drifts up slightly over the 10 days before a seizure (0.612 → 0.625), jumps to 0.742 on the seizure day, then decays below the pre-seizure level by day 6 (0.594 at day 10).
  - The post-event undershoot reflects post-ictal refractoriness plus sponge soaking.
  - The small pre-event rise is mostly selection: seizures happen in brighter brains. It should not be read as a predictor.
- **Does it change outcomes?**
  - Observational shading, on or off, and coarse bands: **no change** (bit-identical).
  - Coupled variant (a "hot" brain fills its sponge faster): dose-dependent harm. Seizure freedom changes by −0.8 pt (feedback 0.25), −1.5 pt (0.5) and **−3.0 pt [−3.4, −2.6]** (1.0), with +0.38 seizures/yr. It is exactly neutral with the sponge off, because shading acts only through the sponge.

## 9. Sponge parameters (charts/05)
| Change | Δ SF pt | Other effects |
|---|---|---|
| Relapse-reservoir gate dorm_gate 0.9 | **+12.9** | −1.01 seizures/yr |
| dorm_gate 0.1 | −8.5 | +0.97 seizures/yr |
| Network-reservoir gate circ_gate 0.03 / 0.3 | ≈ 0 | — |
| Capacity 10 / 160 | ≈ 0 | — |
| Permeability 0.01 | +2.3 | — |
| Permeability 0.2 | −0.5 | — |
| Kill 0.05 | **+7.9** | residual −21.4 pt; **eliminated +29.3 pt** |

**Emergent findings**
- The sponge's benefit comes almost entirely from soaking **reawakenings of quiescent foci**, not escaped discharges.
- Capacity never binds at these levels.
- Giving the sponge a small kill rate turns "residual risk" into "eliminated". The sponge then acts as a clearance route rather than a buffer, which mirrors the v4 metastasis result.

## 10. Comparison with known public patterns (qualitative)
- Missed medication is the strongest modifiable driver. This is consistent with the Epilepsy Foundation and with surveys from India and Saudi Arabia.
- Stress and sleep loss are frequently reported, but their causal effect per exposure is modest (Haut 2007 ORs). The model reproduces "often reported, modest effect".
- Moderate alcohol is neutral (Hamerle 2018); binges matter.
- Seizure clusters are common (28% of those still seizing, inside the 15–43% range). SeizeIT2 EMU annotations show heavy over-dispersion (interval CV 2.31; 52% of subjects with ≥ 3 seizures in 24 h), more than the outpatient model, as expected for medication-tapered EMU stays.
- Photosensitivity and musicogenic epilepsy are individually dramatic but rare, so they have no population impact.
- **Not reproduced:** the model's seizure freedom is slightly above the band, and the illness attribution is too high.

## 11. Files
See README_PLAIN.md for a plain-language version.
- Folders: `code/`, `data/` (CSV summaries and contrasts; raw per-person pickles in `data/raw/`), `charts/01–09`.
- Documentation: PREFLIGHT.md, MAPPING.md, PARAMETERS.md, PUBLIC_DATA_INPUTS.md, CELL_SHADING.md, ITERATION_LOG.md, LAYERS.md, SPONGE_MODULE.md, UPDATE_SEQUENCE.md.
