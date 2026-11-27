#!/usr/bin/env python3
"""Psilocybin in people WITHOUT a seizure history (speculative; all effect sizes are assumptions). Cohort: one latent focus per
person, no antiseizure medication, the same everyday trigger exposures; base rate set so that P(any seizure per year) ~= epilepsy
incidence 61.44 / 100,000 person-years (Fiest 2017; ASSUMPTION that first-seizure risk ~ incidence). Precision rule on P(seizure
in last 365 d), half-width 0.0002, batches of 20,000, cap 300,000 persons. Outcome per 100,000 persons."""
import os, json, copy, math, numpy as np, pandas as pd
import epi_core as C, harness as H, experiments as X
from multiprocessing import Pool
OUT = os.path.join(C.HERE, "..", "data")
TARGET = 61.44e-5
def base_params():
    P = H.load_set("FULL_anchored"); return P
def cohort(br): return dict(n_circ_probs=[1.0], resp_frac=0.0, base_rate=br, eff_non_lo=0.0, eff_non_hi=0.0)
def pilot():
    P = base_params(); br = P["cohort"]["base_rate"] * 0.01
    for it in range(4):
        P2 = copy.deepcopy(P); P2["cohort"].update(cohort(br)); x = []
        o = C.run(P2, dict(no_asm=True), seed=55, batch=0, n=100000); p = 1 - o["sf12"].mean()
        print("pilot base_rate", br, "P(seizure/yr)", p, flush=True)
        if p <= 0: br *= 10; continue
        br = br * TARGET / p
    return br
def work(arg):
    name, inst, br = arg
    P = base_params(); P["cohort"].update(cohort(br)); H.register("NOHIST", P)
    inst = dict(inst, no_asm=True)
    name, D, info, _ = H.run_condition(dict(name=name, pset="NOHIST", inst=inst, keys=["sf12"], stop=dict(target_hw=0.0002, batch=20000, min_batches=3, cap_batches=15)))
    p = 1 - D.sf12.mean(); n = len(D); lo, hi = H.wilson(int((~D.sf12.astype(bool)).sum()), n)
    D[["batch", "pid", "sf12", "seiz_obs"]].to_pickle(os.path.join(OUT, "raw", f"nohist_{name}.pkl.gz"))
    return dict(name=name, persons=n, stop_reason=info["stop_reason"], p_seizure_yr_per100k=p * 1e5, lo=lo * 1e5, hi=hi * 1e5, recon_bad=info["recon_bad"], obs_bad=info["obs_bad"])
if __name__ == "__main__":
    br = pilot(); json.dump(dict(base_rate=br, target_per_yr=TARGET), open(os.path.join(OUT, "nohist_base_rate.json"), "w"))
    D = X.PSILO_DAYS
    conds = [("nohist_baseline", {}, br),
             ("nohist_psilo_low_neutral", dict(psilo=dict(days=D, mult=1.0, mult_next=1.0)), br),
             ("nohist_psilo_high_neutral", dict(psilo=dict(days=D, mult=1.0, mult_next=1.0)), br),
             ("nohist_psilo_low_exacerb", dict(psilo=dict(days=D, mult=1.5, mult_next=1.2)), br),
             ("nohist_psilo_high_exacerb", dict(psilo=dict(days=D, mult=3.0, mult_next=1.5, susceptible_frac=0.3, mult_susceptible=10.0, mult_next_susceptible=3.0)), br),
             ("nohist_psilo_high_exacerb_plus_ssri", dict(psilo=dict(days=D, mult=3.0, mult_next=1.5, susceptible_frac=0.3, mult_susceptible=10.0, mult_next_susceptible=3.0, ssri_interaction=1.5),
                                                          ssri=dict(target="all", mult=1.48, early_mult=2.35, early_days=30)), br)]
    with Pool(6) as pool: rows = pool.map(work, conds)
    R = pd.DataFrame(rows)
    B = pd.read_pickle(os.path.join(OUT, "raw", "nohist_nohist_baseline.pkl.gz"))
    for i, r in R.iterrows():
        A = pd.read_pickle(os.path.join(OUT, "raw", f"nohist_{r['name']}.pkl.gz")); A["any"] = (A.seiz_obs > 0).astype(int); B2 = B.copy(); B2["any"] = (B2.seiz_obs > 0).astype(int)
        m, lo, hi, n = H.paired(A, B2, "any"); R.loc[i, "excess_per100k"] = m * 1e5; R.loc[i, "excess_lo"] = lo * 1e5; R.loc[i, "excess_hi"] = hi * 1e5; R.loc[i, "n_paired"] = n
    R.to_csv(os.path.join(OUT, "nohist_psilocybin.csv"), index=False); print(R.to_string())
