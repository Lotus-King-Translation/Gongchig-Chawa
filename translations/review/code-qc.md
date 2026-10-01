# Gongchig structural-code QC

Scope: read-only review of `scripts/import_legacy.py`, `validate_paired.py`, `validate_project.py`, `test_validation.py`, `build_support.py`, `paired/pairing.json`, and `source/README.md` in `work/gongchig-candidate`; relevant status, decisions, contract, register, format, provenance and validation README also inspected. No candidate files were edited. The candidate is currently a staging directory, not a Git checkout; Git status/HEAD/remote checks are therefore unavailable for it.

Outcome: one execution blocker and five material validation gaps. These findings concern structural correctness and preservation, not semantic translation certification. Evidence is in `work/code-qc-evidence.json`; `work/code_qc_probe.py` constructs and deletes a synthetic project copy and applies the pair-regex correction **in runtime memory only** to isolate later findings. Its synthetic English is deliberately not a translation and must not enter the candidate.

## C01 — P1: the pair regex cannot parse the actual canonical files

- Location: `scripts/validate_paired.py:9`, then `pairs()` lines 31–43.
- Expression `r'<!-- pair: ([^|>]+?)(.*?) -->'` gives `group(1) == 'G'` and `group(2) == 'C-000001 | source: ...'` for a valid `GC-000001` marker. Both capturing groups are lazy, and nothing forces the first to consume the ID.
- Reproduced on the real canonical source: `invalid or duplicate pair metadata: G`. This blocks `validate_paired`, `validate_project`, and `build_support`.
- Minimal correction: make the first group greedy: `r'<!-- pair: ([^|>]+)(.*?) -->'`. A delimiter-constrained alternative is also acceptable.
- Regression: parse one valid source marker and one valid translation marker and assert the full ID. Existing baseline must pass before relying on corruption-test rejections; otherwise negative fixtures can fail for this unrelated parser error.

## C02 — P1: note linkage can be broken or moved away from its occurrence and still pass

- Location: `scripts/validate_project.py:52–58`.
- The validator collects only a **global set of displayed note IDs**. It discards the target slug and source pair containing each link.
- After the isolated regex correction, both changes pass `project()`: `[FTEST](../translations/NOTES.md#wrong-target)`; moving the only FTEST link from its required first pair to the final pair.
- Impact: a source problem or provisional term can lose its visible annotation at the affected occurrence even though the gate reports all note records linked.
- Minimal correction: parse `(display_id, target_slug)` inside each already-parsed translation pair; require `target_slug == display_id.lower()` and a matching rendered note. Build expected links from `notes[*].pairs` **plus each USAGE row with a note ID** so repeated provisional occurrences are protected. Require each expected pair/note link to occur. Other intentional cross-references may remain permitted.
- Add separate wrong-slug and moved-occurrence corruption fixtures.

## C03 — P2: generated notes and coverage can contradict authored evidence

- Location: `scripts/validate_project.py:28–33,55–58`; `scripts/build_support.py:10–32`; root `README.md` validation command list.
- `project()` checks note headings but not rendered note contents. Coverage checks only anchor order, pair and `status`, not context, review-note links, resolution or physical-witness claims. The README does not invoke the existing support-reconstruction check.
- Reproduced: delete every explanatory field from NOTES.md while retaining `## FTEST`; delete the coverage review flag and change `physical_witness_verified` to true. `project()` still passes.
- Minimal correction: call `build_support.render(root)` in the project gate and compare every returned output with its saved content. This reuses the existing deterministic renderer and checks NOTES.md, coverage.json and bilingual.md together. Alternatively make the documented release command sequence explicitly run this check, but integrating it into the project gate prevents accidental omission.
- Add one altered-note-body fixture and one altered-coverage flag fixture. Keep coverage as “represented,” not “resolved”; this check cannot certify semantic completeness.

## C04 — P2: usage records need exact-source and schema validation

- Location: `scripts/validate_project.py:59–66`.
- Rows are checked only for known anchor/pair, existing note ID and a note for provisional category. Exact Tibetan, category vocabulary, and the rest of the usage schema are not checked.
- Reproduced: replace U00001 usage `exact_tibetan` with `མེད་མེད་མེད`, which does not occur there; the project still passes.
- Minimal correction: require the intended usage header and essential fields; check nonempty exact Tibetan is a substring of the designated anchor (or a deliberately supported multi-anchor construction), validate category against the documented set, and retain current note checks. English lexical correctness remains a review task; do not pretend a substring test establishes it.
- Add an absent-Tibetan-quotation fixture and an unknown-category fixture.

## C05 — P2: empty edition values pass metadata validation

- Location: `scripts/validate_paired.py:68–71`; metadata-presence logic at lines 44–49.
- `None` and `unset` are rejected, but the empty string is accepted. A blank `translation-edition:` passes the whole project gate. In the standalone validator, jointly blank source/source-reference editions and blank `source:` / `role:` values also pass because the keys exist.
- Minimal correction: reject `not value` as well as `unset` for required editions and required pair-provenance/role values. Preserve the existing fixed-source comparison in `project()`, which already prevents altered source headers or metadata from passing the whole-project gate.
- Add blank-translation-edition and empty-source-provenance tests. Missing-format, unsupported-format and duplicate-format tests remain useful after C01 is corrected.

## C06 — P2: final signoff accepts string false and leaves required terminology evidence unpinned

- Location: `scripts/validate_project.py:81–89`.
- `not signoff.get('independent_agent_qc_complete')` treats the JSON string `"false"` as complete. Reproduced with valid fixture hashes: final mode accepts it.
- The minimum hash set includes source, translation, pairing, notes.json and QC.md but omits USAGE.csv and PROPOSED-GLOSSARY.csv. The final gate therefore permits a nominally fixed release whose terminology-use/proposal evidence changes without invalidating its minimal signoff.
- Minimal correction: require `is True`; require hash coverage for authored terminology-use/proposal inputs and the source/template provenance/register records used to establish authority. Generated projections can be rebuilt under C03, or also hashed if the release publishes them. This does not require cryptographic user signatures or any new approval workflow.
- Add a string-false signoff fixture and a missing-terminology-hash fixture. Continue describing this as an agent-reviewed working draft with flags, never final human certification.

## Source-format and reconstruction assessment

- The actual read-only importer passes: 206 exact decoded source strings, 173 pairs, 134 artificial affix clusters removed, 1,364 artificial ASCII token spaces removed, 208 native spaces restored, and zero Tibetan textual emendations.
- The map has exactly the stated layout: one h1, one h2, eight prose pairs, 163 verse pairs. Ordered anchor flattening covers U00001–U00206 exactly once. The duplicated U00132/U00133 is preserved; the absent fifth-section conclusion is not invented. No source-format boundary error was found by inspecting this map.
- `project()` compares the entire canonical source with reconstruction, including fixed provisional header, edition, source commit, provenance markers and format metadata. This is stronger than the generic standalone paired validator and should remain authoritative for release.
- The format grouping is itself authored in pairing.json. Reconstruction cannot independently discover a wrong literary classification if that map is deliberately changed and all projections regenerated; the explicit review and final hash of the pairing map provide that protection. Do not describe archive-byte checks as an independent judgment that prose/verse classifications are correct.
- `build_support` currently ignores `format` when rendering bilingual Markdown. Native newlines inside multi-line verses may collapse when ordinary Markdown is rendered. Optional small presentation improvement: emit hard line breaks for verse and mapped heading levels for h1/h2/h3 while keeping canonical strings unchanged.

## Test/claim boundaries

The existing suite has a useful positive project baseline and targeted corruption cases, including lost closing material, changed archive bytes, glossary modification and unsigned-final rejection. It currently fails at C01 and does not cover C02–C06. The reported successful probes are **demonstrations of accepted corrupt fixtures**, not passing production validation. Full production translation validation was intentionally not attempted while the coordinator was assembling its files. The validator's explicit `semantic_certification: not provided by this structural validator` is correct and should remain. Prefer “represented anchors” to “translated anchors” in mechanical counts if the latter could be read as a semantic claim.
