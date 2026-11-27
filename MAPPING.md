# MAPPING.md: how the Oroboro architecture is mapped onto epilepsy / seizure dynamics

Speculative modeling / architecture testbed only. No clinical claims, not medical advice. Epilepsy is the *subject* used to exercise the architecture, exactly as metastasis was in the v4 testbed (`Oroboro/consciousness-mapping/Oroboro_Metastasis_Architecture_Testbed.md`).

## Sources of the architecture (the user's own systems only)
- GitHub `caitlynrandels-del/Oroboro/consciousness-mapping/` (read-only through the GitHub connector, 26 Nov 2026), specifically:
  - `Oroboro_Framework_Summary.md` (Nexus, Transcriber, Dictator, Levy, Genesis, HardCapIntegration, "independent parts recombined to match the whole-system observable");
  - `Sponge_Absorption_Mechanic.md`;
  - `Operational_Update_Sequence.md`;
  - `Oroboro_Metastasis_Architecture_Testbed.md`;
  - `NaCl_Polarity_Mesh_Research_Note.md` (mesh locking, consensus, delta reconciliation).
- `caitlynrandels-del/metastatic-cascade-analysis` (`Operational_Update_Sequence.md`, model and v4 summary).
- The v4 code on this computer (`/workspace/oroboro-multidb-sim-v4/code`, read only). From it the following were copied and adapted:
  - counter-based RNG;
  - Genesis/Nexus/Levy classes;
  - the sponge (both layers);
  - the layer switch interface;
  - background processors;
  - the update sequence and the adaptive stop rule.
- **No external operating-system or framework assumptions.** The code uses only numpy/scipy/pandas/matplotlib for arithmetic and plotting.

## Component mapping
| Oroboro component | Metastasis testbed (v4) | Epilepsy testbed (this run) | Where |
|---|---|---|---|
| Genesis (origin identity, infinite weight) | primary tumour shedding stream | each virtual brain's epileptogenic network (root tag "I am the OG avatar"); every focus mirrors back to it | `epi_core.Genesis` |
| Independent reduced states (Parts) | groups of disseminated cells | **groups of neural circuits / foci** (1–4 foci per brain, split into K parts by id). A Part sees only its own foci plus *yesterday's* Nexus summary of its brain | `epi_core.run` parts loop |
| Nexus (register / archive / telemeter) | monthly recombination | daily recombination of the parts into whole-brain observables (seizures, discharges, sponge fill, shade) | `epi_core.Nexus` |
| Levy-weighted transitions | clear +1, detach +7, fail +2, colonize +14, exit +4 | clear +1 = discharge suppressed locally (or focus remits); detach +7 = discharge escapes its focus; fail +2 = escaped discharge fails to recruit the network (aborted/subclinical); **colonize +14 = clinical seizure**; exit +4 = quiescent focus reawakens | `epi_core.Levy` |
| Salience gate + homeostasis | establishment checkpoint, load-raised threshold | whole-brain recruitment gate (rec_p), raised for a few days after a seizure (post-ictal refractoriness, lagged) | `rec_eff` |
| Clearance / dormancy | cleared cells / dormant cells | **eliminated** = every focus cleared and nothing held, no seizure in the last 12 months (remission analogue); **dormancy** = quiescent focus suppressed by medication that can reawaken; **residual risk** = seizure-free for 12 months but at least one non-cleared focus or held content remains | outcomes in `epi_core.run` |
| Overt lesion | colonisation | seizure in the last 12 months (the "drug-resistant / still seizing" analogue) | `sf12` |
| Mesh consensus | ledger vs heat-trace per organ | Levy ledger vs heat-trace intensity field vs daily seizure matrix must agree for every focus | `consensus_ok` |
| Delta reconciliation | whole vs 4 parts | whole-brain run vs K = 2 or 3 independent parts, **bit-identical** per focus and per day; census and Levy checks | `epi_core.reconcile`, preflight, each condition |
| Transcriber / Dictator | chronicle | chronicle of seizures, reawakening attempts and sponge soaks (`record=True`) | `epi_core.Transcriber` |
| Sponge (porous intermediary; capacity = HardCapIntegration; permeability; membrane skin; Levy = absorbed content; heat-trace = fill gradient; deformable) | circulating cells / dormant-exit attempts soaked | escaped discharges (+7 each) soaked before the recruitment gate, and reawakening attempts (+4) of quiescent foci soaked; release at permeability; availability from yesterday's reconciled whole-brain fill | `sponge.py`, `SPONGE_MODULE.md` |
| Background processors | PrincipleAuditor, MemoryBlender, MeshRerouteMonitor, CorrelationPipeline | same four, re-mapped (seizures outside the dominant focus = "reroutes") | `background.py` |
| Update sequence ("redstone torch") | parameter files and calibration iterates | same six steps on every proposal (torch) and every accepted calibration iterate; final parameter files committed by it | `update_sequence.py`, `UPDATE_SEQUENCE.md` |
| **Cell shading (PROVISIONAL)** | — | per-focus shade and cel band; shades every Levy event; whole-brain shade = reconciled aggregate; feeds the heat-trace; optional coupled variant through the sponge | `CELL_SHADING.md` |
| **Receptor/pathway gate (PROPOSED; off by default)** | — | psilocin on-off gate (Balabandian et al. 2025): engages in a dose window with pathways intact; acts on the recruitment threshold (`rec_mult`), the relapse gate (`dorm_mult`) and permeability/latch (`perm_mult`); pathway booleans = antagonist knockouts; 5-HT2A = negative control | `GATE_NOTE.md`, `code/layers.py` (proposed) |

## Observables after delta reconciliation (what is compared with public data)
- P(seizure-free in the last 12 of 24 months) → Chen 2018 / Kwan & Brodie 2000 / WHO.
- P(≥1 cluster day with ≥3 seizures | still seizing) → cluster reviews.
- Self-reported triggers among people with seizures, using two attribution rules (below) → the trigger surveys.
- Residual risk, eliminated, seizures per person-year, Levy totals and shade are reported, but there is no public target for them.

## Key assumptions (all explicit)
1. **Time step** = 1 day, horizon 730 days, outcome window = last 365 days. Everyone starts antiseizure medication (ASM) on day 0.
2. **Foci:** number per brain 1/2/3/4 with probabilities 0.50/0.25/0.15/0.10. Secondary foci have half the base rate. Discharge rates are log-normal across foci (σ = 1.2). All of these are assumptions.
3. **ASM response** is two-class: responders (fraction calibrated, ≈ 0.50) get 90–100% suppression, non-responders 20–70%. This is an assumption; only the resulting seizure-freedom proportion is calibrated.
4. **Triggers** multiply the day's discharge rate. Exposures are person-level daily events, shared by all foci of a brain (so independent of the partition).
5. **Self-report.** Surveys ask people what triggers their seizures, and the model has no perception data. Two rules are reported:
   - **naive:** ≥1 seizure fell on the exposure day or the day after;
   - **perceived** (used for calibration): naive, AND the share of seizure-days in the exposure window is ≥ 1.5 × the share of all days in the window. The 1.5 ratio is an assumption.
6. **Not modelled:** ASM switching, age, epilepsy syndrome, mortality/SUDEP, treatment gaps in low-income countries.
7. **Non-identifiability.** Several parameters cannot be identified from the targets:
   - resp_frac and cluster_b stayed at their start values;
   - the free stress and sleep multipliers stayed close to the diary anchors.
   See ITERATION_LOG.md.
