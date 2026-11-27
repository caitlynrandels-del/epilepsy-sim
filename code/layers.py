"""Switchable domain layers for the epilepsy testbed (v4 interface: P['layers'] = {'sponge': True/False/dict, name: True/False/dict}).
Absent/disabled -> exactly the core model. EVERY numeric value is an ASSUMPTION; the structure follows standard concepts named in
LAYERS.md. 'materials', 'physics' act on the biological sponge only (no effect when the sponge is off, by design); 'heat' is
observational; 'inhibition', 'hpa', 'kindling', 'network' act on seizure dynamics."""
import copy, numpy as np
DEFAULTS = {
 "materials": dict(enabled=True, porosity=0.7, porosity_ref=0.5, sat_exponent=2.0, hysteresis=0.5, elasticity=0.5),
 "physics": dict(enabled=True, pressure_k=1.0, diffusion_D=1.0, compression_k=2.0),
 "heat": dict(enabled=True, diffusion=0.2, dissipation=0.1),
 # GABAergic / inhibitory surround with exhaustion (immune-surveillance analogue): clearance odds x (1 + boost/(1 + D/K)), D = yesterday's discharges
 "inhibition": dict(enabled=True, boost=1.0, exhaustion_K=5.0),
 # HPA axis / stress-hormone load + trigger cascade: H_t = decay*H + stress_t ; rate x (1 + k*H) ; stress -> sleep loss, illness/binge -> missed dose
 "hpa": dict(enabled=True, decay=0.8, k=0.10, sleep_given_stress_mult=2.0, miss_given_ill_or_binge_mult=2.0),
 # 'seizures beget seizures' (Hawkes-type self-excitation of the focus that seized): rate x (1 + k * kin), kin decays with tau days
 "kindling": dict(enabled=True, k=0.5, tau=2.0),
 # whole-brain mesh coupling through the Nexus peer summary: rate x (1 + k * seizures yesterday in the same brain)
 "network": dict(enabled=True, k=0.3),
 # CELL SHADING (PROVISIONAL definition - none found in the user's repos/transcripts; see ../CELL_SHADING.md). Per-focus continuous shade
 # s in [0,1] = state tone (cleared 0, held 0.15, quiescent 0.25, active 0.5) + energy highlight 0.5*(1-exp(-(discharges + 3*seizures
 # + kindling charge)/energy_scale)), quantised cel-style into 4 bands at `bands`. Observational by default (feedback=0): it shades the
 # Levy events, the heat-trace and the reconciled whole-brain observable but never feeds back. feedback>0 = coupled variant: yesterday's
 # reconciled whole-brain shade darkens the sponge (availability x (1 - feedback*shade)), i.e. a 'hot' brain has a fuller sponge.
 "shading": dict(enabled=True, energy_scale=2.0, bands=[0.2, 0.4, 0.7], feedback=0.0),
}
NAMES = list(DEFAULTS); ALL_LAYERS = ["sponge"] + NAMES
def get(P, name):
    L = (P.get("layers") or {}).get(name)
    return L if (isinstance(L, dict) and L.get("enabled")) else None
def normalize(P):
    """True -> defaults; False/absent -> off; dict -> those parameters. 'sponge' is translated to P['sponge'] (sponge.DEFAULT_BIO + overrides)."""
    import sponge as _sp
    L = dict(P.get("layers") or {}); Q = dict(P); out = {}
    if "sponge" in L:
        v = L.pop("sponge")
        if v is True or (isinstance(v, dict) and v.get("enabled", True)):
            Q["sponge"] = dict(_sp.DEFAULT_BIO, **(v if isinstance(v, dict) else {})); Q["sponge"]["enabled"] = True
        else: Q.pop("sponge", None)
    for n, v in L.items():
        if v is True: out[n] = copy.deepcopy(DEFAULTS[n])
        elif v is False or v is None: continue
        else: out[n] = dict(DEFAULTS[n], **v)
    Q["layers"] = out
    return Q
# sponge helpers (identical rules to v4 layers.py)
def sponge_capacity_scale(P):
    L = get(P, "materials"); return (L["porosity"] / L["porosity_ref"]) if L else 1.0
def sponge_avail(P, fill, cap):
    L = get(P, "materials"); x = np.clip(fill / cap, 0.0, None)
    return np.maximum(0.0, 1.0 - (x ** L["sat_exponent"] if L else x))
def sponge_relax(P):
    L = get(P, "materials"); return 0.4 * L["elasticity"] if L else 0.2
def sponge_perm_factor(P, fill, cap, fill_prev2):
    f = np.ones_like(fill); L = get(P, "materials")
    if L: f = f * np.where(fill >= fill_prev2, 1 - L["hysteresis"], 1 + L["hysteresis"])
    Q = get(P, "physics")
    if Q:
        fr = fill / cap; f = f * np.maximum(0.0, 1 + Q["diffusion_D"] * (fr - fr.mean(axis=1, keepdims=True))) * (1 + Q["compression_k"] * np.maximum(0.0, fr - 1))
    return f
def sponge_gate_factor(P, load):
    Q = get(P, "physics"); return np.minimum(3.0, 1 + Q["pressure_k"] * load) if Q else 1.0
