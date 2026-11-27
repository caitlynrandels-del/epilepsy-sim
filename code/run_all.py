#!/usr/bin/env python3
"""Main runs: every condition in experiments.py with the adaptive stop rule, paired (common-random-number) contrasts, synergy of
combinations, layer effects, sponge sweep, and the no-seizure-history cohort for psilocybin. Writes ../data/*.csv."""
import os, sys, json, copy, time, math
import numpy as np, pandas as pd
from multiprocessing import Pool
import epi_core as C, harness as H, experiments as X, targets as TG
OUT = os.path.join(C.HERE, "..", "data"); RAW = os.path.join(OUT, "raw"); os.makedirs(RAW, exist_ok=True)
PAIRCOLS = ["batch", "pid", "sf12", "seiz_obs", "residual", "eliminated", "cluster_days_obs", "musico", "dep", "photo", "cat", "fem"] + ["on_" + k for k in C.DRUGS]
SETS = ["FULL_anchored", "FULL_free", "CORE_anchored", "CORE_free"]
def _withshade(s):
    P = H.load_set(s)
    if s.startswith("FULL"): P["layers"]["shading"] = True    # observational layer: added after calibration, cannot change the fit (verified in preflight)
    return P
def init():
    for s in SETS: H.register(s, _withshade(s))
    H.register("MAIN", _withshade("FULL_anchored"))
def work(cond):
    init() if not H.PSETS else None
    name, D, info, tr = H.run_condition(cond)
    s = H.summarize(D); s.update(name=name, group=cond["group"]); info["name"] = name
    D[[c for c in PAIRCOLS if c in D]].to_pickle(os.path.join(RAW, f"{name}.pkl.gz"))
    if tr is not None: json.dump(tr, open(os.path.join(RAW, f"{name}_sponge_trace.json"), "w"))
    return s, info
def pair(a, b, key, mask=None):
    A = pd.read_pickle(os.path.join(RAW, f"{a}.pkl.gz")); B = pd.read_pickle(os.path.join(RAW, f"{b}.pkl.gz"))
    return H.paired(A, B, key, mask)
if __name__ == "__main__":
    init(); t0 = time.time(); conds = X.conds()
    only = sys.argv[1:]  # optional subset
    if only: conds = [c for c in conds if c["name"] in only]
    summ, infos = [], []
    with Pool(int(os.environ.get("EPI_PROCS", 7)), initializer=init) as pool:
        for s, info in pool.imap_unordered(work, conds):
            summ.append(s); infos.append(info)
            print(f"[{len(summ)}/{len(conds)}] {s['name']}: persons {info['persons']} ({info['stop_reason']}), SF12 {s['p_sf12']:.3f}, seiz/yr {s['seiz_per_yr']:.2f}, "
                  f"recon_bad {info['recon_bad']}, obs_bad {info['obs_bad']}, checks_bad {info['checks_bad']}, {info['seconds']}s", flush=True)
    S = pd.DataFrame(summ); I = pd.DataFrame(infos)
    S.to_csv(os.path.join(OUT, "summary_conditions.csv"), index=False); I.to_csv(os.path.join(OUT, "run_info_conditions.csv"), index=False)
    print("total", round(time.time() - t0), "s")
