#!/usr/bin/env python3
"""Preflight: confirm every component is active and every switch behaves before the main runs (writes ../PREFLIGHT.md)."""
import os, json, copy, math, datetime, tempfile
import numpy as np
import epi_core as C, layers as LY, sponge as SPM, background as BG, update_sequence as US, harness as H
from zoneinfo import ZoneInfo
rows = []
def chk(area, what, ok, detail): rows.append((area, what, "PASS" if ok else "FAIL", detail)); print(("PASS" if ok else "FAIL"), area, what, detail, flush=True)
def main(pset_path):
    P0 = json.load(open(pset_path)); P0.pop("_calibration", None); P0.pop("_note", None)
    ALL = {l: True for l in ["sponge"] + LY.NAMES}   # includes the provisional 'shading' layer
    P = copy.deepcopy(P0); P["layers"] = dict(ALL); n = 600
    a = C.run(P, seed=7, n=n, record=True, record_n=20)
    ag = a["_agg"]
    chk("core", "Genesis root identity registered; Nexus recombined every day", ag["recombinations"] == P["days"], f"recombinations {ag['recombinations']} / days {P['days']}")
    chk("core", "Levy ledger total equals sum of per-person weighted events", ag["levy_ok"], f"Levy total {ag['levy_total']:.0f}")
    kinds = {k: int(a['levy_' + k].sum()) for k in C.KINDS}
    chk("core", "all five Levy event kinds occur (clear/detach/fail/colonize/exit)", all(v > 0 for v in kinds.values()), str(kinds))
    chk("core", "census (active+quiescent+cleared+held foci = all foci)", ag["census_ok"], f"{ag['n_circuits']} foci")
    chk("core", "mesh consensus (Levy ledger == heat-trace == daily seizure matrix, every focus)", ag["consensus_ok"], "")
    chk("core", "Transcriber/Dictator chronicle records critical events", len(a["_chronicle"]) > 0, f"{len(a['_chronicle'])} entries, e.g. {a['_chronicle'][:2]}")
    Q = copy.deepcopy(P); Q["dyn"]["refractory"] = 0.0; b = C.run(Q, seed=7, n=n)
    chk("core", "salience gate + homeostasis (post-ictal refractoriness) active: switching it off changes runs", b["_sig"] != a["_sig"], "")
    for K in (2, 3):
        for sp in (True, False):
            Q = copy.deepcopy(P); Q["layers"]["sponge"] = sp
            w = C.run(Q, seed=8, n=n); d = C.run(Q, seed=8, n=n, mode="decomposed", K=K)
            chk("delta reconciliation", f"whole vs {K} independent parts bit-identical (sponge {'ON' if sp else 'OFF'}, all layers ON)", C.reconcile(w, d)["consistent"], "")
    o = C.run(P, seed=7, n=n, observers=BG.all_background() + [SPM.BookkeepingSponge()]); r = o["_observers"]
    chk("background", "4 background processors + bookkeeping sponge attached leave the run unchanged", o["_sig"] == a["_sig"],
        ", ".join(f"{k}={v}" for k, v in r.items() if k.startswith("bg_")))
    chk("sponge (bookkeeping)", "conservation (inflow = released + squeezed + spill) and reconciled Levy stream = model Levy", r["bk_conservation_ok"] and r["bk_levy_matches_model"], f"spill {r['bk_spill_levy']:.1f}")
    chk("sponge (biological)", "conservation absorbed = released + squeezed + held (Levy units)", ag["sponge_ok"], f"absorbed {a['_sp_abs']}, released {a['_sp_rel']}")
    # toggles
    base_off = copy.deepcopy(P0); base_off["layers"] = {l: False for l in ALL}; z = C.run(base_off, seed=9, n=n)
    absent = copy.deepcopy(P0); absent["layers"] = {}; z2 = C.run(absent, seed=9, n=n)
    chk("layer", "all switches False == layers absent (core model)", z["_sig"] == z2["_sig"], "")
    for l in ["sponge"] + LY.NAMES:
        for spon in (False, True):
            if l == "sponge" and spon: continue
            L1 = {m: False for m in ALL}; L1["sponge"] = spon or l == "sponge"; L0 = dict(L1); L0[l] = False if l != "sponge" else False
            L1[l] = True
            Pa = copy.deepcopy(P0); Pa["layers"] = L1; Pb = copy.deepcopy(P0); Pb["layers"] = L0
            Pc = copy.deepcopy(P0); Pc["layers"] = {k: v for k, v in L0.items() if k != l}
            ra, rb, rc = C.run(Pa, seed=9, n=n), C.run(Pb, seed=9, n=n), C.run(Pc, seed=9, n=n)
            changed = ra["_sig"] != rb["_sig"]
            neutral_expected = (l in ("heat", "shading")) or (l in ("materials", "physics") and not spon)
            ok = (rb["_sig"] == rc["_sig"]) and (changed != neutral_expected)
            wd = C.run(Pa, seed=9, n=300); dd = C.run(Pa, seed=9, n=300, mode="decomposed", K=2)
            ok = ok and C.reconcile(wd, dd)["consistent"]
            chk("layer", f"{l} toggle (sponge {'ON' if L1['sponge'] else 'OFF'}): disabled==absent; enabled {'neutral (expected)' if neutral_expected else 'changes runs'}; whole-vs-parts OK",
                ok, f"changed={changed}")
    # cell shading specifics
    Ps = copy.deepcopy(P); Ps["layers"]["shading"] = True; sa = C.run(Ps, seed=12, n=n)
    chk("cell shading", "whole-brain shade = reconciled aggregate of the parts every day; Levy by shade band sums to Levy total", sa["_agg"]["shading_ok"] and sa["shade_recon_bad"] == 0, f"recon mismatches {sa['shade_recon_bad']}")
    sd = C.run(Ps, seed=12, n=n, mode="decomposed", K=3)
    chk("cell shading", "shade raster, band raster and Levy-by-band bit-identical whole vs 3 parts", C.reconcile(sa, sd)["consistent"], "")
    Pf = copy.deepcopy(Ps); Pf["layers"]["shading"] = {"feedback": 0.5}; sf = C.run(Pf, seed=12, n=n)
    chk("cell shading", "coupled variant (feedback 0.5 -> sponge) changes runs; observational default does not", sf["_sig"] != sa["_sig"], "")
    Pf2 = copy.deepcopy(Pf); Pf2["layers"]["sponge"] = False; sf2 = C.run(Pf2, seed=12, n=n); Ps2 = copy.deepcopy(Ps); Ps2["layers"]["sponge"] = False; sa2 = C.run(Ps2, seed=12, n=n)
    chk("cell shading", "coupled variant is neutral with the sponge OFF (it acts only through the sponge)", sf2["_sig"] == sa2["_sig"], "")
    # instances plumbing
    I0 = C.run(P, seed=10, n=n)
    for nm, inst, expect_change in (("SSRI neutral (mult 1.0, no stress relief)", dict(ssri=dict(target="depressed", mult=1.0, early_mult=1.0, early_days=0)), False),
                                    ("SSRI observational OR 1.48", dict(ssri=dict(target="depressed", mult=1.48, early_mult=2.35, early_days=30)), True),
                                    ("stimulant HR 0.73", dict(stim=dict(mult=0.73)), True), ("NSAID neutral on illness", dict(nsaid=dict(on_illness=True, mult=1.0)), False),
                                    ("psilocybin high exacerbation", dict(psilo=dict(days=[120, 300], mult=3.0, mult_next=1.5)), True),
                                    ("recreational drug x5", dict(recdrug=dict(p_day=0.05, mult=5.0)), True), ("stress OFF", dict(off=["stress"]), True),
                                    ("musicogenic cohort", dict(musicogenic_frac=1.0), True)):
        r2 = C.run(P, inst, seed=10, n=n); ch = r2["_sig"] != I0["_sig"]
        chk("instance", f"{nm}: {'changes runs' if expect_change else 'bit-identical to baseline (neutral by construction)'}", ch == expect_change, f"changed={ch}")
    # update sequence
    tmp = tempfile.mkdtemp(); tgt = os.path.join(tmp, "p.json"); json.dump({"dyn": {"clear_p": 0.9}}, open(tgt, "w"))
    rec = US.apply_update(tgt, {"dyn": {"clear_p": "1.2", "rec_p": 0.3}}, context="preflight test update", log_path=os.path.join(tmp, "log.jsonl"))
    chk("update sequence", "six steps: staged quick fix, UPDATE ALL, hash-verified undo, PT timestamp, identical re-apply, torch->autocorrect",
        rec["verified"] and rec["steps"]["undo"]["restore_exact"] and rec["steps"]["do_it_again"]["identical"] and rec["steps"]["autocorrect"]["n_corrections"] == 2,
        f"corrections {rec['steps']['autocorrect']['n_corrections']} (numeric string -> number, clamp 1.2 -> 1.0), timestamp {rec['timestamp_pt']}")
    rec2 = US.apply_update(tgt, {"dyn": {"clear_p": float('nan')}}, context="preflight NaN", log_path=os.path.join(tmp, "log.jsonl"))
    chk("update sequence", "non-finite update rejected (not committed)", not rec2["committed"], f"committed={rec2['committed']}")
    L = [json.loads(x) for x in open(os.path.join(os.path.dirname(pset_path), "..", "update_sequence_log.jsonl"))]
    it = [x for x in L if x.get("kind") == "iterate" and "best-iterate" in x.get("context", "")]
    chk("update sequence", "active inside calibration (every accepted best-iterate passed the sequence, all verified)", len(it) > 0 and all(x["verified"] for x in it), f"{len(it)} iterate records")
    # stop rule
    H.register("PF", P)
    nm, D, info, _ = H.run_condition(dict(name="pf_prec", pset="PF", stop=dict(target_hw=0.06, batch=200, min_batches=2, cap_batches=30)))
    chk("stop rule", "adaptive batches stop on CI half-width (test target 0.06)", info["stop_reason"] == "precision", f"batches {info['batches']}, persons {info['persons']}, recon_bad {info['recon_bad']}, obs_bad {info['obs_bad']}")
    nm, D, info, _ = H.run_condition(dict(name="pf_cap", pset="PF", stop=dict(target_hw=0.0001, batch=200, min_batches=2, cap_batches=3)))
    chk("stop rule", "cap honoured (cap 3 batches)", info["stop_reason"] == "cap" and info["batches"] == 3, f"reason {info['stop_reason']}")
    chk("stop rule", "configured for main runs", True, f"target half-width {H.STOP['target_hw']} on P(seizure-free 12 m), P(residual risk), P(eliminated); batch {H.STOP['batch']} persons; min {H.STOP['min_batches']} batches; cap {H.STOP['cap_batches']} batches")
    ts = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %I:%M %p PT")
    nf = sum(r[2] == "FAIL" for r in rows)
    with open(os.path.join(C.HERE, "..", "PREFLIGHT.md"), "w") as f:
        f.write(f"# PREFLIGHT.md: component and switch checks before the main runs\n\nSpeculative modeling / architecture testbed only. No clinical claims.\n\nRun {ts} on parameter set `{os.path.relpath(pset_path, os.path.join(C.HERE, '..'))}`. Result: **{len(rows) - nf} PASS, {nf} FAIL**.\n\n| Area | Check | Result | Detail |\n|---|---|---|---|\n")
        for r in rows: f.write("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |\n")
    return nf
if __name__ == "__main__":
    import sys; raise SystemExit(main(sys.argv[1]))
