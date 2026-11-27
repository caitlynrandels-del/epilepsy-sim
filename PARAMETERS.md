# PARAMETERS.md: every parameter, its value, and where it comes from

Speculative modeling / architecture testbed only. No clinical claims.
Labels:
- **[SRC]** taken from a public source (see PUBLIC_DATA_INPUTS.md);
- **[ANCH]** an assumed value anchored on a public source;
- **[CAL]** calibrated (Nelder–Mead) to public targets;
- **[ASSUME]** a pure modelling assumption;
- **[ARCH]** carried over from Caitlyn's Oroboro v4 architecture.

Files:
- `code/params_base.json`: starting values.
- `data/calibration/params_{FULL_anchored,FULL_free,CORE_anchored,CORE_free}.json`: written through the update sequence.
- MAIN = `params_FULL_anchored.json` with the shading layer added (observational, so the outcomes are unchanged).

## Time and Levy weights
| Key | Value | Label |
|---|---|---|
| days / obs_days | 730 / 365 (day step; outcomes over the last 12 months) | ASSUME |
| Levy clear / detach / fail / colonize / exit | 1 / 7 / 2 / 14 / 4 | ARCH (v4 weights; epilepsy meanings in MAPPING.md) |

## Cohort (people with epilepsy, all starting an ASM on day 0)
| Key | Value | Label / source |
|---|---|---|
| n_circ_probs (1/2/3/4 foci) | 0.50/0.25/0.15/0.10 | ASSUME |
| female_frac | 0.5 | ASSUME |
| catamenial_frac (of women) | 0.423 | SRC Herzog 1997 / NIH progesterone trial (≥2-fold phase rise) |
| photosensitive_frac | 0.03 | SRC Epilepsy Foundation "about 3%" |
| musicogenic_frac | 1.4e-5 | ANCH Critchley 1977 1/10,000,000 ÷ prevalence 0.007 |
| depression_frac | 0.231 | SRC Fiest 2013 pooled |
| base_rate (discharges/focus/day before ASM) | **0.6177** | CAL (start 0.35) |
| lam_sigma | 1.2 (log-normal across foci) | ASSUME |
| secondary_scale | 0.5 | ASSUME |
| resp_frac (ASM responders) | **0.5004** | CAL (barely moved from 0.5: weakly identified) |
| eff_resp / eff_non | 0.90–1.0 / U(0.2, 0.7) | ASSUME |

## Dynamics
| Key | Value | Label |
|---|---|---|
| clear_p (local suppression of a discharge) | 0.9 | ASSUME |
| rec_p (escaped discharge recruits the network → seizure) | 0.35 | ASSUME |
| refractory / refr_tau (post-ictal raise of the gate, lagged) | 0.5 / 1 day | ASSUME (homeostasis analogue) |
| quiesce_p, wake_p, remit_p, q_rate | 0.02, 0.002, 1e-4, 0.03 | ASSUME |
| miss_drop / miss_wake_mult | 0.5 / ×4 | ASSUME (Epilepsy Foundation: missed doses are a leading cause of breakthrough seizures; magnitude assumed) |
| cluster_b (same-day branching, ≤ 6 generations) | **1.0004** | CAL (weakly identified); structure motivated by Osorio 2010 self-triggering and SeizeIT2 over-dispersion |

## Exposures (daily probabilities) and multipliers (on the day's discharge rate)
| Trigger | p (per day) | Multiplier | Labels |
|---|---|---|---|
| Stress | **0.0886** (×1.5 if depressed) | 1.26 | p CAL; m ANCH Haut 2007 OR 1.06/point × 4 points; dep ×1.5 ASSUME |
| Sleep loss | **0.0548** | 1.33 | p CAL; m ANCH Haut 2007 0.91/h × 3 h |
| Missed dose | **0.1029** | efficacy × 0.5 that day, wake × 4 | p CAL |
| Alcohol, moderate | 0.10 | 1.0 | SRC Hamerle 2018 (no association) |
| Binge (acts the next day) | 0.01 | 3 | timing SRC Hamerle 2018; values ASSUME |
| Illness/fever (4-day episodes) | onset 0.0082 | **1.416** | p ASSUME; m CAL |
| Low pressure (weather) | 0.16 | 1.14 | m SRC doi:10.1111/epi.13776 (direction contested) |
| Sensory overload | 0.05 | 1.1 | ASSUME |
| Photic (photosensitive only) | 0.02 | 5 | ASSUME |
| Catamenial phase (7 days per 28) | — | 2 | SRC Herzog (≥2-fold definition) |
| Music, generic | 0.6 | 1.0 | ANCH: K.448 evidence mixed (alternative 0.9) |
| Music, musicogenic, emotional / neutral | emotional share 0.2 | 20 / 2 | ASSUME |
| HPA layer cascades | stress → sleep loss × 2; illness or binge → missed dose × 2 | — | ANCH Nanjing 2017 (stress–sleep correlated); magnitude ASSUME |

The FULL_free scenario also calibrated m_stress → 1.237 and m_sleep → 1.256. Both are close to the Haut anchors.

## Attribution (self-report analogue)
- **perceive_ratio = 1.5** (ASSUME). A trigger is "reported" if the share of seizure-days falling in the person's exposure window (the exposure day or the day after) is ≥ 1.5 × the share of days in the window.
- The naive rule (any coincidence) is reported as attrN_*.

## Calibration targets (code/targets.py)
| Observable | Point | Band | Source |
|---|---|---|---|
| sf12 | 0.637 | 0.60–0.70 | Chen 2018; Kwan & Brodie 2000; WHO "up to 70%" |
| cluster (≥3 in 24 h, given still seizing) | — | 0.149–0.43 | cluster reviews |
| stress / sleep / miss / ill (reported) | — | 0.30–0.56 / 0.18–0.52 / 0.07–0.41 / 0.06–0.14 | trigger surveys §3 |
| catamenial (women) | — | 0.12–0.28 | Frucht, EpiWatch |
| any / two+ triggers | — | 0.55–0.89 / 0.28–0.61 | Nakken, Sperling, Nanjing, AIIMS |

Score = Σ (distance outside the band / band width)² + 0.05 × (pull toward the point).

## Layers (code/layers.py; values ARCH/ASSUME)
- **sponge:** circ_gate 0.10, dorm_gate 0.50, capacity 40, hard cap 3×, deform 0.5, permeability 0.05/day, kill 0.
- **materials:** porosity 0.7 (ref 0.5), saturation exponent 2, hysteresis 0.5, elasticity 0.5.
- **physics:** pressure_k 1, diffusion_D 1, compression_k 2.
- **heat:** diffusion 0.2, dissipation 0.1 (observational).
- **inhibition:** boost 1.0, exhaustion_K 5.
- **hpa:** decay 0.8, k 0.10, sleep_given_stress ×2, miss_given_ill_or_binge ×2.
- **kindling:** Hawkes k 0.5, tau 2 days.
- **network:** k 0.3 (lagged whole-brain coupling).
- **shading (PROVISIONAL):** energy_scale 2, bands [0.2, 0.4, 0.7], feedback 0 (variants 0.25 / 0.5 / 1.0).

## Instances (code/experiments.py)
**Natural triggers**
- *_OFF: exposure probability set to 0.
- *_AMPx2: exposure probability × 2.
- *_ONLY: all other triggers off.

**Music**
- K448: m_music_generic 0.9.
- User upper bound: musicogenic_frac 0.01. This is the request's figure; no source was found.
- Musicogenic cohort: frac 1.0, with emotional share 0 / 0.2 / 1.0.

**SSRI**
- Observational: × 1.48, × 2.35 in the first 30 days [ANCH 2023 meta-analysis].
- Neutral: × 1.0 [ANCH epilepsy-specific reviews].
- Optional stress relief (stress exposure × 0.5 [ASSUME]).
- Target: the depressed subgroup, or everyone.

**Stimulants (whole cohort exposed)**
- × 0.73 [ANCH Brikell 2019 HR].
- × 1.0 neutral.
- × 1.3 "threshold" [ASSUME; request's premise, contradicted by the evidence].
- "+ sleep loss" variants double sleep-loss exposure.

**NSAIDs**
- On illness days, or regularly at 5% of days.
- Neutral 1.0.
- Susceptible 10% at × 1.3 [ASSUME].
- Animal antiseizure × 0.9 [ANCH 2024 review].
- Fever relief: illness multiplier excess × 0.5 [ASSUME].

**Psilocybin** (4 sessions on days 120 / 300 / 480 / 660 [ASSUME])
- Low dose: anti × 0.8; neutral × 1.0; exacerbation × 1.5 on the day, × 1.2 the next day.
- High dose: anti × 0.7; neutral; exacerbation × 3 / × 1.5, with a susceptible 30% at × 10 / × 3.
- "+ SSRI": high-dose exacerbation, SSRI observational for everyone, and a co-use interaction × 1.5 [ANCH Simonsson, co-use common in reported events; magnitude ASSUME].
- All magnitudes are assumptions; no human dose-response data exist.

**Psilocybin, no seizure history** (code/nohist.py)
- One focus per person, no ASM.
- base_rate tuned so first-seizure incidence = 61.44 / 100k person-years [SRC Fiest 2017].
- Then the same psilocybin hypotheses are applied.

**Other recreational drugs**
- Use days with p 1/30 or 1/7, × 5 [ASSUME].

**Combos**
- Exposure × 2 on several triggers at once; synergy is measured as an interaction on paired common random numbers.
