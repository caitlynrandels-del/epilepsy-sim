# GATE_NOTE.md — Psilocin On-Off Gate Analysis

**Speculative modeling only. No clinical claims or medical advice.**

## Source

Balabandian et al. (2025). Psilocin exerts anticonvulsant effects against PTZ- and MES-induced seizures in mice via 5-HT1A and CB1 receptors: involvement of nitrergic, opioidergic, and kynurenine pathways. *Pharmacol Res Perspect* 13(2):e70079.

## Key findings from the paper (verified against source)

- Modest doses (3 mg/kg and 5 mg/kg i.p.) reduced seizure incidence in mouse PTZ (clonic) and MES (tonic-clonic) models.
- 10 mg/kg and 20 mg/kg showed no effect — a bounded dose window, not a simple dose response.
- Onset ~30 minutes; effect still present at 9 days (latching behavior).
- 5-HT1A upregulated; CB1 expression downregulated (AM-251 blocks the effect).
- 5-HT2A expression unchanged.
- Blocking experiments implicate kynurenine pathway (1-MT), nitrergic/NO/cGMP, and opioidergic systems.

## Oroboro mapping (on-off gate)

The receptor/pathway modulation is treated as a switchable gate layer with:

- **Dose window**: only the 3–5 mg/kg equivalent range activates the gate.
- **Hold time / latch**: once activated, the gate remains in the “quiet-favoring” state for an extended period.
- **One switch per pathway**: CB1, kynurenine, nitric oxide, opioid. Each can be toggled independently to match the paper’s antagonist results.

### Construct mapping

| Oroboro construct              | Gate role                                      |
|--------------------------------|------------------------------------------------|
| Sponge membrane_gate / permeability | Primary absorption into quiet residual pool   |
| Cell-shade band threshold      | Switch between quiet and active/seizing bands |
| Levy-weighted transition       | Raises the weight required for seizure onset  |
| Polarity mesh / HardCap        | Bounds the gate so it cannot runaway          |
| Delta reconciliation           | Recombines independent circuit gates to whole-brain observable |

### Testable prediction

With the sponge compartment turned off, most of the gate’s protective effect should disappear. Prior runs showed the sponge works mainly by preventing quiet foci from reawakening (relapse gate). The psilocin gate is hypothesized to operate through the same channel.

## Instantiation proposal

Optional parameter `psilocin_gate` (default off):

- When on and inside the dose window: increase sponge absorption, raise Levy seizure threshold, bias shade toward quiet band.
- Outside window or with pathway antagonists: gate inactive or reversed.
- On/off toggle for direct comparison.

All parameters remain speculative. Architecture testbed only.
