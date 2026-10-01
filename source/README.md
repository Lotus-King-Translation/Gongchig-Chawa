# Source and provenance

The governing input is the Tibetan `msgid` sequence in archived `legacy/wip/en/001.po`, pinned in `PROVENANCE.json`. Its 206 context IDs and source strings exactly equal the Tibetan PO. Both raw root transcript copies are byte-identical. All original acquired bytes remain in `legacy/`; their SHA-256 and URLs are in `../editions/REGISTER.csv`.

`legacy/scripts/sentences_to_transifex.py` inserts an artificial tsheg plus `␣` at attached-particle boundaries, spaces between tokens, and ` ` for native spaces. The inverse is precisely:

```python
text.replace('་␣', '').replace(' ', '').replace(' ', ' ')
```

The historical exporters remove only `␣`, leaving 134 spurious tshegs across 108 units. This project removes the whole inserted cluster. All 206 decoded strings exactly reconstruct the root transcript after trimming only outer line whitespace. Internal native spaces, Tibetan spelling and punctuation remain unchanged; no Unicode normalization is applied.

`anchors.json` and `normalization.json` are generated provenance projections; `../paired/source.md` is their frozen canonical publication surface. `scripts/import_legacy.py` checks them without writing by default; `--write` is the documented initial reconstruction command. Pair structure is authored in `../paired/pairing.json` and frozen with the release.

This is a provisional electronic source, not a golden edition. In particular U00133 repeats U00132, whereas its historical English describes a fifth-section conclusion missing from the Tibetan. Both archival layers are retained; the working translation translates the duplicate and discloses the mismatch. See translation notes for other source queries.
