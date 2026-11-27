# Oroboro Epilepsy Relational Simulation

**Speculative architecture testbed only. No clinical claims or medical advice.**

November 2026 · Caitlyn Connor Randels

Adaptation of the Oroboro metastasis relational simulation architecture testbed (v4 metastatic-cascade model and data-informed simulations) to epilepsy and seizure dynamics. Uses only Oroboro systems (state reduction, independent reduced states, Levy-weighted transitions, delta reconciliation, Nexus/Transcriber/Levy/Genesis, mesh and sponge analogs) as the operating system. Public data ingested as inputs.

117 scenarios covering approximately 1.13 million simulated people over two years each. All components passed preflight (50/50 checks); every brain’s whole result matched the sum of its independent parts.

This repository now holds the full code, results, notes, and paper (not only the study summary).

## Key results matching public patterns

- Residual risk high: ~71% seizure-free at 12 months (published range typically 60–70%); only ~3% ever fully clear.
- Missed medication produced the largest single paired gain (~7 additional seizure-free points).
- Triggers stack: stress + missed medication exceeded the sum of individual effects. Turning all triggers off raised seizure freedom by **+10.4 percentage points** paired (0.80 fewer seizures/person-year); the unpaired difference was +10.1 points / 0.89 fewer.
- Music: no population-level effect at realistic musicogenic rates; in a fully susceptible cohort emotional music drove most of the risk.
- Drug effects mixed:
  - SSRIs: neutral under epilepsy-specific evidence, harmful under general-population evidence.
  - Ibuprofen: essentially neutral.
  - Adderall/stimulants: helpful under published data, harmful only under an assumed threshold-lowering premise.
  - Psilocybin: small worst-case harm at high doses in people with epilepsy history; no measurable benefit; no detectable effect without seizure history.
  - Weekly recreational drug use: most harmful.

## Notable observations

- Self-reported triggers can mislead (music and weather frequently reported even when causal weight is low).
- Sponge compartment mattered substantially: disabling it cost ~10 seizure-free points, primarily by allowing quiet foci to reawaken.
- Bookkeeping sponge spill was zero in 113 of 117 conditions. The four exceptions are the extreme musicogenic cohorts and two SSRI-for-everyone conditions (`ssri_obsOR_all`, `psilo_high_exacerb_plus_ssri`); conservation still held in all 117.
- On core-vs-full validation, only the core model with free multipliers scored better than MAIN (0.282 vs 0.353); the core model with anchored multipliers was worse (0.385). Both core scenarios fit more public bands (7/9 vs 5/9).

## Cell shading

Temporary definition used (four bands: dark, quiet, active, seizing). Shade tracks excitability, settledness, Levy weight, and local coupling; drives heat-trace and charts. Pure display changes nothing; when feeding the sponge it lowered seizure freedom by 1–3 points. Seizing band covered ~3% of brain-days but carried ~80% of event weight. Shade spikes on seizure day and falls below baseline within ~6 days.

See [`CELL_SHADING.md`](CELL_SHADING.md).

## Psilocin / mouse effect as on-off gate

Reexamination of Balabandian et al. (2025, *Pharmacol Res Perspect* 13(2):e70079): modest doses of psilocin (~3 mg/kg i.p.) showed anticonvulsant effects in mouse PTZ and MES models via 5-HT1A (upregulated) and CB1 (downregulated; AM-251 blocked), plus kynurenine, nitrergic, and opioidergic pathways. 5-HT2A expression unchanged.

Mapped as a candidate on-off gate in Oroboro terms (sponge `membrane_gate` / permeability, cell-shade band switch, Levy-weighted transition threshold). Optional `psilocin_gate` parameter proposed (off by default) for future runs. Full note: [`GATE_NOTE.md`](GATE_NOTE.md).

## Paper and starting points

- Paper (PDF): [`paper/Epilepsy_Seizure_Dynamics_Relational_Simulation_Study.pdf`](paper/Epilepsy_Seizure_Dynamics_Relational_Simulation_Study.pdf) (Word copy and build source in `paper/`).
- Plain-language overview: [`README_PLAIN.md`](README_PLAIN.md)
- Results: [`RESULTS_SUMMARY.md`](RESULTS_SUMMARY.md)
- Mapping, parameters, public data: [`MAPPING.md`](MAPPING.md), [`PARAMETERS.md`](PARAMETERS.md), [`PUBLIC_DATA_INPUTS.md`](PUBLIC_DATA_INPUTS.md)
- Checks and history: [`PREFLIGHT.md`](PREFLIGHT.md), [`ITERATION_LOG.md`](ITERATION_LOG.md)


## What's included here

This public tree has the study paper, code, documentation, charts, calibration and summary results, and the gate/cell-shading notes.

Not uploaded (kept on the project computer; cited in [`PUBLIC_DATA_INPUTS.md`](PUBLIC_DATA_INPUTS.md)):
- Third-party OpenNeuro / SeizeIT2 per-recording event files (`sources/openneuro/`, ~12 MB, 2,800+ files).
- Raw per-condition pickle dumps (`data/raw/`).

## Reproduce (Python 3.11+, numpy, scipy, pandas, matplotlib)

```
cd code
python3 preflight.py                 # 50 checks
python3 calibrate.py <scenario>      # FULL_anchored | FULL_free | CORE_anchored | CORE_free
python3 run_all.py && python3 contrasts.py && python3 nohist.py
python3 final_observables.py && python3 charts.py
```

## Limitations

Architecture testbed, not a calibrated clinical predictor. Some initial literature figures were adjusted to match source ranges. All parameters are speculative.

## Related work

- [Oroboro](https://github.com/caitlynrandels-del/Oroboro) and [consciousness-mapping](https://github.com/caitlynrandels-del/Oroboro/tree/main/consciousness-mapping)
- [metastatic-cascade-analysis](https://github.com/caitlynrandels-del/metastatic-cascade-analysis)

---

*Independent research. Speculative modeling only. Not medical advice.*
