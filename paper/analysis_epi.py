# Analysis for the epilepsy-sim manuscript. Every number used in the text is read from ../data/*.csv|json (or ../PREFLIGHT.md, ../data/calibration).
# Produces figures in ./figures and the dict F of derived quantities. No simulation is re-run here.
import os, re, json, collections, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..')); DATA = os.path.join(ROOT, 'data'); FIG = os.path.join(HERE, 'figures')
os.makedirs(FIG, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, 'code')); import targets as TG
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Liberation Serif', 'DejaVu Serif'], 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 200, 'savefig.dpi': 200})
GREY = '#9a9a9a'; DARK = '#222222'; BLUE = '#2b5c8a'; ORANGE = '#c8741a'; RED = '#a23b3b'

S = pd.read_csv(os.path.join(DATA, 'summary_conditions.csv')).set_index('name')
RI = pd.read_csv(os.path.join(DATA, 'run_info_conditions.csv')).set_index('name')
CT = pd.read_csv(os.path.join(DATA, 'contrasts.csv'))
FO = pd.read_csv(os.path.join(DATA, 'final_observables.csv')).set_index('observable')
NH = pd.read_csv(os.path.join(DATA, 'nohist_psilocybin.csv')).set_index('name')
SY = pd.read_csv(os.path.join(DATA, 'synergy.csv'))
EV = json.load(open(os.path.join(DATA, 'cell_shading_event_triggered.json')))
SZ2 = json.load(open(os.path.join(DATA, 'public', 'seizeit2_summary.json')))
NHB = json.load(open(os.path.join(DATA, 'nohist_base_rate.json')))
US = [json.loads(l) for l in open(os.path.join(DATA, 'update_sequence_log.jsonl'))]
PAR = {sc: json.load(open(os.path.join(DATA, 'calibration', f'params_{sc}.json'))) for sc in ['FULL_anchored', 'FULL_free', 'CORE_anchored', 'CORE_free']}

def con(name, subset='all'):
    x = CT[(CT.condition == name) & (CT['subset'].str.startswith(subset))]
    assert len(x) >= 1, (name, subset); return x.iloc[0]
def syn(combo, key):
    x = SY[(SY.combo == combo) & (SY.key == key)]; return x.iloc[0]
def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h

F = {}
F['n_cond'] = len(S); F['n_persons'] = int(S.persons.sum()); F['nohist_persons'] = int(80000 * 5 + 120000)
assert F['n_persons'] == 1130000 and (RI.stop_reason == 'precision').all() and len(RI) == 117
F['recon_bad'] = int(RI.recon_bad.sum()); F['obs_bad'] = int(RI.obs_bad.sum()); F['checks_bad'] = int(RI.checks_bad.sum()); F['shade_bad'] = int(RI.shade_recon_bad.sum())
F['recon_n'] = int(RI.recon_n.sum()); F['obs_n'] = int(RI.obs_n.sum())
F['spill_conds'] = [(n, float(v)) for n, v in RI.bk_spill_levy.items() if v > 0]
F['cons_ok'] = bool(RI.bk_conservation_ok.all()); F['levy_ok'] = bool(RI.bk_levy_matches_model.all()); F['bg_fail'] = int(RI.bg_diag_fail.sum())
F['cpu_s'] = float(RI.seconds.sum()); F['batches_min'] = int(RI.batches.min()); F['batches_max'] = int(RI.batches.max())
F['persons_by_cond'] = collections.Counter(S.persons)
F['hardcap_max'] = float(S.sp_hardcap_any.max()); F['hardcap_n_pos'] = int((S.sp_hardcap_any > 0).sum()); F['hardcap_n'] = int(S.sp_hardcap_any.notna().sum())
# update sequence
F['us_n'] = len(US); F['us_ver'] = int(sum(bool(x['verified']) for x in US))
F['us_corr'] = int(sum(x['steps']['autocorrect']['n_corrections'] for x in US)); F['us_err'] = int(sum(x['steps']['autocorrect']['n_errors'] for x in US))
F['us_iter'] = sum(1 for x in US if x['context'].startswith('calibrate') and 'best-iterate' in x['context'])
F['us_write'] = sum(1 for x in US if 'committed' in x); F['us_reg'] = sum(1 for x in US if x['context'].startswith('harness register'))
F['us_exact'] = bool(all(x['steps']['undo']['restore_exact'] and x['steps']['do_it_again']['identical'] for x in US))
assert F['us_n'] == F['us_iter'] + F['us_write'] + F['us_reg']
# preflight
pf = open(os.path.join(ROOT, 'PREFLIGHT.md')).read().splitlines()
rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in pf if l.startswith('| ') and not l.startswith('| Area')]
F['pf_rows'] = rows; F['pf_n'] = len(rows); F['pf_pass'] = sum(r[2] == 'PASS' for r in rows)
F['pf_area'] = collections.OrderedDict(); [F['pf_area'].__setitem__(r[0], F['pf_area'].get(r[0], 0) + 1) for r in rows]
F['pf_head'] = [l for l in pf if 'Result:' in l][0]
# calibration
BASE = S.loc['baseline']
TARGET_KEYS = list(TG.TARGETS.keys()); OBSCOL = {'sf12': 'p_sf12', 'cluster_given_sz': 'cluster_given_sz', 'attr_stress': 'attr_stress', 'attr_sleep': 'attr_sleep', 'attr_miss': 'attr_miss', 'attr_ill': 'attr_ill',
                                          'attr_catamenial_women': 'attr_catamenial_women', 'attr_any': 'attr_any', 'attr_two_plus': 'attr_two_plus'}
SC_ROWS = {'FULL_anchored': 'calset_FULL_anchored', 'FULL_free': 'calset_FULL_free', 'CORE_anchored': 'calset_CORE_anchored', 'CORE_free': 'calset_CORE_free'}
F['val'] = {}
for sc, nm in SC_ROWS.items():
    ob = {k: float(S.loc[nm, OBSCOL[k]]) for k in TARGET_KEYS}; sco, _ = TG.score(ob); ib = TG.in_band(ob)
    F['val'][sc] = dict(ob=ob, score=sco, nin=sum(ib.values()), ib=ib, sf=float(S.loc[nm, 'p_sf12']), lo=float(S.loc[nm, 'p_sf12_lo']), hi=float(S.loc[nm, 'p_sf12_hi']),
                       cal_score=PAR[sc]['_calibration']['score'], n_eval=PAR[sc]['_calibration']['n_eval'], n_cal=PAR[sc]['_calibration']['n_persons'])
    assert F['val'][sc]['nin'] == int(S.loc[nm, 'fit_in_band']), (sc, F['val'][sc]['nin'], S.loc[nm, 'fit_in_band'])
F['nbands'] = len(TARGET_KEYS)
F['fo'] = FO

# ------------------------------------------------------------------ figures
def save(fig, fn): fig.savefig(os.path.join(FIG, fn), bbox_inches='tight'); plt.close(fig)
LAB = {'sf12': 'Seizure-free\n12 months', 'cluster_given_sz': 'Cluster day\n(still seizing)', 'attr_stress': 'Reports\nstress', 'attr_sleep': 'Reports\nsleep loss', 'attr_miss': 'Reports\nmissed dose', 'attr_ill': 'Reports\nillness',
       'attr_catamenial_women': 'Reports\ncatamenial', 'attr_any': 'Reports\n≥1 trigger', 'attr_two_plus': 'Reports\n≥2 triggers'}
# Fig 1 calibration fit
fig, ax = plt.subplots(figsize=(7.2, 3.3))
for i, k in enumerate(TARGET_KEYS):
    pt, lo, hi, _ = TG.TARGETS[k]; ax.add_patch(plt.Rectangle((i - 0.33, lo), 0.66, hi - lo, color='#d9d9d9', zorder=0))
    ax.plot([i - 0.33, i + 0.33], [pt, pt], color='#777777', lw=0.8, zorder=1)
mk = {'FULL_anchored': ('o', DARK, 'MAIN (all layers + sponge, anchored)'), 'FULL_free': ('s', ORANGE, 'all layers, free multipliers'), 'CORE_anchored': ('^', BLUE, 'core only, anchored'), 'CORE_free': ('v', RED, 'core only, free')}
for j, (sc, (m, c, lab)) in enumerate(mk.items()):
    xs = np.arange(len(TARGET_KEYS)) + (j - 1.5) * 0.14; ys = [F['val'][sc]['ob'][k] for k in TARGET_KEYS]
    ax.plot(xs, ys, m, color=c, ms=5, label=lab, ls='none', zorder=3)
mo = FO.loc[[ {'sf12': 'sf12', 'cluster_given_sz': 'cluster_any'}.get(k, k) for k in TARGET_KEYS]]
ax.errorbar(np.arange(len(TARGET_KEYS)) - 0.21, mo.value, yerr=[mo.value - mo.lo, mo.hi - mo.value], fmt='none', ecolor=DARK, elinewidth=0.8, capsize=1.5, zorder=2)
ax.set_xticks(range(len(TARGET_KEYS))); ax.set_xticklabels([LAB[k] for k in TARGET_KEYS], fontsize=7.5); ax.set_ylabel('proportion'); ax.set_ylim(0, 1)
ax.legend(fontsize=7, frameon=False, loc='upper right', ncol=2, bbox_to_anchor=(1.0, 1.18)); ax.text(0.0, -0.33, 'Grey bars: published range of each target; thin line: point value used. Validation seeds, 10,000 people per scenario; bars on MAIN = 95% CI.', transform=ax.transAxes, fontsize=7)
save(fig, 'fig1_calibration_fit.png')

# Fig 2 triggers
TRG = [('missed medication', 'miss'), ('stress', 'stress'), ('catamenial (women)', 'catamenial'), ('illness / fever', 'ill'), ('binge drinking', 'binge'), ('sleep loss', 'sleep'), ('low pressure', 'weather'), ('sensory overload', 'sensory'),
       ('photic', 'photic'), ('moderate alcohol', 'alcohol'), ('generic music', 'music')]
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
for k, (lab, key) in enumerate(TRG):
    r = con(f'{key}_OFF'); o = con(f'{key}_ONLY')
    for a, v, c, off in ((axs[0], r.d_sf12, BLUE, 0.17), (axs[0], o.d_sf12, ORANGE, -0.17)):
        pass
    axs[0].errorbar(100 * r.d_sf12, k - 0.17, xerr=[[100 * (r.d_sf12 - r.d_sf12_lo)], [100 * (r.d_sf12_hi - r.d_sf12)]], fmt='o', color=BLUE, ms=3.5, capsize=1.5, lw=0.9, label='remove it (vs MAIN)' if k == 0 else None)
    axs[0].errorbar(100 * o.d_sf12, k + 0.17, xerr=[[100 * (o.d_sf12 - o.d_sf12_lo)], [100 * (o.d_sf12_hi - o.d_sf12)]], fmt='s', color=ORANGE, ms=3.5, capsize=1.5, lw=0.9, label='add it alone (vs no triggers)' if k == 0 else None)
    axs[1].errorbar(r.d_seiz_obs, k - 0.17, xerr=[[r.d_seiz_obs - r.d_seiz_obs_lo], [r.d_seiz_obs_hi - r.d_seiz_obs]], fmt='o', color=BLUE, ms=3.5, capsize=1.5, lw=0.9)
    axs[1].errorbar(o.d_seiz_obs, k + 0.17, xerr=[[o.d_seiz_obs - o.d_seiz_obs_lo], [o.d_seiz_obs_hi - o.d_seiz_obs]], fmt='s', color=ORANGE, ms=3.5, capsize=1.5, lw=0.9)
for a in axs: a.axvline(0, color='#666666', lw=0.6)
axs[0].set_yticks(range(len(TRG))); axs[0].set_yticklabels([t[0] for t in TRG]); axs[0].invert_yaxis()
axs[0].set_xlabel('change in P(seizure-free, 12 m), percentage points'); axs[1].set_xlabel('change in seizures per person-year'); axs[0].legend(fontsize=7, frameon=False, loc='center right')
save(fig, 'fig2_triggers.png')

# Fig 3 self-report vs causal
ATT = [('missed medication', 'miss', 'miss'), ('stress', 'stress', 'stress'), ('sleep loss', 'sleep', 'sleep'), ('illness', 'ill', 'ill'), ('binge drinking', 'binge', 'binge'), ('low pressure', 'weather', 'weather'), ('moderate alcohol', 'alcohol', 'alcohol'),
       ('sensory overload', 'sensory', 'sensory'), ('photic', 'photic', 'photic'), ('generic music', 'music', 'music')]
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={'width_ratios': [1.6, 1]}, sharey=True)
for k, (lab, a, c) in enumerate(ATT):
    axs[0].barh(k - 0.19, 100 * FO.loc[f'attr_{a}', 'value'], 0.36, color=BLUE, label='perceived rule' if k == 0 else None)
    axs[0].barh(k + 0.19, 100 * FO.loc[f'attrN_{a}', 'value'], 0.36, color='#bbbbbb', label='naive rule (any coincidence)' if k == 0 else None)
    r = con(f'{c}_OFF'); axs[1].errorbar(100 * r.d_sf12, k, xerr=[[100 * (r.d_sf12 - r.d_sf12_lo)], [100 * (r.d_sf12_hi - r.d_sf12)]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
axs[0].set_yticks(range(len(ATT))); axs[0].set_yticklabels([t[0] for t in ATT]); axs[0].invert_yaxis(); axs[0].set_xlabel('% of people with seizures who "report" it as a trigger'); axs[0].legend(fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2)
axs[1].axvline(0, color='#666666', lw=0.6); axs[1].set_xlabel('true effect of removing it:\nΔ P(seizure-free), pp')
save(fig, 'fig3_self_report.png')

# Fig 4 music
MU = [('realistic musicogenic\nprevalence (music OFF = same)', 'baseline'), ('upper bound 1%\n(unsourced)', 'musicogenic_userupper_1pct'), ('generic music protective\n(×0.9, K.448-type)', 'music_generic_protective_K448'),
      ('all susceptible,\nneutral music only', 'musicogenic_cohort_emotional0.0'), ('all susceptible,\n20% emotional', 'musicogenic_cohort_emotional0.2'), ('all susceptible,\n100% emotional', 'musicogenic_cohort_emotional1.0')]
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
for k, (lab, n) in enumerate(MU):
    r = S.loc[n]; axs[0].errorbar(r.p_sf12, k, xerr=[[r.p_sf12 - r.p_sf12_lo], [r.p_sf12_hi - r.p_sf12]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
    axs[1].errorbar(r.seiz_per_yr, k, xerr=[[r.seiz_per_yr - r.seiz_per_yr_lo], [r.seiz_per_yr_hi - r.seiz_per_yr]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
axs[0].axvline(BASE.p_sf12, color=GREY, lw=0.7, ls='--'); axs[1].axvline(BASE.seiz_per_yr, color=GREY, lw=0.7, ls='--')
axs[0].set_yticks(range(len(MU))); axs[0].set_yticklabels([m[0] for m in MU], fontsize=7.5); axs[0].invert_yaxis(); axs[0].set_xlabel('P(seizure-free, 12 m)'); axs[1].set_xlabel('seizures per person-year (log scale)'); axs[1].set_xscale('log'); axs[1].set_xticks([1.5, 2, 4, 10, 20, 40]); axs[1].set_xticklabels(['1.5', '2', '4', '10', '20', '40']); axs[1].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
save(fig, 'fig4_music.png')

# Fig 5 drugs forest
DR = [('SSRI, observational OR, depressed subgroup (exposed)', 'ssri_obsOR_depressed', 'exposed'), ('SSRI, observational OR, everyone', 'ssri_obsOR_all', 'all'), ('SSRI, neutral (epilepsy-specific evidence)', 'ssri_neutral_depressed', 'all'),
      ('SSRI neutral + stress relief (exposed)', 'ssri_neutral_stressrelief_depressed', 'exposed'), ('SSRI observational + stress relief (exposed)', 'ssri_obsOR_stressrelief_depressed', 'exposed'),
      ('Stimulant, HR 0.73 (Brikell)', 'stim_obsHR_0.73', 'all'), ('Stimulant, neutral', 'stim_neutral', 'all'), ('Stimulant, threshold-lowering ×1.3 (assumed)', 'stim_threshold_1.3', 'all'),
      ('Stimulant threshold ×1.3 + doubled sleep loss', 'stim_threshold_plus_sleeploss', 'all'), ('NSAID on illness days, neutral', 'nsaid_illness_neutral', 'all'), ('NSAID, 10% susceptible ×1.3', 'nsaid_illness_susceptible10pct', 'all'),
      ('NSAID, animal antiseizure ×0.9', 'nsaid_illness_animal_antiseizure', 'all'), ('NSAID, fever relief', 'nsaid_illness_fever_relief', 'all'),
      ('Psilocybin low dose, exacerbation', 'psilo_low_exacerb', 'all'), ('Psilocybin high dose, antiseizure', 'psilo_high_anti', 'all'), ('Psilocybin high dose, exacerbation', 'psilo_high_exacerb', 'all'),
      ('Psilocybin high exacerbation + SSRI for all', 'psilo_high_exacerb_plus_ssri', 'all'), ('Other recreational drug, monthly ×5', 'recdrug_monthly_x5', 'all'), ('Other recreational drug, weekly ×5', 'recdrug_weekly_x5', 'all')]
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for k, (lab, n, sub) in enumerate(DR):
    r = con(n, 'exposed' if sub == 'exposed' else 'all'); c = RED if r.d_sf12 < 0 and r.d_sf12_hi < 0 else (BLUE if r.d_sf12 > 0 and r.d_sf12_lo > 0 else GREY)
    ax.errorbar(100 * r.d_sf12, k, xerr=[[100 * (r.d_sf12 - r.d_sf12_lo)], [100 * (r.d_sf12_hi - r.d_sf12)]], fmt='o', color=c, ms=3.5, capsize=1.5, lw=0.9)
ax.axvline(0, color='#666666', lw=0.6); ax.set_yticks(range(len(DR))); ax.set_yticklabels([d[0] for d in DR], fontsize=7.5); ax.invert_yaxis(); ax.set_xlabel('paired change in P(seizure-free, 12 m) vs MAIN, percentage points (95% CI; red = lower, blue = higher, grey = indistinguishable from 0)')
ax.xaxis.label.set_size(7.5)
save(fig, 'fig5_drugs.png')

# Fig 6 psilocybin no-history + synergy
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={'width_ratios': [1.15, 1.2], 'wspace': 0.85})
NHL = [('low\nneutral', 'nohist_psilo_low_neutral'), ('low\nexacerb.', 'nohist_psilo_low_exacerb'), ('high\nneutral', 'nohist_psilo_high_neutral'), ('high\nexacerb.', 'nohist_psilo_high_exacerb'), ('high exac.\n+ SSRI\nfor all', 'nohist_psilo_high_exacerb_plus_ssri')]
for k, (lab, n) in enumerate(NHL):
    r = NH.loc[n]; axs[0].errorbar(k, r.excess_per100k, yerr=[[r.excess_per100k - r.excess_lo], [r.excess_hi - r.excess_per100k]], fmt='o', color=DARK if k < 4 else RED, ms=3.5, capsize=2, lw=0.9)
axs[0].axhline(0, color='#666666', lw=0.6); axs[0].set_xticks(range(len(NHL))); axs[0].set_xticklabels([n[0] for n in NHL], fontsize=7); axs[0].set_xlabel('psilocybin dose and hypothesis', fontsize=7.5); axs[0].set_ylabel('excess first seizures per 100,000 person-years'); axs[0].set_title('(a) people with no seizure history', fontsize=8.5)
SYN = [('stress × missed dose', 'combo_stress+miss_AMPx2'), ('illness × missed dose', 'combo_ill+miss_AMPx2'), ('stimulant ×1.3 × sleep loss', 'stim_threshold_plus_sleeploss'), ('stress × sleep, sponge OFF', 'combo_stress+sleep_AMPx2_spongeOFF'), ('stress × sleep, sponge ON', 'combo_stress+sleep_AMPx2'), ('binge × sleep', 'combo_binge+sleep_AMPx2')]
for k, (lab, n) in enumerate(SYN):
    r = syn(n, 'seiz_obs'); axs[1].errorbar(r.interaction, k, xerr=[[r.interaction - r.lo], [r.hi - r.interaction]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
axs[1].axvline(0, color='#666666', lw=0.6); axs[1].set_yticks(range(len(SYN))); axs[1].set_yticklabels([s[0] for s in SYN], fontsize=7.5); axs[1].invert_yaxis(); axs[1].set_xlabel('interaction, seizures per person-year'); axs[1].set_title('(b) synergy (combination − A − B + baseline)', fontsize=8.5)
save(fig, 'fig6_psilocybin_synergy.png')

# Fig 7 layers + sponge parameters
LY = [('sponge', 'sponge'), ('inhibition', 'inhibition'), ('HPA axis', 'hpa'), ('kindling', 'kindling'), ('network coupling', 'network'), ('materials', 'materials'), ('physics', 'physics'), ('heat-trace', 'heat'), ('cell shading (observational)', 'shading')]
fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.1), gridspec_kw={'width_ratios': [1, 1, 1.05]})
for k, (lab, key) in enumerate(LY):
    r = con(f'layer_minus_{key}'); o = con(f'layer_only_{key}')
    axs[0].errorbar(100 * r.d_sf12, k, xerr=[[100 * (r.d_sf12 - r.d_sf12_lo)], [100 * (r.d_sf12_hi - r.d_sf12)]], fmt='o', color=BLUE, ms=3.5, capsize=1.5, lw=0.9)
    axs[1].errorbar(100 * o.d_sf12, k, xerr=[[100 * (o.d_sf12 - o.d_sf12_lo)], [100 * (o.d_sf12_hi - o.d_sf12)]], fmt='s', color=ORANGE, ms=3.5, capsize=1.5, lw=0.9)
for a in axs[:2]: a.axvline(0, color='#666666', lw=0.6)
axs[0].set_yticks(range(len(LY))); axs[0].set_yticklabels([l[0] for l in LY], fontsize=7.5); axs[0].invert_yaxis(); axs[1].set_yticks([]); axs[1].invert_yaxis()
axs[0].set_xlabel('(a) all layers on except this one,\nΔ P(seizure-free) vs MAIN, pp', fontsize=7.5); axs[1].set_xlabel('(b) all layers off except this one,\nΔ P(seizure-free) vs core, pp', fontsize=7.5)
SP = [('relapse gate 0.9', 'sponge_dorm_gate_0.9'), ('relapse gate 0.1', 'sponge_dorm_gate_0.1'), ('network gate 0.3', 'sponge_circ_gate_0.3'), ('network gate 0.03', 'sponge_circ_gate_0.03'), ('capacity 160', 'sponge_capacity_160.0'), ('capacity 10', 'sponge_capacity_10.0'),
      ('permeability 0.2', 'sponge_permeability_0.2'), ('permeability 0.01', 'sponge_permeability_0.01'), ('kill rate 0.05', 'sponge_kill_0.05')]
for k, (lab, n) in enumerate(SP):
    r = con(n); axs[2].errorbar(100 * r.d_sf12, k, xerr=[[100 * (r.d_sf12 - r.d_sf12_lo)], [100 * (r.d_sf12_hi - r.d_sf12)]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
axs[2].axvline(0, color='#666666', lw=0.6); axs[2].set_yticks(range(len(SP))); axs[2].set_yticklabels([s[0] for s in SP], fontsize=7.5); axs[2].yaxis.tick_right(); axs[2].spines['right'].set_visible(True); axs[2].spines['left'].set_visible(False); axs[2].invert_yaxis()
axs[2].set_xlabel('(c) sponge parameter change,\nΔ P(seizure-free) vs MAIN, pp', fontsize=7.5)
save(fig, 'fig7_layers_sponge.png')

# copy of repo charts 07 and 08 (provisional cell shading) at original resolution
import shutil
shutil.copy(os.path.join(ROOT, 'charts', '07_cell_shading_raster.png'), os.path.join(FIG, 'fig8_cell_shading_raster.png'))
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.8), gridspec_kw={'wspace': 1.05, 'width_ratios': [1, 1, 1.15]})
w = EV['window']; y = EV['event_triggered_shade']; axs[0].plot(w, y, color=DARK, lw=1.3); axs[0].axvline(0, color=RED, lw=0.7); axs[0].set_xlabel('days from a seizure'); axs[0].set_ylabel('whole-brain shade'); axs[0].set_title('(a) shade around seizures', fontsize=8)
bs = [BASE[f'band{i}_share'] for i in range(4)]; ls = [BASE[f'levy_band{i}_share'] for i in range(4)]; x = np.arange(4)
axs[1].bar(x - 0.2, bs, 0.4, color=BLUE, label='share of brain-days'); axs[1].bar(x + 0.2, ls, 0.4, color=ORANGE, label='share of event weight')
axs[1].set_xticks(x); axs[1].set_xticklabels(['dark', 'quiet', 'active', 'ictal'], fontsize=7); axs[1].legend(fontsize=6.5, frameon=False, loc='upper left'); axs[1].set_title('(b) cel bands, MAIN', fontsize=8); axs[1].set_ylim(0, 1.15)
SV = [('observational (baseline)', 'baseline'), ('coupled 0.25', 'shading_feedback_0.25'), ('coupled 0.5', 'shading_feedback_0.5'), ('coupled 1.0', 'shading_feedback_1.0'), ('sponge OFF baseline', 'baseline_spongeOFF'), ('coupled 0.5, sponge OFF', 'shading_feedback_0.5_spongeOFF')]
for k, (lab, n) in enumerate(SV):
    r = S.loc[n]; axs[2].errorbar(r.p_sf12, k, xerr=[[r.p_sf12 - r.p_sf12_lo], [r.p_sf12_hi - r.p_sf12]], fmt='o', color=DARK, ms=3.5, capsize=1.5, lw=0.9)
axs[2].set_yticks(range(len(SV))); axs[2].set_yticklabels([s_[0] for s_ in SV], fontsize=7); axs[2].invert_yaxis(); axs[2].set_xlabel('P(seizure-free, 12 m)'); axs[2].set_title('(c) observational vs coupled', fontsize=8)
save(fig, 'fig9_cell_shading_events.png')
print('analysis ok', F['pf_n'], F['us_n'], {k: (round(v['score'], 3), v['nin']) for k, v in F['val'].items()})
