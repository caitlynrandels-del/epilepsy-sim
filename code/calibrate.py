#!/usr/bin/env python3
"""Calibration of the epilepsy testbed to public observables (targets.py). Nelder-Mead on transformed parameters with common
random numbers (fixed calibration seed 101, n persons per evaluation). Every proposal is 'torched' (syntax->autocorrect pass of
the update sequence); every accepted best-iterate passes the full update sequence (quick fix -> UPDATE ALL -> undo -> Timestamp ->
do it again -> syntax/autocorrect) via update_sequence.apply_obj; the final set is committed with update_sequence.apply_update.
Scenarios: FULL_anchored (MAIN: all layers + sponge on; stress/sleep multipliers fixed at prospective-diary anchors, Haut 2007),
FULL_free (multipliers free), CORE_anchored, CORE_free (all layers + sponge off)."""
import os, sys, json, copy, time, math
import numpy as np
from scipy.optimize import minimize
import epi_core as C, targets as TG, update_sequence as US
HERE = C.HERE; OUT = os.path.join(HERE, "..", "data", "calibration"); os.makedirs(OUT, exist_ok=True)
FREE = [("cohort", "base_rate", "log"), ("cohort", "resp_frac", "logit"), ("dyn", "cluster_b", "log"), ("exposure", "p_stress", "logit"),
        ("exposure", "p_sleep", "logit"), ("exposure", "p_miss", "logit"), ("mult", "m_ill", "log1")]
FREE_MULT = [("mult", "m_stress", "log1"), ("mult", "m_sleep", "log1")]
def fwd(v, tr): return math.log(v) if tr == "log" else (math.log(v / (1 - v)) if tr == "logit" else math.log(v - 1 + 1e-9))
def inv(z, tr): return math.exp(z) if tr == "log" else (1 / (1 + math.exp(-z)) if tr == "logit" else 1 + math.exp(z))
def scen_params(name):
    P = C.load_params(); P.pop("_note", None)
    allon = name.startswith("FULL")
    P["layers"] = {k: allon for k in P["layers"]}
    return P
def main(name, n=3000, maxfev=140, seed=101):
    P0 = scen_params(name); keys = FREE + (FREE_MULT if name.endswith("free") else [])
    x0 = np.array([fwd(P0[a][b], tr) for a, b, tr in keys]); log = []; best = dict(s=1e9, P=None, ob=None); t0 = time.time()
    live = copy.deepcopy(P0)
    def build(z):
        Q = copy.deepcopy(P0)
        for (a, b, tr), zi in zip(keys, z): Q[a][b] = inv(float(zi), tr)
        Q, corr, errs = US.torch(Q, context=f"calibrate {name} proposal", log_path=False)
        return Q
    def f(z):
        nonlocal live
        Q = build(z); o = C.run(Q, seed=seed, n=n); ob = TG.observables(o); s, parts = TG.score(ob)
        log.append(dict(it=len(log), score=s, **{f"{a}.{b}": Q[a][b] for a, b, _ in keys}, **ob))
        if s < best["s"]:
            live = US.apply_obj(live, lambda _o, Q=Q: copy.deepcopy(Q), context=f"calibrate {name} best-iterate {len(log)} score {s:.4f}")
            best.update(s=s, P=copy.deepcopy(live), ob=ob)
        return s
    r = minimize(f, x0, method="Nelder-Mead", options=dict(maxfev=maxfev, xatol=1e-3, fatol=1e-4, initial_simplex=None, adaptive=True))
    import pandas as pd
    pd.DataFrame(log).to_csv(os.path.join(OUT, f"calib_trace_{name}.csv"), index=False)
    final = copy.deepcopy(best["P"]); final["_calibration"] = dict(scenario=name, score=best["s"], observables=best["ob"], in_band=TG.in_band(best["ob"]),
                                                                    n_eval=len(log), n_persons=n, seed=seed, free=[f"{a}.{b}" for a, b, _ in keys], seconds=round(time.time() - t0))
    target = os.path.join(OUT, f"params_{name}.json")
    rec = US.apply_update(target, final, context=f"calibrate {name} final write")
    print(name, "score", round(best["s"], 4), "verified", rec["verified"], {k: round(v, 3) for k, v in best["ob"].items()}, flush=True)
if __name__ == "__main__":
    main(sys.argv[1], n=int(os.environ.get("CAL_N", 3000)), maxfev=int(os.environ.get("CAL_FEV", 140)))
