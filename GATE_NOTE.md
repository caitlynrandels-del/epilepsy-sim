# GATE_NOTE.md — The psilocin receptor/pathway "on-off gate": Balabandian et al. 2025 reexamined and mapped onto Oroboro

Speculative modeling / architecture testbed only. **No clinical claims, no medical advice.** Nothing here says
anyone should take, avoid, or dose any substance. It maps one published mouse pharmacology result onto the
Oroboro architecture as a candidate *gate construct* for the epilepsy testbed.

Written 26–27 Nov 2026 (PT). Supersedes/augments the brief note in `PUBLIC_DATA_INPUTS.md` line 68.

---

## 1. The study, verified against the open-access full text

- **Citation.** Balabandian M, Manavi MA, Lesani A, Mohammad Jafari R, Shafaroodi H, Heidari N,
  Mirnajafi-Zadeh J, Foroumadi A, Afrooghe A, Dehpour AR. *Psilocin, A Psychedelic Drug, Exerts
  Anticonvulsant Effects Against PTZ- and MES-Induced Seizures in Mice via 5-HT1A and CB1 Receptors:
  Involvement of Nitrergic, Opioidergic, and Kynurenine Pathways.* Pharmacol Res Perspect. 2025;13(2):e70079.
  doi:10.1002/prp2.70079. PMID 39996441. PMCID PMC11851161. License CC BY-NC-ND (open access).
- **Source read.** Europe PMC full-text XML of PMC11851161 (fetched 27 Nov 2026), i.e. the actual article,
  not a secondary summary.
- **Subject.** Mice (in vivo behavioural + ECoG + western blot). Psilocin = 4-hydroxy-DMT, the active
  metabolite of psilocybin, given i.p. Acute dosing.
- **Seizure models.** PTZ (pentylenetetrazole) clonic-seizure-threshold test (CST, reported as mg/kg of PTZ);
  MES (maximal electroshock) for generalised tonic–clonic seizures. ECoG recordings of cortical activity.

### 1.1 Dose–response (the "window" that makes it gate-like)
Doses tested: 0.03, 0.5, 1, 3, 5, 10, 20 mg/kg i.p. **Only 3 and 5 mg/kg raised CST** (anticonvulsant),
ANOVA F[7,35]=6.25, p=0.0002. **3 mg/kg was the most effective.** Higher doses (10, 20 mg/kg) did **not**
increase CST. This inverted-U / bounded-window behaviour is the single most "gate-like" feature of the result.

### 1.2 Time course (onset + a long latch)
At 3 mg/kg: **no effect at 15 min** before PTZ; **significant at 30 min** (peak, F[5,27]=15.61, p<0.0001);
weaker but still significant at 45 min; a significant CST elevation persisted at **24 h**; and a significant
anticonvulsant effect was **still present 9 days after a single injection**. So the gate has a delayed onset
and an unusually long "held-open" tail from one dose.

### 1.3 ECoG
Psilocin + PTZ showed delayed onset and reduced amplitude, frequency and **duration of epileptiform
discharges** vs PTZ alone.

### 1.4 Mechanism — pathway knockouts (each *diminished* the anticonvulsant effect)
Pretreatment with any of the following reduced psilocin's effect, implicating that pathway:
| Pretreatment | Dose/role | Pathway implicated |
|---|---|---|
| **AM-251** | 1 mg/kg, CB1 antagonist | **CB1 receptor** |
| **1-MT** | 1 mg/kg, IDO inhibitor | **kynurenine pathway** |
| **L-NAME** | NOS inhibitor | **nitrergic / NO** |
| **sildenafil** | PDE5 inhibitor | **cGMP** |
| **naltrexone** | opioid antagonist | **opioidergic** |

### 1.5 Mechanism — western blot (expression changes after psilocin)
- **5-HT1A: upregulated.**
- **5-HT2A: no significant change** ("upregulation of 5-HT1A but not 5-HT2A").
- **IDO: downregulated** (kynurenine-pathway enzyme).
- **CB1: downregulated** (expression).

---

## 2. User summary vs the paper — discrepancy check

| User-supplied point | Paper | Verdict |
|---|---|---|
| 3 mg/kg i.p. anticonvulsant vs PTZ clonic and MES tonic-clonic | Yes; 3 mg/kg most effective, 5 mg/kg also works | **Confirmed** (add: it is a *window* 3–5 mg/kg; 10–20 mg/kg ineffective) |
| 5-HT1A upregulated | Yes (western blot) | **Confirmed** |
| CB1 expression downregulated; AM-251 (CB1 antagonist) blocks the effect | Both true | **Confirmed** (see subtlety below) |
| 5-HT2A no significant expression change | Yes | **Confirmed** |
| Kynurenine pathway involved; 1-MT blocks | Yes; IDO also downregulated | **Confirmed** |
| Nitrergic NO/cGMP | Yes; L-NAME and sildenafil block | **Confirmed** |
| Opioidergic | Yes; naltrexone blocks | **Confirmed** |

**No contradictions.** Every mechanistic claim in the user's summary matches the paper. Minor additions worth
recording:
- **It is a dose *window*, not monotonic** (3–5 mg/kg on; 10–20 off). This is central to the "on-off gate" framing.
- **CB1 subtlety (do not over-read).** CB1 *protein expression* goes *down*, yet the CB1 *antagonist* AM-251
  *blocks* the benefit. So CB1 *signalling is required* for the anticonvulsant effect even though receptor
  expression falls. The mapping must therefore treat "CB1 involvement" as a **required pathway node**, not as a
  simple "more CB1 = better." This is the kind of nuance that a naive gate would get backwards.
- **Prevalence figure in the paper.** The paper states epilepsy affects "around 65 million" people. Our testbed
  uses the GBD 2021 figure (~51.7 M active; ~0.7% prevalence). Both are cited in the literature; we keep the
  GBD figure for the model and note the paper's as the older/rounded number. Minor, non-mechanistic.

### 2.1 Consistency with what the project already says
- `PUBLIC_DATA_INPUTS.md` line 68 already cites this paper correctly as "psilocin anticonvulsant in mice
  (PTZ, MES) via **5-HT1A and CB1**, not 5-HT2A" and already flags the user's earlier "via 5-HT2A" request as a
  discrepancy. **That line is correct and needs no reversal** — this note enriches it (dose window, the five
  blockers, IDO/CB1 downregulation). The earlier run-summary statement ("the mouse antiseizure effect ran
  through 5-HT1A/CB1, not 5-HT2A") is **consistent** with the verified paper.
- The only correction relative to the user's *original request wording* ("via 5-HT2A") was already made during
  the run and stands.

---

## 3. Why this maps naturally onto an Oroboro *gate*

Oroboro already models seizures as Levy-weighted transitions passing through **gates**. The paper's result is
not a change in how often a focus fires; it is a change in **thresholds** — raising CST, raising the barrier a
discharge must cross to become a clinical seizure, and doing so in a bounded dose window that antagonists can
switch off. That is exactly the semantics of a gate with (a) an on/off / threshold character, (b) required
upstream pathways, and (c) a persistence/latch.

### 3.1 Cross-reference table: Oroboro construct ↔ Balabandian mechanism
Framework definitions quoted from `caitlynrandels-del/Oroboro/consciousness-mapping/Sponge_Absorption_Mechanic.md`
and `Oroboro_Framework_Summary.md` (read via the GitHub connector, read-only, 27 Nov 2026), and from the
metastasis model `caitlynrandels-del/metastatic-cascade-analysis/metastatic_cascade_model.py`
(`permeability: float = 0.1`, `membrane_gate: float = 0.5`, `absorb()` accepts a cell when
`self.can_accept() and random.random() < self.membrane_gate`).

| Oroboro construct (quoted / defined) | In this epilepsy testbed | Balabandian mechanism it can represent | How |
|---|---|---|---|
| **Membrane / locking** = "Outer skin of the sponge" (gated entry) ; **`membrane_gate`** (metastasis `=0.5`, probabilistic accept) | sponge `circ_gate` 0.10 (network), `dorm_gate` 0.50 (relapse) | The receptor "gate": whether the anticonvulsant pathway is **engaged** (dose in window, pathways intact) | A boolean/threshold multiplier on the gates; antagonists set it off |
| **Recruitment / salience gate** `rec_eff = rec_p·(1 − refractory·e^(−since/τ))` | turns escaped discharge into a clinical seizure | **The CST-raising effect itself** (higher threshold = fewer discharges recruit) | multiply `rec_eff` by `gate_rec_mult < 1` while engaged |
| **Relapse gate** `dorm_gate` (sponge compartment 1) — *the run's dominant lever* | soaks reawakening attempts (+4) of quiescent foci into HELD | psilocin suppressing re-emergence; the long **9-day latch** | raise `dorm_gate` by `gate_dorm_mult > 1`; model the latch via lowered release permeability |
| **Permeability** = release rate (`permeability` 0.05/day; metastasis `0.1`) | how fast held content leaks back | The **24 h–9 day persistence** of a single dose | lower `perm` by `gate_perm_mult < 1` while engaged (slow leak = long latch) |
| **HardCapIntegration** = "Saturation point" ; **capacity**; **deformable (Flubber/Play-Doh) body** | sponge capacity 40, hardcap 3×, deform 0.5 | The dose *ceiling* (10–20 mg/kg no longer help): the gate saturates / closes | gate engagement limited to the dose window; above it, gate = off |
| **Levy weighting** = "Measure of what the sponge has absorbed" ; Levy transition threshold | clear +1, detach +7, fail +2, colonize +14 (seizure), exit +4 | Shifts the balance detach→fail (aborted) instead of detach→colonize (clinical) | lowering `rec_eff` moves weight from `colonize` to `fail` |
| **Cell-shade band switching** (cuts 0.2/0.4/0.7: dark/quiescent/active/seizing) | per-focus tone + energy highlight | Fewer foci cross into the **ictal/hot** band under the engaged gate | emergent: as `rec_eff`↓ and `dorm_gate`↑, fewer `colonize` events → shade stays lower (observable, not an input) |
| **Clearance vs residual dormancy** (`clear_p`; quiesce/wake; HELD) | eliminated vs seizure-free-but-residual | The long tail: a single dose keeps foci **held/quiescent** rather than cleared | effect routes through HELD (relapse reservoir), not through `clear_p`, matching "residual risk" semantics |
| **Heat-trace** = "Visible moisture / fill-level gradient" | fill gradient / shade feed | Visualising where the gate is holding load | descriptive output only |
| **Delta reconciliation / mesh consensus** (bit-identical parts; Levy ledger = heat-trace = seizure matrix) | every condition | — | the new gate must preserve exact reconciliation (focus-local application) |
| **Polarity mesh (NaCl) / magnetic detach-attach** | mesh locking, detach +7 = discharge escapes focus | *Weak analogy only.* The gate could be cast as raising the "detach/attach" polarity barrier, but the paper speaks to recruitment threshold, so we keep it on `rec_eff`/`dorm_gate`, **not** the mesh. Marked inferred. | not used as a primary channel |
| **Nexus / Transcriber / Dictator / Genesis / Levy** | recombination, chronicle, origin, event measure | house the gate's bookkeeping; gate events are Transcriber-chronicled | infrastructure |

Notes on provenance:
- Quoted construct definitions are the user's own (GitHub, above).
- The epilepsy-specific gate names, defaults, and the choice of channels (rec_eff / dorm_gate / permeability)
  are **inferred** by this note as a proposed instantiation; they are labelled as such and are off by default.
- **5-HT2A has no gate node** (no expression change) — it serves as a built-in negative control.
- FAA/ATC relay, wildfire, particle engines: **no genuine analogy** to this receptor result, so not mapped.

---

## 4. Proposed parameterization: a standard on/off "gate" layer

Treat the receptor/pathway modulation as a new **toggleable domain layer** `gate`, exactly like `sponge` and
`shading` (on/off, with a dict for details), so it inherits the existing toggle + ablation + adaptive-precision
machinery.

### 4.1 Parameters (proposed; defaults = OFF, i.e. no change to the completed run)
Add to `code/params_base.json` under `layers`: `"gate": false`.
When enabled, `layers.gate` is a dict parsed in `code/layers.py` (new `Gate` parser) and applied in
`code/epi_core.py` inside the daily loop:

```jsonc
"gate": {
  "rec_mult":   0.70,     // multiplies rec_eff while engaged (CST-raising; <1 = anticonvulsant). Primary channel.
  "dorm_mult":  1.60,     // multiplies sponge dorm_gate while engaged (strengthen relapse gate). Dominant if sponge on.
  "perm_mult":  0.50,     // multiplies sponge permeability while engaged (slow leak = 24h-9d latch).
  "dose":        3.0,     // mg/kg analogue (dimensionless input).
  "window":    [3.0,5.0], // engaged only if window[0] <= dose <= window[1] (inverted-U; 10-20 off).
  "onset_frac":  0.0,     // fraction of first day with no effect (30-min onset analogue; day-step, usually 0).
  "persist_days": 9,      // days a single engagement stays latched after a session.
  "pathways": {"ht1a":true, "cb1":true, "kyn":true, "no_cgmp":true, "opioid":true}
}
```

### 4.2 Engagement logic (proposed, in `epi_core.run`, focus-local so reconciliation stays exact)
```
window_ok = window[0] <= dose <= window[1]
pathways_ok = all(pathways.values())          # any blocker (antagonist) -> False -> gate OFF
active_today = any(session_day <= t <= session_day + persist_days for session_day in gate_days)
engaged = window_ok and pathways_ok and active_today
if engaged:
    rec_eff = rec_eff * rec_mult
    if sponge on: dorm_gate_eff = min(1.0, dorm_gate * dorm_mult); perm = perm * perm_mult
```
`gate_days` reuse the existing `PSILO_DAYS = [120,300,480,660]` (the gate is the mechanistic layer *under* the
psilocin instance). Gate engage/disengage are Transcriber-chronicled when `record=True`.

### 4.3 What each parameter changes
- `rec_mult` (<1): the core CST-raising effect; moves Levy weight from `colonize`→`fail`; the only channel that
  still works with the **sponge off**.
- `dorm_mult` (>1): routes extra reawakening attempts into HELD; **this is the dominant channel when the sponge
  is on**, because the completed run showed the sponge's benefit is almost entirely its relapse gate
  (`dorm_gate 0.9: +12.9 pt`, `0.1: −8.5 pt`; network gate & capacity ≈ 0). The proposed gate deliberately
  plugs into the lever the data already singled out.
- `perm_mult` (<1): produces the 24 h–9 day persistence without re-dosing (a latch).
- `window`/`dose`: the on/off inverted-U; above the window the gate is simply off.
- `pathways`: each boolean is a knockout switch standing for one antagonist experiment.

### 4.4 Relation to the completed run's relapse-gate finding
The run's headline mechanistic result was that **the sponge acts mainly through its relapse gate**. The proposed
receptor gate is engineered to express itself through that same relapse gate (`dorm_mult`) plus the recruitment
threshold (`rec_mult`). Prediction to test: **with the sponge OFF, the gate's `dorm_mult` and `perm_mult`
channels are inert and only `rec_mult` acts** — a clean internal consistency check that ties the pharmacology to
the architecture's already-identified dominant lever.

---

## 5. Test plan (do NOT run the full sim here; this is the design)

Use the existing harness: toggle + ablation + the **adaptive precision stop rule** (±1 pt on P(seizure-free 12 m),
run cap) and **delta reconciliation** (bit-identical 2- and 3-part partitions) already applied to every condition.

1. **Toggle.** `gate:false` (baseline) vs `gate:{...defaults, all pathways true}`. Expect seizure-freedom ↑.
2. **Pathway ablation (reproduce the antagonists).** Turn each pathway false one at a time:
   `cb1`=AM-251, `kyn`=1-MT, `no_cgmp`=L-NAME/sildenafil, `opioid`=naltrexone. Expect the effect to collapse
   toward baseline for each — matching Fig 2. (`ht1a` kept as the required "up" node; `5-HT2A` has no node =
   negative control, so there is nothing to ablate, which is itself a check.)
3. **Dose sweep.** `dose` ∈ {0.5, 1, 3, 5, 10, 20}. Expect benefit only at 3 and 5 (inverted-U), reproducing
   Fig 1A.
4. **Persistence.** `persist_days` ∈ {0, 1, 9}. Expect larger cumulative benefit as the latch lengthens.
5. **Sponge interaction.** Run each of the above with `sponge:true` and `sponge:false`. Expect the `dorm_mult`
   and `perm_mult` channels to be inert with the sponge off (prediction in §4.4).
6. **Reconciliation guard.** Confirm `shade_recon_bad == 0` and bit-identical parts for every gate condition
   (the gate is applied focus-locally, so this should hold).
7. **No-history cohort.** Optionally apply the gate in `code/nohist.py` (people without a seizure history) to
   check it changes nothing there (the paper's effect is on seizure threshold in seizure models, not on
   seizure-free brains) — an expected null.

### 5.1 Illustrative micro-check (NOT the real simulation)
A throwaway toy (200k draws, `/tmp`, `prop~Poisson(0.8)`, `rec_p=0.35`) to sanity-check the *direction* only:
- multiplying `rec_eff` by 0.70 drops P(any clinical seizure that day) from **0.2450 → 0.1781 (−6.68 pt)**;
- the dose gate opens only for 3 and 5 mg/kg and is off for 0.5/1/10/20.

This confirms the sign and the window shape; it is **not** a result and uses none of the calibrated model.

---

## 6. Limitations
- **Animal, acute, threshold endpoint.** CST↑/MES protection in mice is not "seizure freedom" in people; the
  mapping borrows a *mechanism shape*, not an efficacy claim.
- **CB1 direction is subtle** (expression down, but antagonist blocks); the gate treats CB1 as a *required
  node*, a simplification.
- **Dose is a dimensionless analogue**; mg/kg does not translate across the model.
- Pathway nodes are modelled as independent AND switches; the real pathways interact.
- The gate's defaults (`rec_mult` etc.) are **assumptions**, not fitted; they are off by default and must be
  swept, not asserted.
- Everything here is **speculative architecture testing**. No clinical claims, no medical advice.

---

## 7. Files touched by this note
- `GATE_NOTE.md` (this file).
- `CELL_SHADING.md` — added a cross-reference to the gate.
- `MAPPING.md` — added a gate row + pointer.
- `PUBLIC_DATA_INPUTS.md` — enriched the Balabandian line (dose window, blockers, IDO/CB1 downregulation).
- `ITERATION_LOG.md` — logged the reexamination.
- `paper_addendum_gate.md` — publication-ready section for the other agent's PDF (I did **not** touch `paper/`).
- `sources/` — added `balabandian_2025_abstract.txt`.
