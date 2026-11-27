#!/usr/bin/env python3
"""Summary statistics from the PUBLIC SeizeIT2 annotations (OpenNeuro ds005873 v1.1.0, CC0; only the small *_events.tsv
annotation files were downloaded - no signal data). Runs of one subject are concatenated in run order using each run's
recordingDuration (ASSUMPTION: runs are consecutive with no gaps; the dataset anonymises dates). EMU recordings in people with
refractory epilepsy admitted for presurgical evaluation - medication is often tapered, so rates are NOT outpatient rates; used only
as a qualitative check of over-dispersion / clustering (inter-seizure-interval CV, share of short intervals, >=3 seizures in 24 h)."""
import glob, os, re, json, numpy as np, pandas as pd
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sources", "openneuro", "ds005873_events")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "public")
os.makedirs(OUT, exist_ok=True)
rows = []
for f in sorted(glob.glob(os.path.join(SRC, "*_events.tsv"))):
    m = re.search(r"(sub-\d+)__ses-(\d+)__eeg__.*run-(\d+)_events", f); sub, ses, run = m.group(1), int(m.group(2)), int(m.group(3))
    d = pd.read_csv(f, sep="\t"); dur = float(d.recordingDuration.iloc[0]) if len(d) else 0.0
    for _, r in d.iterrows():
        rows.append(dict(sub=sub, ses=ses, run=run, rec_dur=dur, onset=float(r.onset), duration=float(r.duration), type=str(r.eventType)))
    if len(d) == 0: rows.append(dict(sub=sub, ses=ses, run=run, rec_dur=dur, onset=np.nan, duration=np.nan, type="none"))
E = pd.DataFrame(rows)
runs = E.groupby(["sub", "ses", "run"]).rec_dur.first().reset_index().sort_values(["sub", "ses", "run"])
runs["offset"] = runs.groupby("sub").rec_dur.cumsum() - runs.rec_dur
E = E.merge(runs[["sub", "ses", "run", "offset"]], on=["sub", "ses", "run"])
S = E[E.type.str.startswith("sz")].copy(); S["t"] = S.offset + S.onset
per = []
isis = []
for sub, g in runs.groupby("sub"):
    tot_h = g.rec_dur.sum() / 3600; ts = np.sort(S[S["sub"] == sub].t.values); isi = np.diff(ts) / 3600
    isis += list(isi)
    c24 = max((np.searchsorted(ts, x + 86400, side="left") - i for i, x in enumerate(ts)), default=0)
    per.append(dict(sub=sub, hours=tot_h, n_sz=len(ts), max_in_24h=int(c24), isi_cv=float(isi.std() / isi.mean()) if len(isi) > 2 and isi.mean() > 0 else np.nan))
P = pd.DataFrame(per); isis = np.array(isis)
summ = dict(source="OpenNeuro ds005873 (SeizeIT2) v1.1.0, CC0, doi:10.18112/openneuro.ds005873.v1.1.0", subjects=int(len(P)), total_hours=float(P.hours.sum()),
            seizures=int(P.n_sz.sum()), subjects_with_seizure=int((P.n_sz > 0).sum()), median_hours_per_subject=float(P.hours.median()),
            seizures_per_subject_median_among_with=float(P.n_sz[P.n_sz > 0].median()),
            frac_subjects_ge3_in_24h_among_with_seizures=float((P.max_in_24h[P.n_sz > 0] >= 3).mean()),
            pooled_isi_hours_median=float(np.median(isis)) if len(isis) else None, pooled_isi_cv=float(isis.std() / isis.mean()) if len(isis) else None,
            frac_isi_under_4h=float((isis < 4).mean()) if len(isis) else None, frac_isi_under_24h=float((isis < 24).mean()) if len(isis) else None,
            median_subject_isi_cv=float(P.isi_cv.median()), seizure_type_counts=S.type.value_counts().to_dict())
P.to_csv(os.path.join(OUT, "seizeit2_per_subject.csv"), index=False)
json.dump(summ, open(os.path.join(OUT, "seizeit2_summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k != "seizure_type_counts"}, indent=1))
