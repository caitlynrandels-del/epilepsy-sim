#!/usr/bin/env python3
"""Charts for the epilepsy testbed (../charts/*.png). Speculative modeling only."""
import os, json, copy, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import epi_core as C, targets as TG, harness as H, run_all as RA
D = os.path.join(C.HERE, "..", "data"); CH = os.path.join(C.HERE, "..", "charts"); os.makedirs(CH, exist_ok=True)
S = pd.read_csv(os.path.join(D, "summary_conditions.csv")).set_index("name"); Ct = pd.read_csv(os.path.join(D, "contrasts.csv"))
def save(f): plt.tight_layout(); plt.savefig(os.path.join(CH, f), dpi=130); plt.close()
NOTE = "Speculative modeling only - not clinical evidence"
# 1 calibration fit
keys = list(TG.TARGETS); fig, ax = plt.subplots(figsize=(10, 5))
for i, k in enumerate(keys):
    pt, lo, hi, _ = TG.TARGETS[k]; ax.plot([i, i], [lo, hi], color="0.75", lw=10, solid_capstyle="butt")
for j, (nm, lab, mk) in enumerate((("baseline", "MAIN (all layers+sponge, anchored)", "o"), ("calset_FULL_free", "all layers, free multipliers", "s"),
                                   ("calset_CORE_anchored", "core only, anchored", "^"), ("calset_CORE_free", "core only, free", "v"))):
    v = [S.loc[nm, "p_sf12"] if k == "sf12" else S.loc[nm, k] for k in keys]; ax.scatter(np.arange(len(keys)) + (j - 1.5) * 0.12, v, marker=mk, label=lab, zorder=3)
ax.set_xticks(range(len(keys))); ax.set_xticklabels([k.replace("attr_", "reports ") for k in keys], rotation=30, ha="right"); ax.set_ylabel("proportion")
ax.set_title("Fit to public observables (grey = published range); validation seeds, 10,000 persons each"); ax.legend(fontsize=8); ax.text(0, -0.02, NOTE, transform=ax.transAxes, fontsize=7); save("01_calibration_fit.png")
# 2 triggers: OFF and x2 effect on seizures/yr + perceived vs causal
nat = ["stress", "sleep", "miss", "alcohol", "binge", "ill", "weather", "sensory", "photic", "catamenial", "music"]
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
for j, suf in enumerate(("_OFF", "_AMPx2")):
    r = Ct[(Ct.subset == "all") & Ct.condition.isin([k + suf for k in nat])].set_index("condition").reindex([k + suf for k in nat])
    y = np.arange(len(nat)) + (j - 0.5) * 0.35
    ax[0].errorbar(r.d_seiz_obs, y, xerr=[r.d_seiz_obs - r.d_seiz_obs_lo, r.d_seiz_obs_hi - r.d_seiz_obs], fmt="o", label="trigger removed" if j == 0 else "exposure doubled")
ax[0].axvline(0, color="k", lw=0.8); ax[0].set_yticks(range(len(nat))); ax[0].set_yticklabels(nat); ax[0].set_xlabel("change in seizures per person-year (paired, 95% CI)"); ax[0].legend()
b = S.loc["baseline", "seiz_per_yr"]
caus = [max(0.0, -Ct[(Ct.condition == k + "_OFF") & (Ct.subset == "all")].d_seiz_obs.iloc[0] / b) for k in nat]
perc = [S.loc["baseline", "attr_" + k] for k in nat]; naive = [S.loc["baseline", "attrN_" + k] for k in nat]
y = np.arange(len(nat)); ax[1].barh(y - 0.27, naive, 0.27, label="'reports' - naive co-occurrence rule"); ax[1].barh(y, perc, 0.27, label="'reports' - perceived-excess rule")
ax[1].barh(y + 0.27, caus, 0.27, label="causal share of seizures (removal run)"); ax[1].set_yticks(y); ax[1].set_yticklabels(nat); ax[1].legend(fontsize=7); ax[1].set_xlabel("proportion")
ax[1].set_title("Perceived trigger vs causal contribution"); save("02_triggers.png")
# 3 drugs
dr = Ct[Ct.condition.str.match(r"^(ssri|stim|nsaid|psilo|recdrug)") & Ct.subset.str.startswith("exposed")].copy()
fig, ax = plt.subplots(figsize=(9, max(4, 0.32 * len(dr)))); y = np.arange(len(dr))
ax.errorbar(dr.d_seiz_obs, y, xerr=[dr.d_seiz_obs - dr.d_seiz_obs_lo, dr.d_seiz_obs_hi - dr.d_seiz_obs], fmt="o"); ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels(dr.condition, fontsize=7); ax.set_xlabel("change in seizures per person-year among exposed (paired, 95% CI)")
ax.set_title("Drug 'instances' - alternative hypotheses (assumption-driven)"); save("03_drug_instances.png")
# 4 layers
lay = Ct[Ct.condition.str.startswith("layer_minus_")].copy(); lay["layer"] = lay.condition.str.replace("layer_minus_", "")
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5)); y = np.arange(len(lay))
ax[0].errorbar(-lay.d_sf12 * 100, y, xerr=[(lay.d_sf12_hi - lay.d_sf12) * 100, (lay.d_sf12 - lay.d_sf12_lo) * 100], fmt="o"); ax[0].axvline(0, color="k", lw=0.8)
ax[0].set_yticks(y); ax[0].set_yticklabels(lay.layer); ax[0].set_xlabel("layer's contribution to P(seizure-free 12 m), points\n(all-on minus all-on-without-layer)")
fs = [S.loc[c, "fit_score"] for c in lay.condition]; ax[1].barh(y, fs); ax[1].axvline(S.loc["baseline", "fit_score"], color="r", label="all on"); ax[1].set_yticks(y); ax[1].set_yticklabels("without " + lay.layer)
ax[1].set_xlabel("fit score (lower = better)"); ax[1].legend(); save("04_layers.png")
# 5 sponge sweep
sw = [n for n in S.index if n.startswith("sponge_")] + ["baseline", "baseline_spongeOFF"]
fig, ax = plt.subplots(figsize=(9, 4.5)); v = S.loc[sw]
ax.barh(range(len(sw)), v.p_sf12, xerr=[v.p_sf12 - v.p_sf12_lo, v.p_sf12_hi - v.p_sf12], color=["C0"] * (len(sw) - 2) + ["C2", "C3"])
ax.set_yticks(range(len(sw))); ax.set_yticklabels(sw, fontsize=8); ax.set_xlim(0.5, 0.85); ax.set_xlabel("P(seizure-free last 12 months)"); ax.set_title("Sponge parameters (all assumptions)"); save("05_sponge.png")
# 6 nohist
p = os.path.join(D, "nohist_psilocybin.csv")
if os.path.exists(p):
    R = pd.read_csv(p); fig, ax = plt.subplots(figsize=(8, 4)); y = np.arange(len(R))
    ax.errorbar(R.p_seizure_yr_per100k, y, xerr=[R.p_seizure_yr_per100k - R.lo, R.hi - R.p_seizure_yr_per100k], fmt="o"); ax.set_yticks(y); ax.set_yticklabels(R.name, fontsize=8)
    ax.set_xlabel("people with >=1 seizure in a year, per 100,000"); ax.set_title("No seizure history: psilocybin hypotheses (assumption-driven)"); save("06_psilocybin_no_history.png")
# 7 cell shading raster + bands
P = H.load_set("FULL_anchored"); P["layers"]["shading"] = True
o = C.run(P, seed=H.EVAL_SEED, batch=0, n=2000, return_daily=True)
order = np.argsort(-o["seiz_obs"])[:40].tolist() + np.nonzero(o["sf12"])[0][:40].tolist()
cmap = ListedColormap(["#1b1b3a", "#3c5a99", "#e8a33d", "#ff3b3b"]); norm = BoundaryNorm([0, 1, 2, 3, 4], 4)
fig, ax = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw=dict(height_ratios=[3, 1]))
ax[0].imshow(o["_band_daily"][order], aspect="auto", cmap=cmap, norm=norm, interpolation="nearest")
ax[0].set_ylabel("virtual brains (top 40 seizing, 40 seizure-free)"); ax[0].set_title("Cell shading (provisional): daily whole-brain cel band - dark: cleared/held, blue: quiescent, amber: active, red: ictal")
sd = o["_shade_daily"]; ax[1].plot(sd[o["sf12"]].mean(axis=0), label="seizure-free group"); ax[1].plot(sd[~o["sf12"]].mean(axis=0), label="still seizing"); ax[1].set_xlabel("day"); ax[1].set_ylabel("mean shade"); ax[1].legend()
save("07_cell_shading_raster.png")
# 8 shade around seizures + Levy by band
dl = o["_daily"]; win = np.arange(-10, 11); acc = []
for i, t in zip(*np.nonzero(dl[:, 20:-20] > 0)):
    acc.append(sd[i, t + 20 + win])
acc = np.array(acc)
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
ax[0].plot(win, acc.mean(axis=0)); ax[0].axvline(0, color="r", lw=0.8); ax[0].set_xlabel("days from a seizure"); ax[0].set_ylabel("whole-brain shade"); ax[0].set_title("Shade around seizure days")
lb = [S.loc["baseline", f"levy_band{b}_share"] for b in range(4)]; bd = [S.loc["baseline", f"band{b}_share"] for b in range(4)]
ax[1].bar(np.arange(4) - 0.2, bd, 0.4, label="share of brain-days"); ax[1].bar(np.arange(4) + 0.2, lb, 0.4, label="share of Levy weight"); ax[1].set_xticks(range(4)); ax[1].set_xticklabels(["dark", "quiescent", "active", "ictal"]); ax[1].legend(fontsize=8)
ax[1].set_title("Cel bands: time vs Levy-weighted events")
fbn = ["baseline", "shading_feedback_0.25", "shading_feedback_0.5", "shading_feedback_1.0", "baseline_spongeOFF", "shading_feedback_0.5_spongeOFF"]
fbn = [x for x in fbn if x in S.index]; v = S.loc[fbn]
ax[2].barh(range(len(fbn)), v.p_sf12, xerr=[v.p_sf12 - v.p_sf12_lo, v.p_sf12_hi - v.p_sf12]); ax[2].set_yticks(range(len(fbn))); ax[2].set_yticklabels(fbn, fontsize=7); ax[2].set_xlim(0.5, 0.8)
ax[2].set_xlabel("P(seizure-free 12 m)"); ax[2].set_title("Shading observational vs coupled"); save("08_cell_shading_events_feedback.png")
json.dump(dict(event_triggered_shade=acc.mean(axis=0).tolist(), window=win.tolist(), n_events=len(acc)), open(os.path.join(D, "cell_shading_event_triggered.json"), "w"))
# 9 synergy
sy = pd.read_csv(os.path.join(D, "synergy.csv")); sy = sy[sy.key == "seiz_obs"]
fig, ax = plt.subplots(figsize=(8, 3.5)); y = np.arange(len(sy))
ax.errorbar(sy.interaction, y, xerr=[sy.interaction - sy.lo, sy.hi - sy.interaction], fmt="o"); ax.axvline(0, color="k", lw=0.8); ax.set_yticks(y); ax.set_yticklabels(sy.combo, fontsize=8)
ax.set_xlabel("interaction (seizures/person-yr): combo - A - B + baseline"); ax.set_title("Trigger cascades: more (>0) or less (<0) than additive"); save("09_synergy.png")
print("charts written", sorted(os.listdir(CH)))
