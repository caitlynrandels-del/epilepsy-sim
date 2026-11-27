#!/usr/bin/env python3
"""Final reconciled observables of the MAIN baseline with 95% CIs (Wilson for proportions, normal for means), compared with the public
target bands. Re-runs the baseline condition (identical seeds -> identical to run_all) to get the per-person attribution flags.
Writes ../data/final_observables.csv."""
import os, pandas as pd, numpy as np
import harness as H, run_all as R, targets as TG, epi_core as C
R.init()
name, D, info, _ = H.run_condition(dict(name="baseline", group="baseline", pset="MAIN"))
n = len(D); rows = []
def prop(key, mask, target=None):
    x = D[key][mask].astype(bool); k, m = int(x.sum()), int(mask.sum()); lo, hi = H.wilson(k, m)
    rows.append(dict(observable=key + ("_women" if key == "attr_catamenial" and target else ""), n=m, value=k / m, lo=lo, hi=hi, target_lo=target[0] if target else np.nan, target_hi=target[1] if target else np.nan))
allm = pd.Series(True, index=D.index); sz = D.seiz_total > 0; szo = D.seiz_obs > 0
B = {k: (v[1], v[2]) for k, v in TG.TARGETS.items()}; B["attr_catamenial"] = B["attr_catamenial_women"]; B["cluster_any"] = B["cluster_given_sz"]
prop("sf12", allm, B.get("sf12")); prop("residual", allm); prop("eliminated", allm)
D["cluster_any"] = D.cluster_days_obs > 0; prop("cluster_any", szo, B.get("cluster_any"))
for k in ("stress", "sleep", "miss", "ill"): prop("attr_" + k, sz, B.get("attr_" + k))
prop("attr_catamenial", sz & D.fem.astype(bool), B.get("attr_catamenial"))
na = sum(D["attr_" + k].astype(int) for k in TG.SURVEY_TRIGGERS)
D["attr_any"] = na >= 1; D["attr_two_plus"] = na >= 2
prop("attr_any", sz, B.get("attr_any")); prop("attr_two_plus", sz, B.get("attr_two_plus"))
for k in ("alcohol", "binge", "weather", "sensory", "photic", "music"): prop("attr_" + k, sz); prop("attrN_" + k, sz)
for k in ("stress", "sleep", "miss", "ill", "catamenial"): prop("attrN_" + k, sz)
m = D.seiz_obs.astype(float); h = 1.96 * m.std(ddof=1) / np.sqrt(n)
rows.append(dict(observable="seizures_per_person_year", n=n, value=m.mean(), lo=m.mean() - h, hi=m.mean() + h))
if "shade_mean_obs" in D:
    s = D.shade_mean_obs; h = 1.96 * s.std(ddof=1) / np.sqrt(n); rows.append(dict(observable="whole_brain_shade_mean", n=n, value=s.mean(), lo=s.mean() - h, hi=s.mean() + h))
out = pd.DataFrame(rows); out["in_band"] = (out.value >= out.target_lo) & (out.value <= out.target_hi)
out.to_csv(os.path.join(C.HERE, "..", "data", "final_observables.csv"), index=False)
print(out.round(4).to_string()); print(info["recon_bad"], info["obs_bad"], info["checks_bad"], info.get("shade_recon_bad"))
