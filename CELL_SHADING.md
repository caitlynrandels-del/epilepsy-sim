# CELL_SHADING.md: cell shading in the epilepsy testbed (PROVISIONAL definition)

Speculative modeling / architecture testbed only. No clinical claims.

## 1. Search for an existing definition
Searched on 26 Nov 2026 (PT):
- **GitHub (`caitlynrandels-del`, all repos, code search).**
  - "shading": 0 hits.
  - "cel shading" / "cel-shading" / "toon": 0 hits.
  - "shade": 5 files. All are about graphics *shaders* (WebGL/Three.js or Metal compute shaders): the Stateful-Particle-Engine README, the Firefly README and its bundled JS, `Oroboro_Framework_Summary.md` ("Metal compute shaders"), and `Oroboro_Research_Submission.md` ("malleable elements employing Metal compute shaders").
- **This agent's past transcripts:** no record available.
- **Local workspace (`/workspace/oroboro-*`, study-writeup, oasis):** no definition.

**No existing Oroboro definition of "cell shading" was found, so the definition below is PROVISIONAL.** It is labelled that way in MAPPING.md, `layers.py` and every chart. It should be replaced by Caitlyn's own definition if she has one.

## 2. Provisional definition
"Cell shading" is read in the cel-shading (toon-rendering) sense: continuous lighting is quantised into a few flat tone bands. Each focus (an independent reduced state) carries:
- a **continuous shade** s ∈ [0, 1] = state tone + energy highlight:
  - state tone: cleared 0, held in the sponge 0.15, quiescent (dormant) 0.25, active 0.5;
  - energy highlight: 0.5 × (1 − exp(−(discharges today + 3 × seizures today + kindling charge) / 2)), zero for cleared foci;
- a **cel band** (4 flat tones), cut at s = 0.2 / 0.4 / 0.7:
  - band 0 "dark": cleared or held;
  - band 1 "quiescent";
  - band 2 "active, interictal";
  - band 3 "ictal / hot".

Where shading enters the model:
1. **Model state (reduced states).** Shade and band are per-focus state, computed inside each Part from that focus only (partition-independent).
2. **Seizure events (Levy-weighted transitions).** Every day's Levy increment of a focus is booked to the focus's band (`levy_band0..3`). The sum over bands equals the Levy total (checked every run).
3. **Heat-trace.** When shading is on, the bookkeeping sponge's heat channel takes the reconciled whole-brain shade instead of the raw seizure count. In the coupled variant, the shade also darkens the biological sponge's fill gradient.
4. **Final observables after delta reconciliation.**
   - Whole-brain shade = (sum of the parts' shade sums) / number of foci, computed by the Nexus.
   - It is checked every day against a direct whole-brain recomputation (`shade_recon_bad` = 0 in all 1.13 million person-runs).
   - The shade raster, band raster and Levy-by-band are bit-identical between whole and 2- or 3-part runs.
   - Whole-brain band = the brightest band among its foci.

## 3. Switch and variants
- `layers={"shading": True}` gives the **observational** default (feedback 0). Shading is ON in the main configuration.
- `{"shading": {"feedback": f}}` gives the **coupled** variant. Yesterday's reconciled whole-brain shade lowers sponge availability (× (1 − f·shade)): a "hot" brain has a fuller sponge. It acts only through the sponge.
- `{"shading": {"bands": [...]}}` changes the cel cut points.

## 4. What it changed (results; details in RESULTS_SUMMARY.md §8 and charts 07–08)
- **Observational shading changes no outcome.** Outcomes are bit-identical with it on, off or absent (preflight; `layer_minus_shading` and `layer_only_shading` both give Δ = 0). Coarser bands also gave Δ = 0.
- **Coupled shading is harmful in a dose-dependent way.** P(seizure-free 12 m) vs the main configuration:
  - feedback 0.25: −0.8 points [−1.0, −0.6];
  - feedback 0.5: −1.5 [−1.7, −1.2];
  - feedback 1.0: −3.0 [−3.4, −2.6]; seizures +0.38 per person-year [+0.30, +0.46].
  - With the sponge OFF, the coupled variant is exactly neutral (as designed).
- **Descriptive patterns (main configuration, 10,000 brains).**
  - Brain-days by band: 4.9% dark, 73.1% quiescent, 19.0% active, 3.0% ictal.
  - The ictal band holds only 3.0% of brain-days but **80.5% of all Levy weight**; the active band holds 17.7%.
  - Mean shade over the last 12 months is 0.255 for seizure-free brains and 0.339 for still-seizing brains.
  - Without the sponge the cohort is brighter (mean 0.317, ictal-band days 5.1%).
  - The event-triggered average shade rises sharply on seizure days and decays over a few days (chart 08).

## 5. Cross-reference: the psilocin receptor gate (see GATE_NOTE.md)
The proposed receptor/pathway "on-off gate" (Balabandian et al. 2025) does not feed shading as an input, but
its effect is **readable in the shade bands**: when the gate is engaged (`rec_mult` < 1, `dorm_mult` > 1), fewer
foci cross into the **active** and **ictal/hot** bands, so the whole-brain shade stays lower. This is an
*emergent, observational* consequence (shading remains a display/measure, not a driver), and it is the band-level
signature to watch when testing the gate. Full definition, parameters and test plan: `GATE_NOTE.md`.
