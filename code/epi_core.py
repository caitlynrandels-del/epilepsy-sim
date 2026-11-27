#!/usr/bin/env python3
"""
Oroboro relational epilepsy / seizure-dynamics testbed (speculative modeling / architecture testbed only; no clinical claims,
not medical advice). Adapted from Caitlyn Randels' v4 metastasis testbed (oroboro-multidb-sim-v4/code/oro_cascade.py).

Architecture (user's Oroboro components; see ../MAPPING.md):
  Genesis      -> origin identity of each virtual brain (its epileptogenic network), infinite weight; every focus mirrors back to it
  Nexus        -> registers the cohort, archives + telemeters daily whole-brain summaries, recombines the parts each day
                  (state reduction: a Part sees only its own circuits + YESTERDAY's Nexus peer summary of its brain)
  Parts        -> independent reduced states = groups of neural circuits / foci (circuit id mod K)
  Levy         -> event ledger, the user's standard weights: clear +1 (discharge suppressed locally / focus remits),
                  detach +7 (discharge escapes its focus), fail +2 (escaped discharge fails to recruit the network = aborted /
                  subclinical event), colonize +14 (network recruited = clinical seizure), exit +4 (quiescent focus reawakens)
  Salience gate + homeostasis -> whole-brain recruitment gate; post-ictal refractoriness (lagged) raises the gate after a seizure
  Transcriber/Dictator -> chronicle of critical events (seizures, reawakenings, sponge events) when record=True
  Mesh consensus -> two records (Levy event ledger, heat-trace intensity field) must agree for every focus
  Delta reconciliation -> whole-system run vs decomposed run (K parts) compared bit-for-bit, plus census and Levy checks
  Sponge       -> toggleable absorptive buffer between Parts and the whole (sponge.py); bookkeeping sponge = observer
Counter-based random numbers keyed by (seed, circuit/person id, day, stream): a focus's fate never depends on the partition.
Time step = 1 day. Default horizon 730 days; outcomes over the last 365 days.
"""
import numpy as np, json, os, math, copy
import layers as LY, rng as R
from scipy.special import ndtri
HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ["clear", "detach", "fail", "colonize", "exit"]
ACTIVE, QUIESCENT, CLEARED, HELD = 0, 1, 2, 3
TRIG = ["stress", "sleep", "miss", "alcohol", "binge", "ill", "weather", "sensory", "photic", "catamenial", "music"]
DRUGS = ["ssri", "stim", "nsaid", "psilo", "recdrug"]
ATTR = TRIG + DRUGS

class Genesis:
    root_tag = "I am the OG avatar"; weight = float("inf")
    def mirror(self, cohort, seed): return dict(origin=self.root_tag, cohort=cohort, seed=seed, weight=self.weight)
class Nexus:
    def __init__(self): self.registry = {}; self.archive = []; self.metrics = dict(recombinations=0, deltas=0)
    def register(self, k, v): self.registry[k] = v
    def telemeter(self, day, s): self.archive.append((day, s["seizures"], s["discharges"]))
class Levy:
    def __init__(self, W, n): self.W = W; self.c = {k: np.zeros(n, dtype=np.int64) for k in KINDS}
    def add(self, kind, idx, x): np.add.at(self.c[kind], idx, x)
    def total(self): return float(sum(self.W[k] * self.c[k].sum() for k in KINDS))
class Transcriber:
    def __init__(self): self.chronicle = []
    def write(self, day, kind, pid, ci): self.chronicle.append((int(day), kind, int(pid), int(ci)))

def load_params(path=None):
    return json.load(open(path or os.path.join(HERE, "params_base.json")))

NEUTRAL_INST = dict(off=[], amp={}, only=None, musicogenic_frac=None, m_music_generic=None, emotional_frac=None,
                    ssri=None, stim=None, nsaid=None, psilo=None, recdrug=None, cohort=None, no_asm=False)

def _cohort(P, inst, seed, pid):
    C = dict(P["cohort"]); C.update((inst.get("cohort") or {}))
    n = len(pid); g = pid * np.uint64(8) + np.uint64(7)
    u = lambda s: R.U(seed, g, 0, s)
    cp = np.cumsum(C["n_circ_probs"]); ncirc = 1 + np.searchsorted(cp, u(1) * cp[-1], side="right")
    ncirc = np.minimum(ncirc, len(cp))
    fem = u(2) < C["female_frac"]; cat = fem & (u(3) < C["catamenial_frac"])
    photo = u(4) < C["photosensitive_frac"]
    mf = inst.get("musicogenic_frac"); musico = u(5) < (C["musicogenic_frac"] if mf is None else mf)
    dep = u(6) < C["depression_frac"]
    resp = u(7) < C["resp_frac"]
    eff = np.where(resp, C["eff_resp"] + (1 - C["eff_resp"]) * u(8), C["eff_non_lo"] + (C["eff_non_hi"] - C["eff_non_lo"]) * u(8))
    if inst.get("no_asm"): eff = np.zeros(n)
    cyc = np.floor(u(9) * 28).astype(int)
    nsaid_s = u(10) < (inst.get("nsaid") or {}).get("susceptible_frac", 0.0)
    psilo_s = u(11) < (inst.get("psilo") or {}).get("susceptible_frac", 0.0)
    def grp(d, s):
        if not d: return np.zeros(n, bool)
        tgt = d.get("target", "all"); base = dep if tgt == "depressed" else np.ones(n, bool)
        return base & (u(s) < d.get("frac", 1.0))
    on = {k: grp(inst.get(k), 12 + i) for i, k in enumerate(DRUGS)}
    return dict(n=n, ncirc=ncirc, fem=fem, cat=cat, photo=photo, musico=musico, dep=dep, resp=resp, eff=eff, cyc=cyc,
                nsaid_s=nsaid_s, psilo_s=psilo_s, on=on)

def run(P, inst=None, seed=1, batch=0, n=2000, mode="whole", K=2, observers=None, record=False, record_n=5, return_daily=False):
    P = LY.normalize(P); I = dict(NEUTRAL_INST); I.update(inst or {})
    T = P["days"]; OBS = P["obs_days"]; D = P["dyn"]; E = dict(P["exposure"]); Mu = dict(P["mult"])
    if I["m_music_generic"] is not None: Mu["m_music_generic"] = I["m_music_generic"]
    if I["emotional_frac"] is not None: E["emotional_frac"] = I["emotional_frac"]
    pid = (np.uint64(batch) * np.uint64(1_000_000) + np.arange(n, dtype=np.uint64))
    Co = _cohort(P, I, seed, pid)
    # circuits (foci)
    maxc = int(Co["ncirc"].max()); cper = np.repeat(np.arange(n), Co["ncirc"]); cidx = np.concatenate([np.arange(k) for k in Co["ncirc"]])
    cg = pid[cper] * np.uint64(8) + cidx.astype(np.uint64); nc = len(cg)
    zc = ndtri(np.clip(R.U(seed, cg, 0, 30), 1e-12, 1 - 1e-12))
    base = P["cohort"]["base_rate"] * np.exp(P["cohort"]["lam_sigma"] * zc) * np.where(cidx == 0, 1.0, P["cohort"]["secondary_scale"])
    state = np.full(nc, ACTIVE, np.int8); kin = np.zeros(nc); hd = np.zeros(nc, np.int64)
    levy = Levy(P["levy_weights"], nc); heat_trace = np.zeros(nc); seiz_c = np.zeros(nc, np.int64)
    nparts = 1 if mode == "whole" else K
    part_of = ((cg >> np.uint64(3)) + cg) % np.uint64(nparts)
    parts = [np.nonzero(part_of == np.uint64(k))[0] for k in range(nparts)]
    nexus = Nexus(); gen = Genesis(); nexus.register("genesis", gen.mirror("epilepsy", seed)); trn = Transcriber() if record else None
    observers = observers or []
    # layers
    Lsh = LY.get(P, "shading"); NB = 4
    shade_c = np.zeros(nc); band_c = np.zeros(nc, np.int8); brain_shade = np.zeros(n); levy_band = np.zeros((n, NB))
    shade_daily = np.zeros((n, T), np.float32) if Lsh else None; band_daily = np.zeros((n, T), np.int8) if Lsh else None; shade_recon_bad = 0
    Wv = P["levy_weights"]
    Lk = LY.get(P, "kindling"); Ln = LY.get(P, "network"); Lh = LY.get(P, "hpa"); Li = LY.get(P, "inhibition"); Lheat = LY.get(P, "heat")
    sp = P.get("sponge") if (P.get("sponge") or {}).get("enabled") else None
    NCOMP = 2
    if sp:
        cap0 = float(sp["capacity"]) * LY.sponge_capacity_scale(P); cap = np.full((n, NCOMP), cap0); fill = np.zeros((n, NCOMP)); fill_prev2 = np.zeros((n, NCOMP))
        load_ema = np.zeros((n, NCOMP)); hard = cap0 * sp["hardcap_mult"]; sp_abs = np.zeros(NCOMP); sp_rel = np.zeros(NCOMP); sp_kill = np.zeros(NCOMP)
        hardcap_days = np.zeros(n, np.int64); fill_trace = []
        heatf = np.zeros((n, NCOMP)) if Lheat else None
    # lagged whole-brain (Nexus) summaries
    S_prev = np.zeros(n); D_prev = np.zeros(n); since = np.full(n, 999.0); H = np.zeros(n)
    stress_prev = np.zeros(n, bool); binge_prev = np.zeros(n, bool); ill_left = np.zeros(n, np.int64)
    expo_prev = {k: np.zeros(n, bool) for k in ATTR}
    attrib = {k: np.zeros(n, np.int32) for k in ATTR}     # seizure-days inside the exposure window (day of or day after exposure)
    expwin = {k: np.zeros(n, np.int32) for k in ATTR}     # all days inside the exposure window (background)
    daily = np.zeros((n, T), np.int16)
    gp = pid * np.uint64(8) + np.uint64(7)
    off = set(I["off"]); only = I["only"]; amp = I["amp"]
    def act(k): return (k not in off) and (only is None or k in only)
    def pe(k, p): return min(1.0, p * amp.get(k, 1.0)) if act(k) else 0.0
    ssri, stim, nsaid, psilo, recd = I["ssri"], I["stim"], I["nsaid"], I["psilo"], I["recdrug"]
    on = Co["on"]
    for t in range(1, T + 1):
        u = lambda s: R.U(seed, gp, t, s)
        # ---------------- person-level exposures (shared by all foci of a brain; partition-independent)
        x = {}
        ps = pe("stress", E["p_stress"]) * np.where(Co["dep"], E["dep_stress_mult"], 1.0)
        if ssri and ssri.get("stress_relief"): ps = ps * np.where(on["ssri"] & Co["dep"], 1.0 / E["dep_stress_mult"], 1.0)
        x["stress"] = u(1) < ps
        psl = np.full(n, pe("sleep", E["p_sleep"]))
        if Lh: psl = psl * np.where(stress_prev, Lh["sleep_given_stress_mult"], 1.0)
        if stim: psl = psl * np.where(on["stim"], stim.get("sleep_mult", 1.0), 1.0)
        x["sleep"] = u(2) < psl
        onset = u(6) < pe("ill", E["p_ill_onset"]); ill_left = np.where(onset, E["ill_days"], np.maximum(0, ill_left - 1)); x["ill"] = ill_left > 0
        x["binge"] = binge_prev.copy()   # heavy-drinking effect acts the NEXT day (Hamerle 2018: seizures after stopping)
        binge_today = u(5) < pe("binge", E["p_binge"])
        pm = np.full(n, pe("miss", E["p_miss"]))
        if Lh: pm = pm * np.where(x["ill"] | binge_prev, Lh["miss_given_ill_or_binge_mult"], 1.0)
        x["miss"] = u(3) < np.minimum(1.0, pm)
        x["alcohol"] = u(4) < pe("alcohol", E["p_alc_mod"])
        x["weather"] = u(7) < pe("weather", E["p_lowpressure"])
        x["sensory"] = u(8) < pe("sensory", E["p_sensory"])
        x["photic"] = u(9) < pe("photic", E["p_photic"])
        x["catamenial"] = Co["cat"] & (((t + Co["cyc"]) % 28) < E["phase_days"]) & act("catamenial")
        x["music"] = u(10) < pe("music", E["p_music"]); emo = x["music"] & (u(11) < E["emotional_frac"])
        # drugs (instances)
        x["ssri"] = on["ssri"].copy() if ssri else np.zeros(n, bool)
        x["stim"] = on["stim"].copy() if stim else np.zeros(n, bool)
        if nsaid:
            x["nsaid"] = on["nsaid"] & ((x["ill"] if nsaid.get("on_illness") else False) | (u(12) < nsaid.get("p_day", 0.0)))
        else: x["nsaid"] = np.zeros(n, bool)
        if psilo:
            sess = t in set(psilo["days"]); x["psilo"] = on["psilo"] & sess
            psilo_after = on["psilo"] & ((t - 1) in set(psilo["days"]))
        else: x["psilo"] = np.zeros(n, bool); psilo_after = np.zeros(n, bool)
        x["recdrug"] = (on["recdrug"] & (u(13) < recd.get("p_day", 0.0))) if recd else np.zeros(n, bool)
        # ---------------- multiplier on discharge rate (log-additive)
        M = np.ones(n)
        M *= np.where(x["stress"], Mu["m_stress"], 1.0); M *= np.where(x["sleep"], Mu["m_sleep"], 1.0)
        M *= np.where(x["alcohol"], Mu["m_alc_mod"], 1.0); M *= np.where(x["binge"], Mu["m_binge"], 1.0)
        mill = np.where(x["ill"], Mu["m_ill"], 1.0)
        if nsaid and nsaid.get("fever_relief"): mill = np.where(x["ill"] & x["nsaid"], 1 + (Mu["m_ill"] - 1) * (1 - nsaid["fever_relief"]), mill)
        M *= mill
        M *= np.where(x["weather"], Mu["m_weather"], 1.0); M *= np.where(x["sensory"], Mu["m_sensory"], 1.0)
        M *= np.where(x["photic"] & Co["photo"], Mu["m_photic"], 1.0); M *= np.where(x["catamenial"], Mu["m_cat"], 1.0)
        M *= np.where(x["music"], Mu["m_music_generic"], 1.0)
        M *= np.where(x["music"] & Co["musico"], np.where(emo, Mu["m_musico_emotional"], Mu["m_musico_neutral"]), 1.0)
        if ssri:
            early = t <= ssri.get("early_days", 0)
            M *= np.where(x["ssri"], ssri["early_mult"] if early else ssri["mult"], 1.0)
        if stim: M *= np.where(x["stim"], stim["mult"], 1.0)
        if nsaid: M *= np.where(x["nsaid"], np.where(Co["nsaid_s"], nsaid.get("mult_susceptible", 1.0), nsaid.get("mult", 1.0)), 1.0)
        if psilo:
            pm0 = np.where(Co["psilo_s"], psilo.get("mult_susceptible", psilo["mult"]), psilo["mult"])
            pm1 = np.where(Co["psilo_s"], psilo.get("mult_next_susceptible", psilo.get("mult_next", 1.0)), psilo.get("mult_next", 1.0))
            if ssri and psilo.get("ssri_interaction"): pm0 = np.where(x["ssri"], pm0 * psilo["ssri_interaction"], pm0)
            M *= np.where(x["psilo"], pm0, 1.0); M *= np.where(psilo_after, pm1, 1.0)
        if recd: M *= np.where(x["recdrug"], recd["mult"], 1.0)
        if Lh: M *= (1 + Lh["k"] * H)
        if Ln: M *= (1 + Ln["k"] * S_prev)
        eff_t = Co["eff"] * (1 - D["miss_drop"] * x["miss"])
        wake_mult = M * (1 + D["miss_wake_mult"] * x["miss"])
        # recruitment gate (salience) with lagged post-ictal refractoriness (homeostasis)
        rec_eff = D["rec_p"] * (1 - D["refractory"] * np.exp(-since / D["refr_tau"]))
        clr = D["clear_p"]
        if Li: clr = 1 - (1 - D["clear_p"]) / (1 + Li["boost"] / (1 + D_prev / Li["exhaustion_K"]))
        clr = np.broadcast_to(clr, (n,))
        if sp:
            gf = LY.sponge_gate_factor(P, D_prev / 10.0)
            av = LY.sponge_avail(P, fill, cap)
            if Lsh and Lsh["feedback"] > 0: av = av * np.clip(1 - Lsh["feedback"] * brain_shade, 0, 1)[:, None]
            perm = np.minimum(1.0, sp["permeability"] * LY.sponge_perm_factor(P, fill, cap, fill_prev2))
            gate0 = np.minimum(1.0, sp["circ_gate"] * gf * av[:, 0]); gate1 = np.minimum(1.0, sp["dorm_gate"] * gf * av[:, 1])
        part_shade = np.zeros(n)
        # ---------------- Parts: independent reduced states (each sees only its own foci + yesterday's Nexus summary)
        for idx in parts:
            if idx.size == 0: continue
            pc = cper[idx]; cgi = cg[idx]; st = state[idx]
            if Lsh: lv0 = sum(Wv[k] * levy.c[k][idx] for k in KINDS)
            uc = lambda s: R.U(seed, cgi, t, s)
            sf = np.where(st == ACTIVE, 1.0, np.where(st == QUIESCENT, D["q_rate"], 0.0))
            lam = base[idx] * M[pc] * (1 - eff_t[pc]) * sf
            if Lk: lam = lam * (1 + Lk["k"] * kin[idx])
            lam = np.minimum(lam, 30.0)
            nd = R.poisson_inv(uc(101), lam)
            cl = R.binom_inv(uc(102), nd, clr[pc]); esc = nd - cl
            levy.add("clear", idx, cl); levy.add("detach", idx, esc)
            if sp:
                h0 = hd[idx]
                rel = R.binom_inv(uc(104), h0, perm[pc, 0]); h1 = h0 - rel
                kl = R.binom_inv(uc(105), h1, sp["kill"]) if sp["kill"] > 0 else np.zeros_like(h1)
                h1 = h1 - kl; levy.add("clear", idx, kl)
                ab = R.binom_inv(uc(103), esc, gate0[pc]); esc = esc - ab; hd[idx] = h1 + ab
                np.add.at(sp_abs, 0, 7.0 * ab.sum()); np.add.at(sp_rel, 0, 7.0 * rel.sum()); np.add.at(sp_kill, 0, 7.0 * kl.sum())
                prop = esc + rel
            else: prop = esc
            sz = R.binom_inv(uc(106), prop, rec_eff[pc]); fl = prop - sz
            levy.add("fail", idx, fl); levy.add("colonize", idx, sz)
            # same-day cluster branching: each clinical seizure releases Poisson(b) further escaped discharges from its focus,
            # which meet the same recruitment gate (focus-local, so partition-independent); up to 6 generations
            gen_sz = sz
            for g in range(6):
                if D["cluster_b"] <= 0 or not gen_sz.any(): break
                ne = R.poisson_inv(uc(120 + 2 * g), D["cluster_b"] * gen_sz.astype(float))
                levy.add("detach", idx, ne)
                g_sz = R.binom_inv(uc(121 + 2 * g), ne, rec_eff[pc]); levy.add("fail", idx, ne - g_sz); levy.add("colonize", idx, g_sz)
                sz = sz + g_sz; gen_sz = g_sz
            seiz_c[idx] += sz; heat_trace[idx] += sz * 1.0
            np.add.at(daily[:, t - 1], pc, sz.astype(np.int16))
            if Lk: kin[idx] = kin[idx] * math.exp(-1.0 / Lk["tau"]) + sz
            # focus state transitions
            ua = uc(107); new = st.copy()
            new[(st == ACTIVE) & (ua < D["quiesce_p"] * Co["eff"][pc])] = QUIESCENT
            q = st == QUIESCENT; ur = uc(110)
            rem = q & (ur < D["remit_p"]); new[rem] = CLEARED; levy.add("clear", idx[rem], 1)
            wk = q & ~rem & (uc(108) < np.minimum(1.0, D["wake_p"] * wake_mult[pc]))
            levy.add("exit", idx[wk], 1)
            if sp:
                soak = wk & (uc(109) < gate1[pc]); new[soak] = HELD; new[wk & ~soak] = ACTIVE
                np.add.at(sp_abs, 1, 4.0 * soak.sum())
                hl = st == HELD; relh = hl & (uc(111) < perm[pc, 1]); new[relh] = QUIESCENT; np.add.at(sp_rel, 1, 4.0 * relh.sum())
                klh = hl & ~relh & (uc(112) < sp["kill"]); new[klh] = CLEARED; levy.add("clear", idx[klh], 1); np.add.at(sp_kill, 1, 4.0 * klh.sum())
                if record:
                    for j in np.nonzero(soak)[0][:3]:
                        if pc[j] < record_n: trn.write(t, "sponge_soak_reawakening", pc[j], cidx[idx[j]])
            else: new[wk] = ACTIVE
            state[idx] = new
            if Lsh:   # cell shading of this part's foci and of today's Levy-weighted transitions (focus-local -> partition-independent)
                tone = np.select([new == ACTIVE, new == QUIESCENT, new == HELD], [0.5, 0.25, 0.15], 0.0)
                en = nd + 3 * sz + (kin[idx] if Lk else 0.0)
                sh = np.minimum(1.0, tone + 0.5 * (1 - np.exp(-en / Lsh["energy_scale"])) * (new != CLEARED))
                bd = np.searchsorted(np.asarray(Lsh["bands"]), sh, side="right").astype(np.int8)
                shade_c[idx] = sh; band_c[idx] = bd
                dl = sum(Wv[k] * levy.c[k][idx] for k in KINDS) - lv0
                np.add.at(levy_band, (pc, bd.astype(int)), dl)
                np.add.at(part_shade, pc, sh)
            if record:
                for j in np.nonzero(sz)[0]:
                    if pc[j] < record_n: trn.write(t, f"seizure x{int(sz[j])}", pc[j], cidx[idx[j]])
                for j in np.nonzero(wk)[0]:
                    if pc[j] < record_n: trn.write(t, "reawakening_attempt", pc[j], cidx[idx[j]])
        # ---------------- Nexus recombination of the parts (whole-brain observables for tomorrow)
        St = daily[:, t - 1].astype(float)
        if Lsh:   # whole-brain shade = reconciled aggregate of the parts; checked against a direct whole-brain recomputation
            direct = np.zeros(n); np.add.at(direct, cper, shade_c)
            shade_recon_bad += int(not np.allclose(direct, part_shade, rtol=0, atol=1e-9))
            brain_shade = part_shade / Co["ncirc"]; shade_daily[:, t - 1] = brain_shade
            mb = np.zeros(n, np.int8); np.maximum.at(mb, cper, band_c); band_daily[:, t - 1] = mb
        Dt = np.zeros(n)
        nexus.metrics["recombinations"] += 1
        # discharges today per brain = clear+detach increments; recomputed from the ledger is expensive -> use lam proxy via ledger delta
        S_prev = St; since = np.where(St > 0, 0.0, since + 1.0)
        if Lh: H = H * Lh["decay"] + x["stress"]
        stress_prev = x["stress"]; binge_prev = binge_today
        sday = St > 0
        for k in ATTR:
            wnd = x[k] | expo_prev[k]; attrib[k] += sday & wnd; expwin[k] += wnd
            expo_prev[k] = x[k]
        if sp:
            f0 = np.zeros(n); np.add.at(f0, cper, 7.0 * hd); f1 = np.zeros(n); np.add.at(f1, cper, 4.0 * (state == HELD))
            fill_prev2 = fill; fill = np.stack([f0, f1], axis=1)
            load_ema = 0.8 * load_ema + 0.2 * np.minimum(1.0, fill / cap)
            tgt = np.minimum(hard, cap0 * (1 + sp["deform"] * load_ema * (sp["hardcap_mult"] - 1)))
            cap = np.maximum(cap0, cap + LY.sponge_relax(P) * (tgt - cap))
            hardcap_days += (fill >= hard - 1e-9).any(axis=1)
            if heatf is not None: heatf = heatf + Lheat["diffusion"] * (heatf.mean(axis=1, keepdims=True) - heatf) - Lheat["dissipation"] * heatf + fill / cap
            if return_daily or t % 30 == 0: fill_trace.append((t, (fill / cap).mean(axis=0).tolist(), (fill / cap).max(axis=0).tolist()))
        # discharges per brain for the inhibition layer / observers (ledger based, partition independent)
        cur = levy.c["clear"] + levy.c["detach"]
        if t == 1: prev_cd = np.zeros(nc, np.int64)
        dd = cur - prev_cd; prev_cd = cur.copy(); np.add.at(Dt, cper, dd)
        D_prev = Dt
        if observers:
            cen = [int((state == s).sum()) for s in (ACTIVE, QUIESCENT, CLEARED, HELD)]
            lt = levy.total(); li = lt - (prev_lt if t > 1 else 0.0); prev_lt = lt
            dom = np.zeros(n); np.add.at(dom, cper[cidx == 0], seiz_c[cidx == 0])
            s = dict(day=t, census=cen, part_census=sum(cen), nexus_census=nc, seizures=int(St.sum()), discharges=float(Dt.sum()), levy_inc=li,
                     heat_inc=float(brain_shade.sum()) if Lsh else float(St.sum()), load=float((state == ACTIVE).sum()) / max(1, nc) * 2.0,
                     seizures_offdominant=int(St.sum() - (dom - (prev_dom if t > 1 else 0)).sum()))
            prev_dom = dom.copy(); nexus.telemeter(t, s)
            for o in observers: o.step(s)
    # ---------------- end: reconciliation, checks, outputs
    out = {}
    last = daily[:, T - OBS:]; sl = last.sum(axis=1)
    def per(arr): z = np.zeros(n, np.int64); np.add.at(z, cper, arr); return z
    st_counts = {nm: per((state == s).astype(np.int64)) for nm, s in (("n_active", ACTIVE), ("n_quiescent", QUIESCENT), ("n_cleared", CLEARED), ("n_held", HELD))}
    out.update(st_counts); out["held_discharges"] = per(hd); out["ncirc"] = Co["ncirc"]
    out["seiz_total"] = daily.sum(axis=1); out["seiz_obs"] = sl; out["sz_days"] = (daily > 0).sum(axis=1)
    out["cluster_days_obs"] = (last >= 3).sum(axis=1); out["cluster_days"] = (daily >= 3).sum(axis=1); out["max_day"] = daily.max(axis=1)
    fd = np.where((daily > 0).any(axis=1), (daily > 0).argmax(axis=1) + 1, 0); out["first_day"] = fd
    # self-report attribution rules (ASSUMPTION, documented in PARAMETERS.md):
    #  naive  (R1): >=1 seizure-day fell in the exposure window (day of exposure or the day after)
    #  perceived (R2, used for calibration): R1 AND share of seizure-days in the window >= PERCEIVE x share of all days in the window
    sdays = (daily > 0).sum(axis=1).astype(float); PERC = P.get("perceive_ratio", 1.5)
    for k in ATTR:
        out["attrN_" + k] = attrib[k] > 0
        out["attr_" + k] = (attrib[k] > 0) & (attrib[k] / np.maximum(sdays, 1) >= PERC * expwin[k] / T)
    for nm in ("fem", "cat", "photo", "musico", "dep", "resp"): out[nm] = Co[nm]
    for k in DRUGS: out["on_" + k] = Co["on"][k]
    for k in KINDS: out["levy_" + k] = per(levy.c[k])
    W = P["levy_weights"]; out["levy"] = sum(W[k] * out["levy_" + k] for k in KINDS)
    nonclear = st_counts["n_active"] + st_counts["n_quiescent"] + st_counts["n_held"]
    out["sf12"] = sl == 0
    out["residual"] = (sl == 0) & ((nonclear > 0) | (out["held_discharges"] > 0))
    out["eliminated"] = (sl == 0) & (nonclear == 0) & (out["held_discharges"] == 0)
    out["sponge_held"] = st_counts["n_held"] + out["held_discharges"]
    # checks
    census_ok = int(sum(v.sum() for v in st_counts.values())) == nc
    levy_ok = abs(levy.total() - float(out["levy"].sum())) < 1e-6 * max(1.0, levy.total())
    consensus_ok = bool(np.array_equal(levy.c["colonize"], seiz_c) and np.allclose(heat_trace, seiz_c) and int(seiz_c.sum()) == int(daily.sum()))
    sponge_ok = True
    if sp:
        held_levy = np.array([7.0 * hd.sum(), 4.0 * (state == HELD).sum()])
        sponge_ok = bool(np.allclose(sp_abs, sp_rel + sp_kill + held_levy))
        out["sp_hardcap_days"] = hardcap_days; out["sp_cap_max_ratio"] = float((cap / cap0).max())
        out["_sp_trace"] = fill_trace; out["_sp_abs"] = sp_abs.tolist(); out["_sp_rel"] = sp_rel.tolist()
    if Lsh:
        so = shade_daily[:, T - OBS:]; bo = band_daily[:, T - OBS:]
        out["shade_mean_obs"] = so.mean(axis=1); out["shade_peak_obs"] = so.max(axis=1); out["shade_final"] = brain_shade.copy()
        for b in range(NB): out[f"band{b}_days_obs"] = (bo == b).sum(axis=1); out[f"levy_band{b}"] = levy_band[:, b]
        out["shade_recon_bad"] = shade_recon_bad
        if return_daily: out["_shade_daily"] = shade_daily; out["_band_daily"] = band_daily
    shade_ok = (shade_recon_bad == 0) and (not Lsh or abs(levy_band.sum() - levy.total()) < 1e-6 * max(1.0, levy.total()))
    agg = dict(census_ok=census_ok, levy_ok=levy_ok, consensus_ok=consensus_ok, sponge_ok=sponge_ok, shading_ok=shade_ok, levy_total=levy.total(),
               n_persons=n, n_circuits=nc, recombinations=nexus.metrics["recombinations"])
    out["_agg"] = agg
    out["_sig"] = (state.tobytes(), hd.tobytes(), daily.tobytes(), tuple(levy.c[k].tobytes() for k in KINDS))
    out["_sig_shade"] = (shade_daily.tobytes(), band_daily.tobytes(), levy_band.tobytes()) if Lsh else None
    if return_daily: out["_daily"] = daily
    if record: out["_chronicle"] = trn.chronicle
    res = dict(agg)
    for o in observers: o.finish(res)
    out["_observers"] = res
    return out

def reconcile(a, b):
    """delta reconciliation: whole-system run vs decomposed run must agree bit-for-bit on every focus and every day."""
    return dict(consistent=(a["_sig"] == b["_sig"]) and (a.get("_sig_shade") == b.get("_sig_shade")))
