# Oroboro Epilepsy Relational Simulation — Study Summary

**Speculative architecture testbed only. No clinical claims or medical advice.**

November 2026 · Caitlyn Connor Randels

## Overview

Adaptation of the Oroboro metastasis relational simulation architecture testbed (v4 metastatic-cascade model and data-informed simulations) to epilepsy and seizure dynamics. Uses only Oroboro systems (state reduction, independent reduced states, Levy-weighted transitions, delta reconciliation, Nexus/Transcriber/Levy/Genesis, mesh and sponge analogs) as the operating system. Public data ingested as inputs.

117 scenarios covering approximately 1.13 million simulated people over two years each. All components passed preflight; every brain’s whole result matched the sum of its independent parts.

## Key Results Matching Public Patterns

- Residual risk high: ~71% seizure-free at 12 months (published range typically 60–70%); only ~3% ever fully clear.
- Missed medication produced the largest single gain (~7 additional seizure-free points).
- Triggers stack: stress + missed medication exceeded the sum of individual effects.
- Music: no population-level effect at realistic musicogenic rates; in a fully susceptible cohort emotional music drove most of the risk.
- Drug effects mixed:
  - SSRIs: neutral under epilepsy-specific evidence, harmful under general-population evidence.
  - Ibuprofen: essentially neutral.
  - Adderall/stimulants: helpful under published data, harmful only under assumed threshold-lowering premise.
  - Psilocybin: small worst-case harm at high doses in people with epilepsy history; no measurable benefit; no detectable effect without seizure history.
  - Weekly recreational drug use: most harmful.

## Notable Observations

- Self-reported triggers can mislead (music and weather frequently reported even when causal weight is low).
- Sponge compartment mattered substantially: disabling it cost ~10 seizure-free points, primarily by allowing quiet foci to reawaken.

## Cell Shading

Temporary definition used (four bands: dark, quiet, active, seizing). Shade tracks excitability, settledness, Levy weight, and local coupling; drives heat-trace and charts. Pure display changes nothing; when feeding the sponge it lowered seizure freedom by 1–3 points. Seizing band covered ~3% of brain-days but carried ~80% of event weight. Shade spikes on seizure day and falls below baseline within ~6 days.

## Psilocin / Mouse Effect as On-Off Gate

Reexamination of Balabandian et al. (2025, Pharmacol Res Perspect 13(2):e70079): modest doses of psilocin (~3 mg/kg i.p.) showed anticonvulsant effects in mouse PTZ and MES models via 5-HT1A (upregulated) and CB1 (downregulated; AM-251 blocked), plus kynurenine, nitrergic, and opioidergic pathways. 5-HT2A expression unchanged.

Mapped as candidate on-off gate in Oroboro terms:
- Sponge membrane_gate / permeability (quiet-pool absorption vs reawakening).
- Cell-shade band switch threshold (quiet vs active/seizing).
- Levy-weighted transition probability.
- Aligns with existing polarity mesh, HardCap, magnetic detach/attach, and delta reconciliation patterns from the metastasis testbed and prior Oroboro components.

Optional `psilocin_gate` parameter proposed (on/off toggle) for future runs.

## Limitations

Architecture testbed, not a calibrated clinical predictor. Some initial literature figures adjusted to match source ranges. All parameters speculative.

## Files

Full simulation outputs and code reside with the Oroboro Metastasis Sim Runner bot. This repository contains the study summary and related notes.
