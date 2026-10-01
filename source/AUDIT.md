# Source audit — 2026-10-01

Independent source-audit agent examined the archived PO, root transcript and tokenization/export scripts before translation.

- Legacy commit: 1d815bff0e12b8eacea9d6776b89b34f82ef038b.
- 206 unique contexts; 206 nonempty English reference entries; Tibetan msgstr fields all empty.
- Tibetan and English msgid/context sequences identical.
- Exact inverse removes 134 artificial `་␣` clusters across 108 anchors and 1,364 token spaces, restoring 208 original spaces.
- All 206 decoded strings equal nonempty root/001.txt lines with outer whitespace trimmed; root/001_v2.txt is byte-identical.
- Native internal spaces at U00063 and U00096 remain.
- 205 unique Tibetan strings: U00132 and U00133 are identical.
- U00133 English describes section five's conclusion, absent from that Tibetan; no source restoration made.
- Source queries include the malformed U00001 title, U00116 གནས་ལུག, U00151 ཐམས་ལམ and U00157 རྒྱུ་མ.
- Opening titles/homage/stanzas, seven thematic sections, eight closing quatrains and final prose adaptation colophon are accounted for.
- Human reference attribution: Tenzin Norgyal, 2023, from the PO header.
- No scans inspected; no independent witnesses established; no claim of source authentication.
