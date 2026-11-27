# paper/: scientific write-up of the epilepsy testbed study

**Speculative modeling / architecture testbed only. No clinical claims, not medical advice.**

- `Epilepsy_Seizure_Dynamics_Relational_Simulation_Study.pdf`: the paper (PDF)
- `Epilepsy_Seizure_Dynamics_Relational_Simulation_Study.docx`: the same paper (Word)
- `analysis_epi.py`: reads `../data/*` and draws figures 1-7 and 9 (figure 8 is repository chart 07)
- `build_part1.py` ... `build_part4.py`: python-docx manuscript builder (concatenated by `mk.sh`); every number in the text is computed from `../data/*`
- `mk.sh`: rebuild (`./mk.sh`; needs python-docx, matplotlib, pandas, scipy and LibreOffice `soffice`)
- `figures/`: figures used in the paper; `style_audit.json`: framework-term and unused-reference audit

Pipeline: python-docx -> DOCX -> LibreOffice -> PDF (same as the metastasis study write-up).
