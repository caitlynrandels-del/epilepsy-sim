#!/usr/bin/env python3
"""Experiment harness with the v4 adaptive precision stop rule: batches of B persons (common random numbers: batch b of every
condition uses the same persons, same exposures, same random streams), stop when the Wilson 95% CI half-width of P(seizure-free
12 m), P(residual risk) and P(eliminated) is <= TARGET_HW, or at the cap. Per condition the first batch is re-run (a) decomposed
into K=2 parts (delta reconciliation, must be bit-identical) and (b) with every background processor + the bookkeeping sponge
attached (must leave the per-focus signature unchanged; conservation + Levy matching must hold). Every parameter set passes the
update sequence (register)."""
import os, json, copy, time, math
import numpy as np, pandas as pd
import epi_core as C, targets as TG, sponge as SPM, background as BG, update_sequence as US
HERE = C.HERE; CAL = os.path.join(HERE, "..", "data", "calibration")
STOP = dict(target_hw=float(os.environ.get("EPI_HW", 0.01)), batch=int(os.environ.get("EPI_B", 2000)), min_batches=3, cap_batches=int(os.environ.get("EPI_CAP", 20)))
EVAL_SEED = 2026
VER_N = 400
def wilson(x, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = x / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
PSETS = {}
def register(name, P):
    PSETS[name] = US.apply_obj({}, lambda _o, P=P: copy.deepcopy(P), context=f"harness register parameter set {name}"); return PSETS[name]
def load_set(name):
    P = json.load(open(os.path.join(CAL, f"params_{name}.json"))); P.pop("_calibration", None); P.pop("_note", None); return P
KEEP = ["sf12", "residual", "eliminated", "seiz_obs", "seiz_total", "cluster_days_obs", "sz_days", "first_day", "levy", "sponge_held",
        "n_active", "n_quiescent", "n_cleared", "n_held", "held_discharges", "fem", "cat", "photo", "musico", "dep", "resp", "ncirc"] + \
       ["attr_" + k for k in C.ATTR] + ["attrN_" + k for k in C.ATTR] + ["on_" + k for k in C.DRUGS] + ["levy_" + k for k in C.KINDS]
SHADE_KEEP = ["shade_mean_obs", "shade_peak_obs", "shade_final"] + [f"band{b}_days_obs" for b in range(4)] + [f"levy_band{b}" for b in range(4)]
def run_condition(cond):
    """cond: dict(name, pset, layers (optional override), inst, stop (optional overrides), keys (precision keys))"""
    P = copy.deepcopy(PSETS[cond["pset"]])
    if cond.get("layers") is not None: P["layers"] = cond["layers"]
    if cond.get("param_over"):
        for a, kv in cond["param_over"].items():
            if isinstance(kv, dict): P[a] = dict(P.get(a, {}), **kv) if isinstance(P.get(a), dict) else kv
            else: P[a] = kv
    inst = cond.get("inst") or {}
    st = dict(STOP, **(cond.get("stop") or {})); keys = cond.get("keys", ["sf12", "residual", "eliminated"])
    rows = []; ver = dict(recon_n=0, recon_bad=0, obs_n=0, obs_bad=0, checks_bad=0); b = 0; reason = "cap"; t0 = time.time(); extra = {}
    while b < st["cap_batches"]:
        o = C.run(P, inst, seed=EVAL_SEED, batch=b, n=st["batch"])
        a = o["_agg"]; ver["checks_bad"] += int(not (a["census_ok"] and a["levy_ok"] and a["consensus_ok"] and a["sponge_ok"] and a["shading_ok"]))
        if b == 0:
            w = C.run(P, inst, seed=EVAL_SEED, batch=999, n=VER_N); d = C.run(P, inst, seed=EVAL_SEED, batch=999, n=VER_N, mode="decomposed", K=2)
            ver["recon_n"] += 1; ver["recon_bad"] += int(not C.reconcile(w, d)["consistent"])
            ob = C.run(P, inst, seed=EVAL_SEED, batch=999, n=VER_N, observers=BG.all_background() + [SPM.BookkeepingSponge()])
            r = ob["_observers"]; ver["obs_n"] += 1
            ver["obs_bad"] += int(ob["_sig"] != w["_sig"] or not r["bk_conservation_ok"] or not r["bk_levy_matches_model"])
            extra.update({k: v for k, v in r.items() if k.startswith("bg_") or k.startswith("bk_")})
            if "_sp_trace" in o: extra["sp_trace_b0"] = o["_sp_trace"]
        df = pd.DataFrame({k: np.asarray(o[k]) for k in KEEP}); df["batch"] = b; df["pid"] = np.arange(len(df))
        for k in SHADE_KEEP:
            if k in o: df[k] = np.asarray(o[k])
        if "shade_recon_bad" in o: ver["shade_recon_bad"] = ver.get("shade_recon_bad", 0) + int(o["shade_recon_bad"])
        if "sp_hardcap_days" in o: df["sp_hardcap_days"] = o["sp_hardcap_days"]
        rows.append(df); b += 1
        if b >= st["min_batches"]:
            D = pd.concat(rows); nn = len(D)
            hw = max((lambda lo_hi: (lo_hi[1] - lo_hi[0]) / 2)(wilson(int(D[k].sum()), nn)) for k in keys)
            if hw <= st["target_hw"]: reason = "precision"; break
    D = pd.concat(rows, ignore_index=True)
    return cond["name"], D, dict(ver, batches=b, persons=len(D), stop_reason=reason, seconds=round(time.time() - t0, 1), **{k: v for k, v in extra.items() if k != "sp_trace_b0"}), extra.get("sp_trace_b0")
def summarize(D):
    n = len(D); s = dict(persons=n)
    for k in ("sf12", "residual", "eliminated"):
        x = int(D[k].sum()); lo, hi = wilson(x, n); s[f"p_{k}"] = x / n; s[f"p_{k}_lo"] = lo; s[f"p_{k}_hi"] = hi
    m = D.seiz_obs.astype(float); s["seiz_per_yr"] = m.mean(); h = 1.96 * m.std(ddof=1) / math.sqrt(n); s["seiz_per_yr_lo"] = m.mean() - h; s["seiz_per_yr_hi"] = m.mean() + h
    szo = D.seiz_obs > 0; s["seiz_per_yr_median_if_any"] = float(m[szo].median()) if szo.any() else 0.0
    s["cluster_given_sz"] = float((D.cluster_days_obs[szo] > 0).mean()) if szo.any() else float("nan")
    sz = D.seiz_total > 0
    for k in C.ATTR:
        s["attr_" + k] = float(D["attr_" + k][sz].mean()) if sz.any() else float("nan"); s["attrN_" + k] = float(D["attrN_" + k][sz].mean()) if sz.any() else float("nan")
    w = sz & D.fem.astype(bool); s["attr_catamenial_women"] = float(D.attr_catamenial[w].mean()) if w.any() else float("nan")
    na = sum(D["attr_" + k].astype(int) for k in TG.SURVEY_TRIGGERS); s["attr_any"] = float((na[sz] >= 1).mean()) if sz.any() else float("nan")
    s["attr_two_plus"] = float((na[sz] >= 2).mean()) if sz.any() else float("nan")
    s["levy_mean"] = D.levy.mean(); s["sponge_held_mean"] = D.sponge_held.mean(); s["quiescent_foci_mean"] = D.n_quiescent.mean(); s["cleared_foci_mean"] = D.n_cleared.mean()
    for k in C.KINDS: s["levy_" + k + "_mean"] = D["levy_" + k].mean()
    if "sp_hardcap_days" in D: s["sp_hardcap_any"] = float((D.sp_hardcap_days > 0).mean())
    if "shade_mean_obs" in D:
        s["shade_mean"] = D.shade_mean_obs.mean(); s["shade_peak_mean"] = D.shade_peak_obs.mean()
        s["shade_mean_sf"] = D.shade_mean_obs[D.sf12.astype(bool)].mean() if D.sf12.any() else float("nan")
        s["shade_mean_seizing"] = D.shade_mean_obs[~D.sf12.astype(bool)].mean() if (~D.sf12.astype(bool)).any() else float("nan")
        bd = np.array([D[f"band{b}_days_obs"].sum() for b in range(4)], float); s.update({f"band{b}_share": bd[b] / bd.sum() for b in range(4)})
        lb = np.array([D[f"levy_band{b}"].sum() for b in range(4)], float); s.update({f"levy_band{b}_share": lb[b] / lb.sum() for b in range(4)})
    ob = {k: s.get(k) for k in TG.TARGETS}; ob["sf12"] = s["p_sf12"]; s["fit_score"] = TG.score(ob)[0]; s["fit_in_band"] = sum(TG.in_band(ob).values())
    for g in ("photo", "musico", "cat", "dep"):
        G = D[D[g].astype(bool)]
        if len(G): s[f"sub_{g}_n"] = len(G); s[f"sub_{g}_sf12"] = G.sf12.mean(); s[f"sub_{g}_seiz_per_yr"] = G.seiz_obs.mean()
    for k in C.DRUGS:
        G = D[D["on_" + k].astype(bool)]
        if len(G): s[f"on_{k}_n"] = len(G); s[f"on_{k}_sf12"] = G.sf12.mean(); s[f"on_{k}_seiz_per_yr"] = G.seiz_obs.mean()
    return s
def paired(D, B, key, mask=None):
    """paired (common-random-number) difference D - B over the persons present in both; returns mean diff and 95% CI."""
    j = D.merge(B, on=["batch", "pid"], suffixes=("", "_b"))
    if mask is not None: j = j[mask(j)]
    x = j[key].astype(float) - j[key + "_b"].astype(float); n = len(x)
    if n < 2: return float("nan"), float("nan"), float("nan"), n
    h = 1.96 * x.std(ddof=1) / math.sqrt(n); return float(x.mean()), float(x.mean() - h), float(x.mean() + h), n
