# Translation record

The canonical authored English is `../paired/translation.md`; the source is the fixed provisional edition authorized by D001. Golden-edition work is skipped, not certified complete. The rough human reference is retained unchanged in REFERENCE.md and the original PO archive, attributed to Tenzin Norgyal (2023).

Read RUN.md, HANDOFF.md, QC.md and NOTES.md. `notes.json` is the authored annotation ledger; `USAGE.csv` records contextual and provisional usages. `PROPOSED-GLOSSARY.csv` contains 125 unapproved candidate records in the active eight-column structure; the established glossary is unchanged. `WORK-QUEUE.json` lists open review actions. `review/` preserves draft and independent-review snapshots, not competing editable translations.

`../scripts/build_support.py` deterministically checks NOTES.md, coverage.json and bilingual.md from the canonical files, pairing map and notes ledger; `--write` regenerates them. `SIGNOFF.json` pins the prepared working draft with explicit review flags. It does not imply a remote release or human certification.
