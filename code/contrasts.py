#!/usr/bin/env python3
"""Paired contrasts (common random numbers) from ../data/raw/*.pkl.gz: condition minus reference, 95% CI of the per-person mean difference."""
import os, json, math, numpy as np, pandas as pd
import harness as H, experiments as X, epi_core as C
OUT = os.path.join(C.HERE, "..", "data"); RAW = os.path.join(OUT, "raw")
_cache = {}
def L(n):
    if n not in _cache: _cache[n] = pd.read_pickle(os.path.join(RAW, f"{n}.pkl.gz"))
    return _cache[n]
KEYS = ["sf12", "seiz_obs", "residual", "eliminated", "cluster_any"]
def prep(D): D = D.copy(); D["cluster_any"] = (D.cluster_days_obs > 0).astype(int); return D
def contrast(a, b, mask=None, label=""):
    A, B = prep(L(a)), prep(L(b)); r = dict(condition=a, reference=b, subset=label)
    for k in KEYS:
        m, lo, hi, n = H.paired(A, B, k, mask); r[f"d_{k}"] = m; r[f"d_{k}_lo"] = lo; r[f"d_{k}_hi"] = hi; r["n_paired"] = n
    return r
def interaction(ab, a, b, base, key):
    J = prep(L(ab)).merge(prep(L(a)), on=["batch", "pid"], suffixes=("", "_a")).merge(prep(L(b)), on=["batch", "pid"], suffixes=("", "_b")).merge(prep(L(base)), on=["batch", "pid"], suffixes=("", "_0"))
    x = J[key].astype(float) - J[key + "_a"] - J[key + "_b"] + J[key + "_0"]; n = len(x); h = 1.96 * x.std(ddof=1) / math.sqrt(n)
    return float(x.mean()), float(x.mean() - h), float(x.mean() + h), n
if __name__ == "__main__":
    S = pd.read_csv(os.path.join(OUT, "summary_conditions.csv")); have = set(S.name)
    rows = []
    for c in X.conds():
        n = c["name"]
        if n not in have or n == "baseline": continue
        if c["group"] == "trigger_only": ref = "triggers_NONE"
        elif n.startswith("layer_only"): ref = "baseline_allOFF_core"
        elif n.startswith("musicogenic_cohort") and n != "musicogenic_cohort_emotional0.2": ref = "musicogenic_cohort_emotional0.2"
        elif n.endswith("_spongeOFF") and n != "baseline_spongeOFF": ref = "baseline_spongeOFF"
        else: ref = "baseline"
        if ref not in have: continue
        rows.append(contrast(n, ref, label="all"))
        for k in C.DRUGS:
            if f"'{k}'" in str(c.get("inst")) or (c.get("inst") or {}).get(k):
                rows.append(contrast(n, ref, mask=lambda j, k=k: j["on_" + k].astype(bool), label=f"exposed to {k}"))
    if "musicogenic_cohort_emotional0.2" in have: rows.append(contrast("musicogenic_cohort_emotional0.2", "baseline", label="all (whole cohort made musicogenic-susceptible vs realistic prevalence)"))
    Ct = pd.DataFrame(rows); Ct.to_csv(os.path.join(OUT, "contrasts.csv"), index=False)
    # synergy / cascade interactions (exposure x2 combos)
    syn = []
    for ab, a, b, base in (("combo_stress+sleep_AMPx2", "stress_AMPx2", "sleep_AMPx2", "baseline"), ("combo_binge+sleep_AMPx2", "binge_AMPx2", "sleep_AMPx2", "baseline"),
                           ("combo_ill+miss_AMPx2", "ill_AMPx2", "miss_AMPx2", "baseline"), ("combo_stress+miss_AMPx2", "stress_AMPx2", "miss_AMPx2", "baseline"),
                           ("combo_stress+sleep_AMPx2_spongeOFF", "stress_AMPx2_spongeOFF", "sleep_AMPx2_spongeOFF", "baseline_spongeOFF"),
                           ("stim_threshold_plus_sleeploss", "stim_threshold_1.3", "stim_neutral_plus_sleeploss", "baseline")):
        if {ab, a, b, base} <= have:
            for k in ("seiz_obs", "sf12"):
                m, lo, hi, n = interaction(ab, a, b, base, k); syn.append(dict(combo=ab, a=a, b=b, base=base, key=k, interaction=m, lo=lo, hi=hi, n=n))
    pd.DataFrame(syn).to_csv(os.path.join(OUT, "synergy.csv"), index=False)
    print(Ct[["condition", "reference", "subset", "d_sf12", "d_sf12_lo", "d_sf12_hi", "d_seiz_obs", "d_seiz_obs_lo", "d_seiz_obs_hi"]].to_string())
    print(pd.DataFrame(syn).to_string())
