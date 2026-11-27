"""Public observables used as calibration targets (bands from real sources; see ../PUBLIC_DATA_INPUTS.md).
Each target: (point, lo, hi, source key). Fit score = sum over targets of (distance outside band / band width)^2 + small pull to point."""
import numpy as np
TARGETS = {
 # Chen et al. 2018 JAMA Neurol (n=1795): 63.7% seizure-free >=1 y at last follow-up; Kwan & Brodie 2000 NEJM 64% (470 untreated);
 # WHO fact sheet: "up to 70%" could be seizure-free.
 "sf12": (0.637, 0.60, 0.70, "Chen2018;KwanBrodie2000;WHO"),
 # seizure clusters (>=3/24h) among people with ongoing seizures: 14.9% outpatient adults ... 43% diary study (Haut review 2022 / Seizure 2018 review)
 "cluster_given_sz": (0.29, 0.149, 0.43, "ClusterReview2018;Haut2022"),
 # self-reported precipitants among people with seizures
 "attr_stress": (0.41, 0.30, 0.56, "Frucht2000 30%;AIIMS2013 31%;EpiWatch2017 37%;Saudi2020 41%;TJU2007 49.5%;Nanjing2017 56%"),
 "attr_sleep": (0.35, 0.18, 0.52, "Frucht2000 18%;EpiWatch 18%;AIIMS 19.7%;TJU 35.5%;Nanjing 38.4%;Saudi 52%"),
 "attr_miss": (0.25, 0.07, 0.41, "EpiWatch 7%;Nanjing 20%;Saudi 38.5%;AIIMS 41%"),
 "attr_ill": (0.10, 0.06, 0.14, "EpiWatch fever/infection 6%;AIIMS fever 6.4%;Frucht fever/illness 14%"),
 "attr_catamenial_women": (0.20, 0.12, 0.28, "EpiWatch menses 12% (all);Frucht 28% (women with TLE)"),
 "attr_any": (0.65, 0.55, 0.89, "Norway2005 55%;Frucht 62%;TJU 65%;Nanjing 81%;AIIMS 87-89%"),
 "attr_two_plus": (0.45, 0.28, 0.61, "Norway2005 28%;Nanjing 60.8%"),
}
SURVEY_TRIGGERS = ["stress", "sleep", "miss", "ill", "catamenial", "binge", "photic"]   # triggers named in the surveys' checklists
def observables(o):
    sz = o["seiz_total"] > 0; szo = o["seiz_obs"] > 0
    ob = dict(sf12=float(o["sf12"].mean()), residual=float(o["residual"].mean()), eliminated=float(o["eliminated"].mean()),
              cluster_given_sz=float((o["cluster_days_obs"] > 0)[szo].mean()) if szo.any() else float("nan"))
    for k in ("stress", "sleep", "miss", "ill"): ob["attr_" + k] = float(o["attr_" + k][sz].mean()) if sz.any() else float("nan")
    w = sz & o["fem"]; ob["attr_catamenial_women"] = float(o["attr_catamenial"][w].mean()) if w.any() else float("nan")
    na = sum(o["attr_" + k].astype(int) for k in SURVEY_TRIGGERS)
    ob["attr_any"] = float((na[sz] >= 1).mean()) if sz.any() else float("nan"); ob["attr_two_plus"] = float((na[sz] >= 2).mean()) if sz.any() else float("nan")
    return ob
def score(ob, weights=None):
    s = 0.0; parts = {}
    for k, (pt, lo, hi, _) in TARGETS.items():
        v = ob.get(k, float("nan")); w = (weights or {}).get(k, 1.0)
        if not np.isfinite(v): d = 10.0
        else:
            bw = hi - lo; out = max(0.0, lo - v, v - hi) / bw; d = out ** 2 + 0.05 * ((v - pt) / bw) ** 2
        parts[k] = d * w; s += d * w
    return s, parts
def in_band(ob): return {k: bool(lo <= ob.get(k, np.nan) <= hi) for k, (pt, lo, hi, _) in TARGETS.items()}
