#!/usr/bin/env python3
"""Update-handling routine (copied from the v4 metastasis testbed, key lists adapted to the epilepsy parameters) applied to every parameter update / parameter-file write (see UPDATE_SEQUENCE.md).

Sequence (user's names -> operation):
  1. quick fix      : apply the proposed change to a STAGED copy (never the live file).
  2. UPDATE ALL     : propagate the staged change to every dependent file (e.g. params_calibrated.json mirrors params_multidb_main.json).
  3. undo           : revert the staging area to the pre-update snapshot and verify the restore is exact (SHA-256 equal to the snapshot).
  4. Timestamp      : log the change (PT timestamp, before/after hashes, changed keys) to data/update_sequence_log.jsonl.
  5. do it again    : re-apply the same change from the snapshot and verify the result is byte-identical to the first application
                      (idempotence / determinism check).
  6. syntax -> autocorrect : validate schema/types/ranges; auto-correct ONLY clearly invalid formatting (numeric strings -> numbers,
                      probabilities outside [0,1] clamped, non-finite values rejected), logging every correction. Values that are
                      valid are never changed. Then the verified result is committed atomically.
The routine validates and logs; it does not alter dynamics. A model run reads only the committed file.
"""
import os, json, copy, hashlib, math, tempfile, datetime
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(HERE, "..", "data", "update_sequence_log.jsonl")
# keys whose values are probabilities (per-month or per-event) and must lie in [0, 1]
PROB_KEYS = {"clear_p", "rec_p", "quiesce_p", "wake_p", "remit_p", "female_frac", "catamenial_frac", "photosensitive_frac", "musicogenic_frac",
             "depression_frac", "p_stress", "p_sleep", "p_miss", "p_alcohol_moderate", "p_binge", "p_ill_onset", "p_lowpressure", "p_sensory",
             "p_photic", "p_music", "emotional_frac", "asm_eff_mean", "nsaid_susceptible_frac", "psilo_susceptible_frac", "refractory", "pr_sleep_given_stress",
             "circ_clear_p", "arrest_p", "dorm_clear_p", "col_accept", "seed_threshold", "valuation_threshold", "circ_gate", "dorm_gate",
             "permeability", "kill", "deform", "initial_depth", "restore_rate", "exit_factor", "fail_gain", "high_cutoff", "tension_hi",
             "col_threshold_pref", "col_threshold_other", "immune_evasion_lo", "immune_evasion_span", "hysteresis", "protection", "restore_bonus"}
PERM_PARENT = "organ_permissiveness"
POSITIVE_KEYS = {"base_rate", "days", "obs_days", "kindle_tau", "hpa_decay", "m_stress", "m_sleep", "m_miss", "m_ill", "m_binge", "m_photic", "shed_rate", "exit_p", "frailty_k", "capacity", "hardcap_mult", "months", "rest_load"}

def canon(obj): return json.dumps(obj, indent=1, sort_keys=False, default=float).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def now_pt(): return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")

def _diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            out += _diff(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{path}.{k}" if path else str(k))
    elif a != b: out.append(path)
    return out

def autocorrect(obj, path="", parent=""):
    """Return (corrected_obj, corrections, errors). Only clearly invalid formatting is corrected."""
    corr, err = [], []
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            nv, c, e = autocorrect(v, f"{path}.{k}" if path else str(k), str(k)); new[k] = nv; corr += c; err += e
        return new, corr, err
    if isinstance(obj, list):
        new = []
        for i, v in enumerate(obj):
            nv, c, e = autocorrect(v, f"{path}[{i}]", parent); new.append(nv); corr += c; err += e
        return new, corr, err
    v = obj
    if isinstance(v, str):
        try:
            f = float(v)
            if parent in PROB_KEYS or parent in POSITIVE_KEYS or path.split(".")[-2:-1] == [PERM_PARENT]:
                corr.append(dict(path=path, before=v, after=f, rule="numeric string -> number")); v = f
        except ValueError: return v, corr, err
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v is None: return v, corr, err
    if not math.isfinite(v): err.append(dict(path=path, value=str(v), rule="non-finite value rejected")); return v, corr, err
    is_prob = parent in PROB_KEYS or (PERM_PARENT in path.split("."))
    if is_prob and not (0.0 <= v <= 1.0):
        nv = min(1.0, max(0.0, v)); corr.append(dict(path=path, before=v, after=nv, rule="probability clamped to [0,1]")); v = nv
    if parent in POSITIVE_KEYS and v < 0: err.append(dict(path=path, value=v, rule="negative value for a positive-only parameter (not auto-corrected)"))
    return v, corr, err

def _write_atomic(path, data):
    d = os.path.dirname(os.path.abspath(path)); os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".staged_"); os.write(fd, data); os.close(fd); os.replace(tmp, path)

def apply_update(target, proposal, dependents=(), context="", commit=True, log_path=LOG):
    """target: path of the parameter file. proposal: dict (the new parameter set) or callable(old_dict)->new_dict.
    dependents: list of (path, fn(new_dict)->dict) propagated by UPDATE ALL. Returns the log record."""
    rec = dict(timestamp_pt=None, context=context, target=os.path.relpath(target, os.path.join(HERE, "..")), steps={})
    # snapshot
    snap_bytes = open(target, "rb").read() if os.path.exists(target) else None
    old = json.loads(snap_bytes) if snap_bytes else {}
    dep_snap = {p: (open(p, "rb").read() if os.path.exists(p) else None) for p, _ in dependents}
    rec["hash_before"] = sha(snap_bytes) if snap_bytes else None
    make = (lambda o: proposal(copy.deepcopy(o))) if callable(proposal) else (lambda o: copy.deepcopy(proposal))
    # 1 quick fix: staged copy
    staged = make(old); b1 = canon(staged); rec["steps"]["quick_fix"] = dict(staged_hash=sha(b1), changed_keys=_diff(old, staged)[:200])
    # 2 UPDATE ALL: propagate to dependents (staged)
    dep_staged = {p: canon(fn(copy.deepcopy(staged))) for p, fn in dependents}
    rec["steps"]["update_all"] = dict(dependents={os.path.relpath(p, os.path.join(HERE, "..")): sha(b) for p, b in dep_staged.items()})
    # 3 undo: revert staging to the snapshot; verify exact restore
    # staged copies are discarded; the restore source is the live file, which must still equal the snapshot byte for byte
    live = open(target, "rb").read() if os.path.exists(target) else None
    restored = live if live is not None else b""
    rec["steps"]["undo"] = dict(restore_exact=(live == snap_bytes) and ((sha(restored) == rec["hash_before"]) if snap_bytes else True),
                                dependents_restore_exact=all(((open(p, "rb").read() if os.path.exists(p) else None) == dep_snap[p]) for p in dep_snap))
    rec["steps"]["undo"]["restore_exact"] = rec["steps"]["undo"]["restore_exact"] and rec["steps"]["undo"]["dependents_restore_exact"]
    # 4 Timestamp
    rec["timestamp_pt"] = now_pt()
    # 5 do it again: re-apply from snapshot and compare
    again = canon(make(json.loads(restored) if restored else {}))
    dep_again = {p: canon(fn(json.loads(again))) for p, fn in dependents}
    rec["steps"]["do_it_again"] = dict(identical=(again == b1) and all(dep_again[p] == dep_staged[p] for p in dep_staged))
    # 6 syntax -> autocorrect
    fixed, corr, errs = autocorrect(json.loads(again))
    rec["steps"]["autocorrect"] = dict(n_corrections=len(corr), corrections=corr, n_errors=len(errs), errors=errs)
    final = canon(fixed); rec["hash_after"] = sha(final)
    rec["values_changed_by_routine"] = bool(corr)
    ok = rec["steps"]["undo"]["restore_exact"] and rec["steps"]["do_it_again"]["identical"] and not errs
    rec["verified"] = bool(ok); rec["committed"] = False
    if commit and ok:
        if final != (snap_bytes or b""): _write_atomic(target, final)
        for p, fn in dependents:
            b = canon(fn(json.loads(final)))
            if b != (dep_snap[p] or b""): _write_atomic(p, b)
        rec["committed"] = True
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f: f.write(json.dumps(rec, default=float) + "\n")
    return rec

def verify_existing(path, context="retroactive verification"):
    """Retroactive pass on a finished file: proposal = the file's own content, no commit. Reports whether the routine would change anything."""
    content = json.load(open(path))
    return apply_update(path, content, context=context, commit=False)

if __name__ == "__main__":
    import glob, sys
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "..", "data", "calibration", "params_*.json")))
    for f in files:
        r = verify_existing(f)
        print(os.path.basename(f), "verified" if r["verified"] else "NOT VERIFIED", "corrections", r["steps"]["autocorrect"]["n_corrections"],
              "errors", r["steps"]["autocorrect"]["n_errors"], "byte-identical-after-canon", r["hash_after"] == r["hash_before"])

# ---------------------------------------------------------------------------------------------------------------------------
# In-memory variant for ITERATE-LEVEL updates inside calibration loops (v4: closes the v3 gap).
# The "redstone torch": calling torch() fires the validate/autocorrect pass (step 6) on a parameter dict - it is the trigger
# signal that (re)powers the circuit; it adds no semantics beyond running syntax->autocorrect and logging.
def torch(obj, context="", log_path=None):
    fixed, corr, errs = autocorrect(obj)
    if log_path is not False:
        with open(log_path or LOG, "a") as f:
            f.write(json.dumps(dict(timestamp_pt=now_pt(), context=context, kind="torch", n_corrections=len(corr), corrections=corr, n_errors=len(errs), errors=errs), default=float) + "\n")
    return fixed, corr, errs

def apply_obj(old, fn, context="", mirror_path=None, log_path=None):
    """old: current parameter dict (never mutated). fn(copy)->new dict (deterministic). mirror_path: dependent file (iterate checkpoint)
    written by UPDATE ALL after verification. Returns the verified, autocorrected new dict. Raises RuntimeError if verification fails."""
    rec = dict(timestamp_pt=None, context=context, kind="iterate", steps={})
    snap = canon(old); rec["hash_before"] = sha(snap)
    staged = fn(copy.deepcopy(old)); b1 = canon(staged)                                         # 1 quick fix (staged copy)
    rec["steps"]["quick_fix"] = dict(staged_hash=sha(b1), changed_keys=_diff(old, staged)[:200])
    rec["steps"]["update_all"] = dict(dependent=os.path.relpath(mirror_path, os.path.join(HERE, "..")) if mirror_path else None)   # 2 (staged)
    rec["steps"]["undo"] = dict(restore_exact=(canon(old) == snap))                             # 3 undo: live object untouched == snapshot
    rec["timestamp_pt"] = now_pt()                                                              # 4 Timestamp
    again = canon(fn(json.loads(snap)))                                                         # 5 do it again (from restored snapshot)
    rec["steps"]["do_it_again"] = dict(identical=(again == b1))
    fixed, corr, errs = autocorrect(json.loads(b1))                                             # 6 torch -> syntax -> autocorrect
    rec["steps"]["autocorrect"] = dict(trigger="redstone torch", n_corrections=len(corr), corrections=corr, n_errors=len(errs), errors=errs)
    rec["hash_after"] = sha(canon(fixed)); rec["values_changed_by_routine"] = bool(corr)
    rec["verified"] = bool(rec["steps"]["undo"]["restore_exact"] and rec["steps"]["do_it_again"]["identical"] and not errs)
    if rec["verified"] and mirror_path: _write_atomic(mirror_path, canon(fixed))               # 2 UPDATE ALL committed
    with open(log_path or LOG, "a") as f: f.write(json.dumps(rec, default=float) + "\n")
    if not rec["verified"]: raise RuntimeError(f"update sequence verification failed: {context}")
    return fixed
