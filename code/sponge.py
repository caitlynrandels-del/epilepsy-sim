"""Sponge / absorption intermediary, Caitlyn Randels' definition (Oroboro/consciousness-mapping/Sponge_Absorption_Mechanic.md),
adapted from the v4 metastasis testbed (oroboro-multidb-sim-v4/code/sponge.py) to the epilepsy testbed. Speculative modeling only.

Definition implemented: a porous structure between the independent reduced states (Parts = groups of neural circuits/foci)
and their reconciled whole (the Nexus whole-brain recombination). It absorbs local deltas / heat / load / mesh noise without
tight coupling; it has capacity (saturation point = HardCapIntegration) and permeability (release rate); membrane/locking = outer
skin (gated entry); Levy = measure of absorbed content; deformable (Flubber / Play-Doh) body = capacity stretches under sustained
load up to HardCap; heat-trace = logged fill ("moisture") gradient. Not a replacement for Nexus or Genesis: the medium between them.

Epilepsy mapping (all parameter VALUES are assumptions; nothing public measures them):
  compartment 0 = network reservoir: soaks ESCAPED DISCHARGES (an interictal discharge that left its focus, Levy +7) before they
                  reach the whole-brain recruitment gate; releases them later at `permeability` (they then try to recruit again).
  compartment 1 = relapse reservoir: soaks REAWAKENING ATTEMPTS of quiescent foci (Levy +4); the held focus is inert while held
                  and is released back to quiescence.
  availability is computed from YESTERDAY's reconciled whole-brain fill (lagged Nexus channel), so parts are never coupled
  directly -> whole-vs-decomposed runs stay bit-identical with the sponge on.

Two layers, as in v4:
  1. BookkeepingSponge (observer only; no RNG, no writes) - this file.
  2. Biological buffer - implemented in epi_core.run (circuit state HELD and held-discharge counters), defaults DEFAULT_BIO.
"""
import numpy as np
DEFAULT_BIO = dict(enabled=True, circ_gate=0.10, dorm_gate=0.50, capacity=40.0, hardcap_mult=3.0, deform=0.5, permeability=0.05, kill=0.0)
CHANNELS = ("census_delta", "levy", "heat", "load")

class BookkeepingSponge:
    """Observer. Per channel: inflow = |delta|; absorbed = min(inflow, cap - fill); spill = rest (HardCap overflow);
    release = permeability x fill -> reconciliation stream; finish() squeezes the remainder. Checks conservation and that the
    reconciled Levy stream equals the model's Levy total."""
    def __init__(self, capacity=None, permeability=0.2, hardcap_mult=3.0, deform=0.5):
        self.cap0 = dict(census_delta=5.0, levy=5000.0, heat=50.0, load=0.5) if capacity is None else dict(capacity)
        self.cap = dict(self.cap0); self.perm = permeability; self.hard = {k: v * hardcap_mult for k, v in self.cap0.items()}
        self.hm = hardcap_mult; self.deform = deform
        self.fill = {k: 0.0 for k in CHANNELS}; self.inflow = {k: 0.0 for k in CHANNELS}; self.out = {k: 0.0 for k in CHANNELS}
        self.spill = {k: 0.0 for k in CHANNELS}; self.load_ema = {k: 0.0 for k in CHANNELS}; self.trace = []; self.sat = {k: 0 for k in CHANNELS}
    def step(self, s):
        d = dict(census_delta=abs(s["part_census"] - s["nexus_census"]), levy=s["levy_inc"], heat=s["heat_inc"], load=max(0.0, s["load"] - 1.0))
        row = {}
        for k in CHANNELS:
            x = float(d[k]); self.inflow[k] += x
            a = min(x, max(0.0, self.cap[k] - self.fill[k])); self.spill[k] += x - a; self.fill[k] += a
            r = self.perm * self.fill[k]; self.fill[k] -= r; self.out[k] += r
            if self.fill[k] >= self.cap[k] - 1e-12: self.sat[k] += 1
            self.load_ema[k] = 0.8 * self.load_ema[k] + 0.2 * min(1.0, self.fill[k] / self.cap[k])
            tgt = min(self.hard[k], self.cap0[k] * (1 + self.deform * self.load_ema[k] * (self.hm - 1)))
            self.cap[k] = max(self.cap0[k], self.cap[k] + 0.2 * (tgt - self.cap[k])); row[k] = self.fill[k] / self.cap[k]
        self.trace.append(row)
    def finish(self, res):
        for k in CHANNELS: self.out[k] += self.fill[k]; self.fill[k] = 0.0
        cons = all(abs(self.inflow[k] - self.out[k] - self.spill[k]) < 1e-6 * max(1.0, self.inflow[k]) for k in CHANNELS)
        levy_ok = abs(self.out["levy"] + self.spill["levy"] - res["levy_total"]) < 1e-6 * max(1.0, res["levy_total"])
        res.update(bk_conservation_ok=cons, bk_levy_matches_model=levy_ok, bk_spill_levy=self.spill["levy"], bk_sat_days_levy=self.sat["levy"],
                   bk_peak_fill_levy=max(r["levy"] for r in self.trace) if self.trace else 0.0)
