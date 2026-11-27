# UPDATE_SEQUENCE.md: the "redstone torch" update sequence

Source: `Operational_Update_Sequence.md` (Oroboro / metastatic-cascade-analysis). Implementation: `code/update_sequence.py`, copied from v4 with epilepsy probability and positive keys.

**Steps, on every accepted parameter change:**
1. **Quick fix:** stage the change.
2. **UPDATE ALL:** propagate it to dependents.
3. **Undo:** restore exactly; checked by hash.
4. **Timestamp:** PT.
5. **Do it again:** re-apply; must be identical.
6. **Syntax autocorrect ("redstone torch"):** clip probabilities to [0, 1] and positive keys to > 0, and record any corrections.

Every calibration proposal also passes through the torch.

**This run:**
- 193 best-iterate records and 4 final parameter-file writes in `data/update_sequence_log.jsonl`.
- All verified (exact undo, identical redo); 0 corrections or errors.
