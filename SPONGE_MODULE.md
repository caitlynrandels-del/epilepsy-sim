# SPONGE_MODULE.md: the sponge in the epilepsy testbed

Adapted from `Sponge_Absorption_Mechanic.md` (Oroboro) and v4 `SPONGE_MODULE.md`.

## Biological sponge (two compartments per brain)
- **Network reservoir.** Soaks escaped discharges (Levy +7) before they reach the recruitment gate. Gate: circ_gate 0.10.
- **Relapse reservoir.** Soaks reawakening attempts of quiescent foci (+4). Gate: dorm_gate 0.50.
- **Availability** comes from *yesterday's reconciled whole-brain fill*. This makes it partition-invariant and keeps delta reconciliation exact.
- **Fill parameters:** capacity 40 (HardCapIntegration), hard cap 3×, deformation 0.5, release by permeability 0.05/day, kill 0 (held content can be destroyed if kill > 0).
- **States:** held foci are in state HELD (cell shade 0.15, dark band).

## Bookkeeping sponge (observer)
- Mirrors the census, the Levy ledger, the heat-trace and load (caps 5, 5000, 50, 0.5).
- Conservation and Levy checks are done in every condition.
- With shading on, its heat input is the reconciled whole-brain shade.

## Findings
- Removing the sponge costs 10.2 pt of seizure freedom.
- Almost all of its benefit comes from the relapse gate (dorm_gate 0.9: +12.9 pt; 0.1: −8.5 pt). The network gate and capacity barely matter.
- kill 0.05 converts residual risk into elimination (+29.3 pt eliminated).
- It absorbs the stress × sleep synergy.
- Coupled cell shading acts only through it.
