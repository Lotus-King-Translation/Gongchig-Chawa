# Gongchig-Chawa

An annotated, glossary-controlled English working translation of the supplied Tibetan Gongchig verse text, based on the Lotus King Tibetan project template. **Golden-edition work is explicitly skipped by the project owner.** The source is a fixed provisional electronic transcript, not a verified critical or golden edition.

Released as [gongchig-working-v0.1.0](https://github.com/Lotus-King-Translation/Gongchig-Chawa/releases/tag/gongchig-working-v0.1.0); [publication receipt](translations/PUBLICATION.json). Two source spans remain partially unresolved and all proposed terminology remains subject to human review.

## Read

- [Tibetan source](paired/source.md) and [English translation](paired/translation.md): 173 matching reader pairs covering all 206 supplied source units.
- [Translation notes](translations/NOTES.md): source problems, interpretive supplies and unresolved terminology.
- [Independent agent QC](translations/QC.md), [coverage](paired/coverage.json), [usage records](translations/USAGE.csv), [proposed terminology](translations/PROPOSED-GLOSSARY.csv).
- [Current status](PROJECT-STATUS.md), [decisions](DECISIONS.md), [translation handoff](translations/HANDOFF.md).

The rough reference English is attributed in its PO header to Tenzin Norgyal (2023) and retained unchanged in [the archive](source/legacy/wip/en/001.po). It informed the new translation but does not override the Tibetan or the template glossary. Every token-markup transformation is reversible to the archived root transcript. The duplicated Tibetan at U00133 is retained and annotated; the missing section-five conclusion is not invented from English.

## Provenance and method

Template: [tibetan-text-project-template, f6431c2](https://github.com/Lotus-King-Translation/tibetan-text-project-template/tree/f6431c25c7c9fa852c404b8cd3e0e3cdeae1178f). Source: [legacy Gongchig, 1d815bf](https://github.com/Lotus-King-Translation/Gongchig/tree/1d815bff0e12b8eacea9d6776b89b34f82ef038b). See [source provenance](source/README.md) and [register](editions/REGISTER.csv). The supplied link's target identifies Gongchig; its visible Gongchig-Drelwa label was not treated as a different source.

Contributors read [AGENTS.md](AGENTS.md), then [status](PROJECT-STATUS.md), [standard](guidelines/tibetan_translation_standard_v2.md), [glossary](glossary/expanded_tibetan_english_glossary.csv) and [format](FORMAT.md). New terminology remains proposed. A working-draft release does not certify final human editing or resolve source questions.

## Validate

Python 3, standard library only:

```sh
python3 scripts/import_legacy.py
python3 scripts/validate_paired.py
python3 scripts/validate_project.py
python3 scripts/build_support.py
python3 scripts/test_validation.py
python3 scripts/validate_project.py --final
```

`paired/source.md` is frozen against the archival reconstruction. `paired/translation.md` is the canonical authored English. `paired/pairing.json` freezes reader segmentation; `source/anchors.json` and `source/normalization.json` are generated audit projections. Translation drafts are archived review evidence, not a competing editable English authority. Supporting coverage, notes and usage records must stay synchronized with canonical edits. The release signoff pins hashes and becomes invalid if any signed content changes.
