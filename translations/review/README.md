# Review evidence

`first-*`, `middle-*` and `last-*` preserve the original source packages, translator outputs and Proposed tables. Each `qc-*.json` is a separate agent's review of a package they did not translate. Original run-header paths beginning `work/` map to the same-basename snapshots in this directory; the template glossary/guidance map to the unchanged project resources. SHA-256 records identify exact reviewed versions.

`COORDINATOR-CHANGES.json` records later English integration changes. Current canonical English is `../../paired/translation.md`; these archived drafts are evidence, not parallel authoring surfaces. Current notes and usages are in `../notes.json` and `../USAGE.csv`. Later documentation additions are summarized in `../QC.md`.

`code-qc.md` records the pre-repair structural review. Its obsolete-code findings are retained as history; current validation receipts and corruption tests establish whether repairs passed. Synthetic probe translations used during that audit are deliberately excluded from this project.
