# PUBLIC_DATA_INPUTS.md: every public input, its source, licence/terms, and how it was used

Speculative modeling / architecture testbed only. No clinical claims, not medical advice.
Retrieved 26 Nov 2026 (PT). Only openly accessible pages, abstracts and CC0 metadata were used. Nothing behind a login or paywall was accessed, and no large signal datasets were downloaded.
"Use" column: **T** = calibration target, **P** = parameter value taken directly, **A** = anchor for an assumed parameter, **C** = comparison/qualitative check only, **S** = scaling/reporting.

## 1. Burden and prevalence
| Input | Value (as published) | Source (URL) | Licence / terms | Use |
|---|---|---|---|---|
| People with active epilepsy, 2021 | 51.7 million (95% UI 44.9–58.9); 0.7% of population (0.3% idiopathic, 0.4% secondary); age-standardised 658/100k | GBD 2021 Epilepsy Collaborators, *Lancet Public Health* 2025;10(3):e203–e227, doi:10.1016/S2468-2667(24)00302-5. IHME summary: https://www.healthdata.org/research-analysis/library/global-regional-and-national-burden-epilepsy-1990-2021 | Abstract/summary page, publicly readable | S (scale model fractions to global counts) |
| WHO fact sheet (7 Feb 2024) | ~50 million; active epilepsy 4–10 per 1000; ~5 million diagnosed each year; "up to 70%" could be seizure-free if properly diagnosed and treated; ~80% in LMICs | https://www.who.int/news-room/fact-sheets/detail/epilepsy (copy in `sources/who_epilepsy_factsheet.html`) | WHO website, public | T (upper end of the seizure-freedom band), C |
| Active prevalence / incidence meta-analysis | Active 6.38/1000 (95% CI 5.57–7.30); incidence 61.44/100,000 person-years (50.75–74.38) | Fiest et al., *Neurology* 2017, https://pmc.ncbi.nlm.nih.gov/articles/PMC5272794/ | Open access (PMC) | P (base rate of the no-seizure-history cohort), C |
| CDC (US) | ~2.9 million US adults with active epilepsy in 2021–2022, about 1%; MMWR 2015: 2.6 million (1.2%) | https://www.cdc.gov/epilepsy/data-research/facts-stats/ ; https://www.cdc.gov/mmwr/volumes/67/wr/mm6715a1.htm | US government, public domain | C |

## 2. Treatment response, drug resistance and residual risk
| Input | Value | Source | Licence | Use |
|---|---|---|---|---|
| Seizure-free ≥1 year at last follow-up | 63.7% (1144/1795); 50.5% with the first ASM; +11.6% second, +4.4% third | Chen et al., *JAMA Neurology* 2018;75:279, https://pmc.ncbi.nlm.nih.gov/articles/PMC5885858/ | Open access (PMC) | **T** (sf12 point 0.637) |
| Seizure-free during treatment | 64% of 470 previously untreated; 47% on first drug | Kwan & Brodie, *NEJM* 2000;342:314, https://www.nejm.org/doi/full/10.1056/NEJM200002033420503 | Abstract public | T (band) |
| Definition of drug-resistant epilepsy | Failure of two tolerated, appropriately chosen and used ASM schedules | ILAE task force, Kwan et al., *Epilepsia* 2010, https://www.ilae.org/files/ilaeGuideline/Definition-of-Drug-Resistant-Epilepsy-2009-1528-1167.2009.02397.pdf | ILAE public guideline PDF | Definition only (model uses "still seizing in the last 12 months" as the drug-resistance analogue) |

## 3. Trigger (precipitant) self-report surveys
| Survey | n | Values | Source | Use |
|---|---|---|---|---|
| Frucht et al. 2000 (US tertiary) | 400 | ≥1 precipitant 62%; stress 30%; sleep deprivation 18%; sleep 14%; fever/illness 14%; fatigue 13%; menstrual 28% of women with TLE | *Epilepsia* doi:10.1111/j.1499-1654.2000.001534.x (abstract) | T |
| Sperling et al. 2008 (Thomas Jefferson) | 200 | ≥1: 65%; stress 49.5%; lack of sleep 35.5%; fatigue 32.5% | https://pubmed.ncbi.nlm.nih.gov/17977026/ | T |
| Nakken et al. 2005 (Norway) | 794 | ≥1: 55%; ≥2: 28% | https://pubmed.ncbi.nlm.nih.gov/16138128 | T |
| Nanjing 2017 | 154 | ≥1: 81.2%; stress 56.0%; sleep disorder 38.4%; fatigue 27.2%; missed medication 20.0%; ≥2: 60.8%; stress–sleep correlated | doi:10.3760/cma.j.issn.1006-7876.2017.04.005 (abstract) | T; A (stress→sleep cascade in the HPA layer) |
| AIIMS (India) 2013 | 405 | missed medication 40.9%; stress 31.3%; sleep deprivation 19.7%; fever 6.4%; 89% reported ≥1 | *Seizure* https://www.seizure-journal.com/article/S1059-1311(13)00177-5/fulltext | T |
| Saudi Arabia 2020 | 546 | sleep deprivation 52%; stress 41%; missed medication 38.5% | https://smj.org.sa/content/41/8/828 | T |
| EpiWatch app (US) 2017 | 177 reporting | stress 37%; missing sleep 18%; menses 12%; missed meds 7%; fever/infection 6% | *Neurology* 88(16 Suppl) S37.002 | T |
| Tertiary cohort 2023 | 1975 | only 16.3% had a trigger documented in clinic records (missed meds 4.5%, stress 3.9%, sleep 1.9%) | *Neurology* doi:10.1212/WNL.0000000000203555 | C (shows how strongly results depend on how triggers are asked) |
| Epilepsy Foundation trigger pages | qualitative list: stress, lack of/disrupted sleep, missed medicine (a most common cause of breakthrough seizures), alcohol, hormonal changes, drug use | https://www.epilepsy.com/what-is-epilepsy/seizure-triggers ; .../missed-medicines ; .../drug-abuse | Public pages | Model structure (which triggers exist) |
| Haut et al. 2007 prospective diary | 71 adults, 15,179 diary days | each extra hour of sleep: next-day seizure OR 0.91 (0.82–0.99); stress OR 1.06 per point (10-point scale); anxiety 1.07 | https://pubmed.ncbi.nlm.nih.gov/17998482/ | **A**: stress multiplier 1.06^4 = 1.26 (a 4-point stress day is an assumption); sleep-loss multiplier 0.91^-3 = 1.33 (a 3-hour loss is an assumption) |
| Stress narrative review; cortisol review; SMILE RCT | stress commonly reported but causal effect uncertain and may be subgroup-specific; HPA hyperactivity; relaxation reduced seizures 29% vs focused attention 25% (no difference between arms) | doi:10.1111/epi.12377; PubMed 31129236; *Neurology* doi:10.1212/wnl.0000000000005109 | Abstracts | Structure of the HPA layer (C) |

**Discrepancies with the figures in the request:** stress "~50–65%": published single-trigger values range 30–56%. The 65% figure in the Thomas Jefferson study is "≥1 precipitant of any kind", not stress. Sleep deprivation "~30–56%": published 18–52%. The targets use the published ranges.

## 4. Specific triggers
| Input | Value | Source | Use |
|---|---|---|---|
| Photosensitivity | "about 3%" of people with epilepsy (Epilepsy Foundation); 3–5% (Epilepsy Action); 2% (FAQ paper); about 1 in 4000 people overall | https://www.epilepsy.com/what-is-epilepsy/seizure-triggers/photosensitivity ; https://www.epilepsy.org.uk/info/seizure-triggers/photosensitive-epilepsy ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11995705/ | **P** photosensitive_frac 0.03 |
| Catamenial epilepsy | 42.3% of 184 women met ≥1 catamenial pattern, defined as a **≥2-fold** rise in daily seizure frequency in a cycle phase | Herzog et al. 1997 / NIH Progesterone Trial, *Seizure* 2015 https://www.seizure-journal.com/article/S1059-1311(15)00052-7/fulltext | **P** catamenial_frac 0.423, m_cat 2.0 |
| Weather | 14% higher seizure risk per 10.7 hPa fall in pressure; high humidity raised risk (case-crossover); a 2024 admissions study found the opposite direction for pressure | doi:10.1111/epi.13776 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11204309/ | **P** m_weather 1.14 (mixed evidence noted) |
| Alcohol | moderate regular drinking not associated with more seizures (OR 0.82, 0.31–2.19); seizures after heavy intake (≥7 drinks, mean 13.3), usually within 12 h after stopping | Hamerle et al. 2018, https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2018.00401/full ; PubMed 29705654 | **P** m_alc_mod 1.0; structure: binge effect acts the next day |
| Seizure clusters | 13–76% depending on definition; ≥3/24 h: 14.9% outpatient adults, 29% mixed, 43% diary study; 23.6% (temporal) / 16.9% (extratemporal) in drug-resistant focal epilepsy | Haut et al. 2022 Epilepsia (LGS Foundation PDF) ; *Seizure* 2018 review https://www.seizure-journal.com/article/S1059-1311(18)30112-2/fulltext ; doi:10.1111/epi.13465 | **T** cluster band 0.149–0.43 |
| Heavy-tailed inter-seizure intervals | power law with exponent ~0.5; seizure self-triggering ±30 min | Osorio et al. 2010, *Phys Rev E* 82:021919, https://arxiv.org/abs/0712.3929 | C (motivates the Levy-weighted clustering mechanics) |

## 5. Music
| Input | Value | Source | Use |
|---|---|---|---|
| Musicogenic epilepsy | ~1 in 10,000,000 people (Critchley 1977), exact prevalence unknown; emotional content of the music matters in many reports | Maguire 2012 *Epilepsia* critical review https://onlinelibrary.wiley.com/doi/10.1111/j.1528-1167.2012.03523.x ; Handbook chapter https://www.sciencedirect.com/science/article/abs/pii/B9780444626301000263 | **P** musicogenic_frac = 1e-7 / 0.007 ≈ 1.4e-5 of people with epilepsy |
| Request's figure "<0.003–1%" | not found in any source; 1 in 10 million of the general population is ≈0.0014% of people with epilepsy | — | run as a sensitivity upper bound (1%) and clearly labelled |
| Generic music (Mozart K.448) | meta-analyses: epileptiform discharges −28–31% during listening, seizure frequency −32% in small low-quality studies; a multiverse meta-analysis found no significant effect; a 2024 crossover RCT found an acute IED reduction | PubMed 32449680 ; *Sci Rep* 2023 https://www.nature.com/articles/s41598-023-30206-w ; *Seizure* 2024 | A: alternative parameterisation m_music_generic 0.9; baseline 1.0 (neutral) |

## 6. Drugs
| Input | Value | Source | Use |
|---|---|---|---|
| Depression in epilepsy | 23.1% (95% CI 20.6–28.3), 29,891 people, 9 studies | Fiest et al. 2013 *Neurology* https://pmc.ncbi.nlm.nih.gov/articles/PMC3589287/ | **P** depression_frac 0.231 (the request's 20–55% is wider; 23.1% is the pooled estimate) |
| SSRIs (observational, general population) | seizure OR 1.48 (1.32–1.66), 8 studies, 1.7 million people; <30 days of use OR 2.35; SNRI 1.65; TCA 1.27 (ns). Confounding by indication likely | Eur J Clin Pharmacol 2023, PubMed 37996536 | **A** "observational" parameterisation |
| SSRIs in people with epilepsy | clinical studies: no meaningful rise in seizures at therapeutic doses; SSRIs preferred | https://pmc.ncbi.nlm.nih.gov/articles/PMC10514547/ ; *Epilepsy Behav* 2016 review | **A** "neutral" parameterisation |
| ADHD stimulants | in 21,557 people with seizure history, medication periods had FEWER acute seizures (HR 0.73, 0.57–0.94) | Brikell et al. 2019 *Epilepsia* https://pmc.ncbi.nlm.nih.gov/articles/PMC6365170/ ; ILAE Epigraph summary | **A** "observational" (0.73). The request's "can lower threshold" is kept as an assumed alternative (×1.3). The evidence points the other way, so this is flagged as a **discrepancy** |
| NSAIDs / ibuprofen | not shown to lower the threshold in humans; animal PTZ data conflicting (older: lowered; 2024 review: reduced severity in 3 rat studies) | Hitchings, SGUL open access PDF ; PubMed 7202518 ; doi:10.2478/joepi-2024-0001 ; doi:10.1016/j.eplepsyres.2017.02.003 | A: neutral / susceptible-subgroup ×1.3 / animal antiseizure ×0.9 / fever relief |
| Psilocybin & classic psychedelics | no clinical trial or preclinical model showed psychedelics induce seizures. All trials excluded people with seizure history. Case reports both ways | Freidel et al. 2024 *Front Pharmacol* https://pmc.ncbi.nlm.nih.gov/articles/PMC10811552/ | A |
| | scoping review: no clear increase without other drugs; risk with co-use (lithium, kambo) | Soto-Angona et al. 2024, PubMed 38917636 | A |
| | 1.5% of 613 lifetime users reported a psychedelic-related seizure; almost half co-used antidepressants, mood stabilisers or opioid-replacement; more common with personal or family epilepsy history | Simonsson et al., https://pmc.ncbi.nlm.nih.gov/articles/PMC9627432/ | A (SSRI co-use interaction) |
| | case: 32 intracranially recorded seizures after a large recreational mushroom dose; smaller doses did not change baseline | ResearchGate case report 2023 (abstract) | A (high-dose exacerbation hypothesis) |
| | psilocin anticonvulsant in mice: PTZ clonic-threshold (CST) + MES tonic-clonic. **Dose window 3–5 mg/kg i.p.** (3 most effective; 10–20 ineffective). Effect peaks ~30 min, persists to 24 h and 9 days from one dose. Mechanism: **5-HT1A upregulated, 5-HT2A unchanged, IDO & CB1 downregulated**; blocked by AM-251 (CB1), 1-MT (kynurenine), L-NAME (NO), sildenafil (cGMP), naltrexone (opioid). Verified against Europe PMC full text PMC11851161; full analysis in `GATE_NOTE.md` | Balabandian et al. 2025 *Pharmacol Res Perspect* 13(2):e70079, doi:10.1002/prp2.70079, PMID 39996441, CC BY-NC-ND | A (antiseizure gate hypothesis); **discrepancy vs the original request wording "via 5-HT2A": the paper shows 5-HT1A/CB1, NOT 5-HT2A — confirmed** |
| Cocaine / other recreational drugs | systematic review: studies weak, no rigorous causal evidence; seizures in 0.6–8.4% of cocaine-related ED presentations; Epilepsy Foundation advises avoidance | doi:10.1016/j.drugalcdep.2013.08.019 ; Epilepsy Foundation drug-abuse page | A (×5 on use days is an assumption) |

## 7. EEG / iEEG hubs (NEMAR / OpenNeuro): metadata only
Queried through the public OpenNeuro GraphQL API and the public S3 bucket (`sources/openneuro_metadata_20261126.json`, `sources/openneuro/*_participants.tsv`). All CC0.
| Dataset | Subjects / modality / size | Used |
|---|---|---|
| ds003029 Epilepsy-iEEG-Multicenter (also NEMAR on003029) | 35, iEEG, 11.1 GB | participants.tsv (surgical outcome S/F, Engel) – C |
| ds004100 HUP iEEG | 57, iEEG, 14.2 GB | participants.tsv – C |
| ds003876 iEEG Interictal Multicenter | 39, iEEG, 5.4 GB | participants.tsv – C |
| ds005398 Open iEEG (pediatric) | 185, iEEG, 109.7 GB | participants.tsv – C |
| **ds005873 SeizeIT2** (wearable EEG, EMU, refractory epilepsy) | 125, EEG, 47.6 GB | **only the 2,850 `*_events.tsv` annotation files (0.6 MB)**. 883 annotated seizures, 11,626 recording hours. Over-dispersion check (`data/public/seizeit2_summary.json`): pooled inter-seizure-interval CV 2.31; 72.6% of intervals <4 h; 52% of subjects had ≥3 seizures within 24 h (EMU, medication often tapered, so not an outpatient rate) – C |
| ds004752, ds003844, ds003555, ds004469, ds003498 | metadata only | listed, not used further |

## 8. Skipped sources and why
- **GBD Results Tool raw downloads.** These need an IHME account and terms acceptance; the published abstract numbers were used instead.
- **Full-text PDFs of paywalled papers** (e.g. Frucht 2000, Kwan & Brodie 2000, Herzog 1997, Hamerle 2018 full data). Abstracts and open summaries only.
- **EEG/iEEG signal files** (tens to hundreds of GB). Unnecessary for a day-step model; only annotations and participants tables were used.
- **Epilepsy Foundation / ILAE community-forum content.** Personal accounts, not data.
- **The request's figures "musicogenic <0.003–1%", "psilocybin antiseizure via 5-HT2A", "stimulants lower the threshold".** No supporting source was found. Each is run only as a clearly labelled alternative and listed as a discrepancy.
- **WHO page via the fetch tool.** It timed out; it was retrieved with curl instead (same public page).
