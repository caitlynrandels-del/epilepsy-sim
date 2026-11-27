<!-- Publication-ready section for the epilepsy study PDF. Prepared by the gate-analysis agent.
     Drop in as a subsection (e.g. under Discussion or a new "Candidate receptor gate" section).
     Do NOT treat as clinical guidance. Speculative architecture testbed only. -->

### A candidate receptor/pathway "on-off gate" from psilocin pharmacology

A recent controlled mouse study (Balabandian et al., 2025, *Pharmacology Research & Perspectives*
13(2):e70079) reports that psilocin, the active metabolite of psilocybin, raises the clonic seizure
threshold (pentylenetetrazole test) and protects against maximal-electroshock tonic–clonic seizures.
We verified the paper against its open-access full text. Its findings are notable here not as an efficacy
claim but because their *shape* is gate-like and maps cleanly onto the architecture under test.

Three features define that shape. First, the effect occupies a **bounded dose window**: only 3 and 5 mg/kg
(i.p.) raised the threshold, with 3 mg/kg most effective, while 10 and 20 mg/kg did not — an inverted-U, not
a monotonic dose response. Second, the effect has a **delayed onset and a long latch**: absent at 15 minutes,
peaking at 30 minutes, and still significant 24 hours and even 9 days after a single dose. Third, it is
**pathway-gated**: pretreatment with AM-251 (CB1 antagonist), 1-MT (kynurenine/IDO inhibitor), L-NAME (nitric
oxide synthase inhibitor), sildenafil (cGMP), or naltrexone (opioid antagonist) each diminished the effect,
and western blotting showed upregulated 5-HT1A, downregulated IDO and CB1, and no change in 5-HT2A.

We map this onto the testbed as a proposed, toggleable **gate layer** (off by default), engaging only inside a
dose window with its required pathways intact and remaining latched for a persistence interval. When engaged it
raises the whole-brain recruitment threshold (the clonic-seizure-threshold analogue), strengthens the relapse
gate that returns reawakening foci to a held state, and lowers release permeability to reproduce the multi-day
persistence. Each required pathway is a separate switch, so an ablation of any one reproduces the corresponding
antagonist experiment; 5-HT2A, unchanged in the paper, provides a built-in negative control, and the dose sweep
should reproduce the inverted-U.

This design is deliberately aligned with the study's dominant mechanistic result reported earlier in this work:
the absorbent intermediary's benefit was almost entirely attributable to its relapse gate rather than its
network gate or capacity. Routing the proposed receptor gate through that same relapse gate yields a testable
prediction — with the intermediary disabled, only the recruitment-threshold channel should remain active — and
keeps the new construct consistent with delta reconciliation, which is preserved because the gate is applied at
the level of individual reduced states.

We did not run the full gated model for this paper; the construct, its parameters and its test plan (toggle,
per-pathway ablation, dose sweep, and on/off comparison of the absorbent layer, all under the adaptive-precision
stop rule) are documented in the project's gate note. As throughout, this is speculative architecture testing:
no clinical claim is made, and nothing here is medical advice.

*Reference:* Balabandian M, Manavi MA, Lesani A, Mohammad Jafari R, Shafaroodi H, Heidari N, Mirnajafi-Zadeh J,
Foroumadi A, Afrooghe A, Dehpour AR. Psilocin, A Psychedelic Drug, Exerts Anticonvulsant Effects Against PTZ- and
MES-Induced Seizures in Mice via 5-HT1A and CB1 Receptors: Involvement of Nitrergic, Opioidergic, and Kynurenine
Pathways. Pharmacol Res Perspect. 2025;13(2):e70079. doi:10.1002/prp2.70079. PMID 39996441.
