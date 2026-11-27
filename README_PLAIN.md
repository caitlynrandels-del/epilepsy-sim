# What this is, in plain language

**This is a computer experiment about a modelling architecture, not medical research.** It does not say anything reliable about any real person's seizures, medications or drug use. Please do not use it to make health decisions. If you have questions about epilepsy, triggers or medicines, ask a neurologist or pharmacist.

## The idea
Caitlyn's Oroboro architecture was first tested on cancer spread (metastasis). Here the same machinery is pointed at epilepsy:
- Each virtual brain has 1–4 "hot spots" (foci) that can fire small discharges.
- Usually the brain stops a discharge locally. Sometimes it escapes and, if the whole brain gets recruited, becomes a seizure.
- Medication damps the hot spots. Missed doses, stress, poor sleep, illness, menstrual-cycle phases, heavy drinking, weather and other triggers make firing more likely on the days they happen.
- A "sponge" soaks up some escaped activity and some attempts by quiet hot spots to wake up again.
- Every brain is simulated both as one whole and as separate pieces. The pieces always add back up exactly to the whole ("delta reconciliation"), and this was checked in every run.
- **Cell shading** (a provisional idea, since we couldn't find Caitlyn's own definition) colours each hot spot like a cartoon: dark, calm blue, active amber, or seizure red. The whole brain's colour is exactly the sum of its parts.

We tuned the model so that roughly 7 in 10 virtual people become seizure-free on medication, and so that the triggers they would "report" look like real surveys. It got 5 of 9 targets in range; the misses are listed honestly in RESULTS_SUMMARY.md.

## What came out (inside the model only)
- **Missed medication** was by far the biggest driver. Removing it raised the share of seizure-free people by about 7 points.
- **Stress and sleep loss** are reported a lot but each mattered modestly. Triggers combine: stress plus missed doses was worse than the two added together.
- **Moderate drinking** did nothing (as in the published study used); binges did a little.
- **Music** only mattered for the extremely rare people with musicogenic epilepsy, and then mostly the emotional music did. At realistic rarity there was no population effect.
- **Psilocybin:** under all the assumed scenarios the effect was small. In people with no seizure history, no extra seizures could be detected unless an SSRI assumption was layered on top. All psilocybin numbers are guesses; no real dose data exist.
- **SSRIs and stimulants:** the result depends entirely on which body of evidence you believe. The model shows how far apart those views are; it cannot pick between them.
- **People "blame" common exposures.** Weather and music were often blamed even when they caused nothing.
- **The sponge mattered a lot.** It works mainly by keeping quiet hot spots quiet, and it smoothed out the stress-plus-sleep combination.
- **Cell shading** shows that the "red" seizure colour covers only 3% of days but 80% of the system's activity score. As a pure display it changes nothing. If shading is allowed to fill the sponge, outcomes get slightly worse.

See RESULTS_SUMMARY.md for numbers with uncertainty ranges, and charts/ for pictures.
