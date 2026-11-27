"""Condition list for the epilepsy run. MAIN = FULL_anchored calibrated set (all layers + sponge on). Every value not drawn from a
cited source is marked as an assumption in ../PARAMETERS.md (section 'Instances')."""
import copy
NAT = ["stress", "sleep", "miss", "alcohol", "binge", "ill", "weather", "sensory", "photic", "catamenial", "music"]
LAYERS = ["sponge", "materials", "physics", "heat", "inhibition", "hpa", "kindling", "network", "shading"]
PSILO_DAYS = [120, 300, 480, 660]   # assumption: 4 sessions over 2 years
NOHIST = dict(n_circ_probs=[1.0], resp_frac=0.0, base_rate=None)   # base_rate filled in run_all from calibration (no-history cohort)
def conds(main="MAIN"):
    C = []
    add = lambda name, group, **kw: C.append(dict(name=name, group=group, pset=kw.pop("pset", main), **kw))
    add("baseline", "baseline")
    add("baseline_spongeOFF", "baseline", layers={**{l: True for l in LAYERS}, "sponge": False})
    add("baseline_allOFF_core", "baseline", layers={l: False for l in LAYERS})
    for s in ("FULL_free", "CORE_anchored", "CORE_free"): add(f"calset_{s}", "calibration_validation", pset=s)
    add("calset_FULL_anchored", "calibration_validation")
    # natural triggers
    add("triggers_NONE", "trigger", inst=dict(off=list(NAT)))
    for k in NAT:
        add(f"{k}_OFF", "trigger", inst=dict(off=[k]))
        if k != "catamenial": add(f"{k}_AMPx2", "trigger", inst=dict(amp={k: 2.0}))
        add(f"{k}_ONLY", "trigger_only", inst=dict(only=[k]))
    # music
    add("music_generic_protective_K448", "music", inst=dict(m_music_generic=0.9))
    add("musicogenic_userupper_1pct", "music", inst=dict(musicogenic_frac=0.01))
    for ef in (0.0, 0.2, 1.0): add(f"musicogenic_cohort_emotional{ef}", "music", inst=dict(musicogenic_frac=1.0, emotional_frac=ef))
    add("musicogenic_cohort_music_OFF", "music", inst=dict(musicogenic_frac=1.0, off=["music"]))
    # SSRIs
    add("ssri_obsOR_depressed", "drug", inst=dict(ssri=dict(target="depressed", mult=1.48, early_mult=2.35, early_days=30)))
    add("ssri_neutral_depressed", "drug", inst=dict(ssri=dict(target="depressed", mult=1.0, early_mult=1.0, early_days=0)))
    add("ssri_neutral_stressrelief_depressed", "drug", inst=dict(ssri=dict(target="depressed", mult=1.0, early_mult=1.0, early_days=0, stress_relief=True)))
    add("ssri_obsOR_stressrelief_depressed", "drug", inst=dict(ssri=dict(target="depressed", mult=1.48, early_mult=2.35, early_days=30, stress_relief=True)))
    add("ssri_obsOR_all", "drug", inst=dict(ssri=dict(target="all", mult=1.48, early_mult=2.35, early_days=30)))
    # stimulants
    add("stim_obsHR_0.73", "drug", inst=dict(stim=dict(mult=0.73)))
    add("stim_neutral", "drug", inst=dict(stim=dict(mult=1.0)))
    add("stim_threshold_1.3", "drug", inst=dict(stim=dict(mult=1.3)))
    add("stim_obsHR_plus_sleeploss", "combo", inst=dict(stim=dict(mult=0.73, sleep_mult=2.0)))
    add("stim_threshold_plus_sleeploss", "combo", inst=dict(stim=dict(mult=1.3, sleep_mult=2.0)))
    add("stim_neutral_plus_sleeploss", "combo", inst=dict(stim=dict(mult=1.0, sleep_mult=2.0)))
    # NSAIDs / ibuprofen
    add("nsaid_illness_neutral", "drug", inst=dict(nsaid=dict(on_illness=True, mult=1.0)))
    add("nsaid_illness_susceptible10pct", "drug", inst=dict(nsaid=dict(on_illness=True, mult=1.0, susceptible_frac=0.10, mult_susceptible=1.3)))
    add("nsaid_illness_animal_antiseizure", "drug", inst=dict(nsaid=dict(on_illness=True, mult=0.9)))
    add("nsaid_illness_fever_relief", "drug", inst=dict(nsaid=dict(on_illness=True, mult=1.0, fever_relief=0.5)))
    add("nsaid_regular_neutral", "drug", inst=dict(nsaid=dict(p_day=0.05, mult=1.0)))
    add("nsaid_regular_susceptible10pct", "drug", inst=dict(nsaid=dict(p_day=0.05, mult=1.0, susceptible_frac=0.10, mult_susceptible=1.3)))
    # psilocybin (people WITH epilepsy)
    for dose, H in (("low", dict(anti=dict(mult=0.8, mult_next=1.0), neutral=dict(mult=1.0, mult_next=1.0), exacerb=dict(mult=1.5, mult_next=1.2))),
                    ("high", dict(anti=dict(mult=0.7, mult_next=1.0), neutral=dict(mult=1.0, mult_next=1.0),
                                  exacerb=dict(mult=3.0, mult_next=1.5, susceptible_frac=0.3, mult_susceptible=10.0, mult_next_susceptible=3.0)))):
        for hyp, d in H.items(): add(f"psilo_{dose}_{hyp}", "drug", inst=dict(psilo=dict(days=PSILO_DAYS, **d)))
    add("psilo_high_exacerb_plus_ssri", "combo", inst=dict(psilo=dict(days=PSILO_DAYS, mult=3.0, mult_next=1.5, susceptible_frac=0.3, mult_susceptible=10.0,
                                                                      mult_next_susceptible=3.0, ssri_interaction=1.5),
                                                           ssri=dict(target="all", mult=1.48, early_mult=2.35, early_days=30)))
    # other recreational drugs (cocaine/high-dose amphetamine-like)
    add("recdrug_monthly_x5", "drug", inst=dict(recdrug=dict(p_day=1 / 30, mult=5.0)))
    add("recdrug_weekly_x5", "drug", inst=dict(recdrug=dict(p_day=1 / 7, mult=5.0)))
    # combinations / cascades (exposure x2)
    for nm, ks in (("stress+sleep", ["stress", "sleep"]), ("stress+sleep+miss", ["stress", "sleep", "miss"]), ("binge+sleep", ["binge", "sleep"]),
                   ("ill+miss", ["ill", "miss"]), ("stress+miss", ["stress", "miss"]), ("common5", ["stress", "sleep", "miss", "binge", "ill"])):
        add(f"combo_{nm}_AMPx2", "combo", inst=dict(amp={k: 2.0 for k in ks}))
    add("combo_common5_AMPx2_spongeOFF", "combo", inst=dict(amp={k: 2.0 for k in ["stress", "sleep", "miss", "binge", "ill"]}),
        layers={**{l: True for l in LAYERS}, "sponge": False})
    add("stress_AMPx2_spongeOFF", "combo", inst=dict(amp={"stress": 2.0}), layers={**{l: True for l in LAYERS}, "sponge": False})
    add("sleep_AMPx2_spongeOFF", "combo", inst=dict(amp={"sleep": 2.0}), layers={**{l: True for l in LAYERS}, "sponge": False})
    add("combo_stress+sleep_AMPx2_spongeOFF", "combo", inst=dict(amp={"stress": 2.0, "sleep": 2.0}), layers={**{l: True for l in LAYERS}, "sponge": False})
    # layers: all-on minus one, all-off plus one
    for l in LAYERS:
        add(f"layer_minus_{l}", "layer", layers={**{m: True for m in LAYERS}, l: False})
        add(f"layer_only_{l}", "layer", layers={**{m: False for m in LAYERS}, l: True})
    for l in ("materials", "physics", "heat"):
        add(f"layer_only_{l}_with_sponge", "layer", layers={**{m: False for m in LAYERS}, l: True, "sponge": True})
    # cell shading: observational (default) vs coupled-feedback variants (provisional definition, CELL_SHADING.md)
    for fb in (0.25, 0.5, 1.0): add(f"shading_feedback_{fb}", "shading", layers={**{m: True for m in LAYERS}, "shading": {"feedback": fb}})
    add("shading_feedback_0.5_spongeOFF", "shading", layers={**{m: True for m in LAYERS}, "sponge": False, "shading": {"feedback": 0.5}})
    add("shading_bands_coarse", "shading", layers={**{m: True for m in LAYERS}, "shading": {"bands": [0.5]}})
    # sponge parameter sweep (one at a time, all other layers on)
    for k, vals in (("capacity", [10.0, 160.0]), ("permeability", [0.01, 0.2]), ("kill", [0.05]), ("circ_gate", [0.03, 0.3]), ("dorm_gate", [0.1, 0.9])):
        for v in vals: add(f"sponge_{k}_{v}", "sponge", layers={**{m: True for m in LAYERS}, "sponge": {k: v}})
    return C
