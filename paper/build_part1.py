# Build the epilepsy-sim manuscript. python-docx -> DOCX, LibreOffice -> PDF (same pipeline/style as study-writeup/v5).
# Every number in the text is taken from analysis_epi.py (reads ../data/*), never typed by hand, except text copied from the repo's own documentation.
import os, subprocess, re, json
import numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import analysis_epi as A
from analysis_epi import F, S, CT, FO, NH, SY, con, syn, wil, BASE, PAR, EV, SZ2, RI

HERE = A.HERE; FIG = A.FIG
TITLE = 'A calibrated relational simulation of seizure dynamics built on public epilepsy data: triggers, drug, music and psilocybin scenarios, an absorptive buffer, and provisional cell shading'
NAME = 'Caitlyn Randels'

def pc(x, d=1): return f'{100 * x:.{d}f}%'
def p3(x): return f'{x:.3f}'
def num(x, d=3): return f'{x:.{d}f}'
def cnt(x): return f'{int(round(x)):,}'
def sg(x, d=1): return f'{x + (1e-9 if x >= 0 else -1e-9):+.{d}f}'
def pp(x, d=1): return sg(100 * x, d)                       # proportion difference -> signed percentage points
def ppci(r, d=1, lo='d_sf12_lo', hi='d_sf12_hi', v='d_sf12'): return f'{pp(r[v], d)} [{pp(r[lo], d)}, {pp(r[hi], d)}]'
def sci(r, d=2): return f'{sg(r.d_seiz_obs, d)} [{sg(r.d_seiz_obs_lo, d)}, {sg(r.d_seiz_obs_hi, d)}]'
def pci(r, d=1): return f'{100 * r.p_sf12:.{d}f}% [{100 * r.p_sf12_lo:.{d}f}, {100 * r.p_sf12_hi:.{d}f}]'

REFS = {
 'gbd': 'GBD 2021 Epilepsy Collaborators. [Global, regional and national burden of epilepsy, 1990–2021.] Lancet Public Health. 2025;10(3):e203–e227. doi:10.1016/S2468-2667(24)00302-5. IHME summary: https://www.healthdata.org/research-analysis/library/global-regional-and-national-burden-epilepsy-1990-2021',
 'who': 'World Health Organization. Epilepsy (fact sheet), 7 February 2024. https://www.who.int/news-room/fact-sheets/detail/epilepsy. Accessed 26 November 2026.',
 'fiest17': 'Fiest KM, et al. Prevalence and incidence of epilepsy: a systematic review and meta-analysis of international studies. Neurology. 2017. https://pmc.ncbi.nlm.nih.gov/articles/PMC5272794/',
 'cdc': 'US Centers for Disease Control and Prevention. Epilepsy data and statistics (facts and stats). https://www.cdc.gov/epilepsy/data-research/facts-stats/ ; MMWR 2015 report https://www.cdc.gov/mmwr/volumes/67/wr/mm6715a1.htm. Accessed 26 November 2026.',
 'chen18': 'Chen Z, et al. Treatment outcomes in patients with newly diagnosed epilepsy treated with established and new antiepileptic drugs: a 30-year longitudinal cohort study. JAMA Neurol. 2018;75:279. https://pmc.ncbi.nlm.nih.gov/articles/PMC5885858/',
 'kwan00': 'Kwan P, Brodie MJ. Early identification of refractory epilepsy. N Engl J Med. 2000;342:314–319. https://www.nejm.org/doi/full/10.1056/NEJM200002033420503 (abstract).',
 'ilae': 'Kwan P, et al. [ILAE task-force definition of drug-resistant epilepsy.] Epilepsia. 2010. https://www.ilae.org/files/ilaeGuideline/Definition-of-Drug-Resistant-Epilepsy-2009-1528-1167.2009.02397.pdf',
 'frucht': 'Frucht MM, et al. [Seizure precipitants, 400 patients, US tertiary centre.] Epilepsia. 2000. doi:10.1111/j.1499-1654.2000.001534.x (abstract).',
 'sperling': 'Sperling MR, et al. [Seizure precipitants, 200 patients, Thomas Jefferson University.] 2008. PubMed 17977026.',
 'nakken': 'Nakken KO, et al. [Self-reported seizure precipitants, n = 794, Norway.] 2005. PubMed 16138128.',
 'nanjing': '[Seizure precipitants, 154 patients, Nanjing.] 2017. doi:10.3760/cma.j.issn.1006-7876.2017.04.005 (abstract).',
 'aiims': '[Self-reported seizure precipitants, 405 patients, AIIMS, India.] Seizure. 2013. https://www.seizure-journal.com/article/S1059-1311(13)00177-5/fulltext',
 'saudi': '[Seizure precipitants, 546 patients, Saudi Arabia.] 2020;41(8):828. https://smj.org.sa/content/41/8/828',
 'epiwatch': '[EpiWatch app, self-reported triggers, 177 reporting.] Neurology. 2017;88(16 Suppl):S37.002 (abstract).',
 'tert23': '[Triggers documented in clinic records, 1,975 patients.] Neurology. 2023. doi:10.1212/WNL.0000000000203555.',
 'haut07': 'Haut SR, et al. [Prospective diary study of seizure precipitants, 71 adults, 15,179 diary days.] 2007. PubMed 17998482.',
 'stresslit': '[Stress and seizures: narrative review] doi:10.1111/epi.12377; cortisol/HPA review, PubMed 31129236; SMILE randomized trial, Neurology doi:10.1212/wnl.0000000000005109 (abstracts).',
 'ef': 'Epilepsy Foundation. Seizure triggers; missed medicines; drug abuse; photosensitivity. https://www.epilepsy.com/what-is-epilepsy/seizure-triggers ; https://www.epilepsy.com/what-is-epilepsy/seizure-triggers/photosensitivity. Accessed 26 November 2026.',
 'ea': 'Epilepsy Action. Photosensitive epilepsy. https://www.epilepsy.org.uk/info/seizure-triggers/photosensitive-epilepsy ; photosensitivity FAQ paper, https://pmc.ncbi.nlm.nih.gov/articles/PMC11995705/',
 'herzog': 'Herzog AG, et al. [Catamenial epilepsy patterns, 1997; NIH Progesterone Trial analysis.] Seizure. 2015. https://www.seizure-journal.com/article/S1059-1311(15)00052-7/fulltext',
 'weather': '[Weather and seizures: case-crossover study] doi:10.1111/epi.13776; 2024 admissions study, https://pmc.ncbi.nlm.nih.gov/articles/PMC11204309/',
 'hamerle': 'Hamerle M, et al. [Alcohol and seizures.] Front Neurol. 2018. https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2018.00401/full ; PubMed 29705654.',
 'cluster': '[Seizure cluster literature:] Haut SR, et al. Epilepsia 2022 (LGS Foundation PDF); Seizure 2018 review, https://www.seizure-journal.com/article/S1059-1311(18)30112-2/fulltext ; doi:10.1111/epi.13465.',
 'osorio': 'Osorio I, et al. [Seizure self-triggering and heavy-tailed inter-seizure intervals.] Phys Rev E. 2010;82:021919. https://arxiv.org/abs/0712.3929',
 'maguire': 'Maguire MJ. Music and epilepsy: a critical review. Epilepsia. 2012. doi:10.1111/j.1528-1167.2012.03523.x (cites Critchley 1977 for ~1 in 10,000,000).',
 'mozart': '[Mozart K.448 and epilepsy:] meta-analysis, PubMed 32449680; Sci Rep. 2023, https://www.nature.com/articles/s41598-023-30206-w ; Seizure. 2024 crossover RCT (abstracts).',
 'fiest13': 'Fiest KM, et al. Depression in epilepsy: a systematic review and meta-analysis. Neurology. 2013. https://pmc.ncbi.nlm.nih.gov/articles/PMC3589287/',
 'ssriobs': '[Antidepressants and seizure risk: meta-analysis.] Eur J Clin Pharmacol. 2023. PubMed 37996536.',
 'ssriepi': '[SSRIs in people with epilepsy:] https://pmc.ncbi.nlm.nih.gov/articles/PMC10514547/ ; Epilepsy Behav. 2016 review.',
 'brikell': 'Brikell I, et al. [ADHD medication periods and acute seizures in people with a seizure history.] Epilepsia. 2019. https://pmc.ncbi.nlm.nih.gov/articles/PMC6365170/',
 'nsaid': '[NSAIDs and seizures:] Hitchings (SGUL open-access PDF); PubMed 7202518; doi:10.2478/joepi-2024-0001; doi:10.1016/j.eplepsyres.2017.02.003.',
 'freidel': 'Freidel et al. [Psychedelics and seizures.] Front Pharmacol. 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC10811552/',
 'soto': 'Soto-Angona et al. [Scoping review of psychedelics and seizures.] 2024. PubMed 38917636.',
 'simonsson': 'Simonsson et al. [Psychedelic-related seizures in lifetime users, n = 613.] https://pmc.ncbi.nlm.nih.gov/articles/PMC9627432/',
 'mushcase': 'Case report of intracranially recorded seizures after a large recreational mushroom dose (ResearchGate listing, 2023; abstract only).',
 'balab': 'Balabandian et al. [Psilocin anticonvulsant effects in mice.] Pharmacol Res Perspect. 2025. doi:10.1002/prp2.70079.',
 'cocaine': '[Systematic review of cocaine and seizures.] Drug Alcohol Depend. doi:10.1016/j.drugalcdep.2013.08.019.',
 'openneuro': 'OpenNeuro / NEMAR public datasets (CC0): ds003029 (Li et al.), ds004100 (Bernabei et al.), ds003876, ds005398, and metadata for ds004752, ds003844, ds003555, ds004469, ds003498. https://openneuro.org ; https://nemar.org. Queried 26 November 2026.',
 'seizeit2': 'SeizeIT2 wearable EEG dataset, OpenNeuro ds005873 v1.1.0 (CC0). doi:10.18112/openneuro.ds005873.v1.1.0.',
 'oroboro': 'Randels C. Oroboro / consciousness-mapping repository (Oroboro_Framework_Summary, Sponge_Absorption_Mechanic, Operational_Update_Sequence, Oroboro_Metastasis_Architecture_Testbed, NaCl_Polarity_Mesh_Research_Note). GitHub: caitlynrandels-del/Oroboro. Read 26 November 2026.',
 'mca': 'Randels C. metastatic-cascade-analysis (model, v4 summary, Operational_Update_Sequence). GitHub: caitlynrandels-del/metastatic-cascade-analysis. Read 26 November 2026.',
 'v5': 'Randels C. A stochastic cascade model of metastatic dissemination calibrated to multiple public databases: effects of an absorptive buffer and optional domain layers at equal precision, and reproducibility. Manuscript, November 2026.',
}
ORDER = []
def C(*keys):
    for k in keys:
        if k not in ORDER: ORDER.append(k)
    ns = sorted(ORDER.index(k) + 1 for k in keys); out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1: j += 1
        out.append(f'{ns[i]}–{ns[j]}' if j - i >= 2 else ','.join(str(v) for v in ns[i:j + 1])); i = j + 1
    return '[' + ','.join(out) + ']'

d = Document()
st = d.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
for s in d.sections:
    s.left_margin = s.right_margin = Inches(1); s.top_margin = s.bottom_margin = Inches(0.9)
for hs, sz in [('Heading 1', 13), ('Heading 2', 11), ('Heading 3', 10.5)]:
    h = d.styles[hs]; h.font.name = 'Times New Roman'; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = RGBColor(0, 0, 0)
    for a in ('w:eastAsia', 'w:ascii', 'w:hAnsi'): h.element.rPr.rFonts.set(qn(a), 'Times New Roman')
    h.paragraph_format.space_before = Pt(10 if hs == 'Heading 1' else 7); h.paragraph_format.space_after = Pt(3); h.paragraph_format.keep_with_next = True
def footer_page_numbers():
    p = d.sections[0].footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Speculative modeling only. No clinical claims. No medical advice.   |   '); r.font.size = Pt(8)
    r = p.add_run(); r.font.size = Pt(9)
    for tag, txt in [('begin', None), (None, 'PAGE'), ('end', None)]:
        if tag:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), tag); r._r.append(e)
        else:
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt; r._r.append(e)
footer_page_numbers()
SECTION = {'name': ''}; LOG = []
import re as _rem
def mf(t): return _rem.sub(r'(?<![\w.])-(?=\d)', '\u2212', t) if isinstance(t, str) else t
def P(text, bold=False, italic=False, size=None, align=None, space=6, justify=True, keep=False):
    text = mf(text); LOG.append((SECTION['name'], text))
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align is not None: p.alignment = align
    elif justify: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space)
    if keep: p.paragraph_format.keep_with_next = True
    return p
def RP(parts, space=6):
    LOG.append((SECTION['name'], ' '.join(t for t, _ in parts)))
    p = d.add_paragraph()
    for t, bb in parts:
        r = p.add_run(mf(t)); r.bold = bb
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.space_after = Pt(space); return p
def H(text, lvl=1):
    if lvl == 1: SECTION['name'] = text
    LOG.append((SECTION['name'], text)); return d.add_heading(text, level=lvl)
def B(text):
    text = mf(text); LOG.append((SECTION['name'], text))
    p = d.add_paragraph(style='List Bullet'); p.add_run(text); p.paragraph_format.space_after = Pt(2); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color); tcPr.append(sh)
NT = [0]; NF = [0]
def T(header, rows, caption, note=None, widths=None, fs=8):
    NT[0] += 1; caption = f'Table {NT[0]}. {caption}'
    LOG.append((SECTION['name'], caption + ' ' + (note or '') + ' ' + ' '.join(str(x) for r in rows for x in r)))
    P(caption, bold=True, size=9, space=2, justify=False, keep=True)
    t = d.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(fs); shade(c, 'E8E8E8')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''; r = cells[i].paragraphs[0].add_run(mf(str(v))); r.font.size = Pt(fs)
    for ri, row in enumerate(t.rows):
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
                if ri < 2: p.paragraph_format.keep_with_next = True
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    if widths:
        t.autofit = False; tw = sum(widths); sc = min(1.0, 6.9 / tw)
        for i, w in enumerate(widths): t.columns[i].width = Inches(w * sc)
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Inches(w * sc)
    if note: P(note, size=8.5, space=8, justify=False)
    else: d.add_paragraph().paragraph_format.space_after = Pt(2)
def FIGURE(fn, caption, w=6.5):
    NF[0] += 1
    d.add_picture(os.path.join(FIG, fn), width=Inches(w)); p = d.paragraphs[-1]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
    P(f'Figure {NF[0]}. {caption}', size=9, space=10, justify=True)
def BOX(title, text, fill='F3E3E3'):
    t = d.add_table(rows=1, cols=1); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]; c.text = ''; shade(c, fill)
    p = c.paragraphs[0]; r = p.add_run(title + ' '); r.bold = True; r.font.size = Pt(10); r2 = p.add_run(mf(text)); r2.font.size = Pt(9.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    LOG.append((SECTION['name'], title + ' ' + text)); d.add_paragraph().paragraph_format.space_after = Pt(2)
