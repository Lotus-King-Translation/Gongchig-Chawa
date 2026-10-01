#!/usr/bin/env python3
"""Reconstruct the fixed provisional source; never emend Tibetan readings."""
import argparse
import ast
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITION = 'gongchig-provisional-source-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_po(path):
    """Read this archived singular PO subset; fail on unsupported syntax."""
    rows, row, active = [], {}, None
    for num, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            if row.get('msgctxt'):
                rows.append(row)
            row, active = {}, None
        elif line.startswith('#'):
            continue
        elif line.startswith(('msgctxt ', 'msgid ', 'msgstr ')):
            active, literal = line.split(' ', 1)
            if active in row:
                raise ValueError(f'duplicate PO field at {path}:{num}')
            row[active] = ast.literal_eval(literal)
            if active == 'msgctxt':
                row['po_line'] = num
        elif line.startswith('"') and active:
            row[active] += ast.literal_eval(line)
        else:
            raise ValueError(f'unsupported PO syntax at {path}:{num}')
    if row.get('msgctxt'):
        rows.append(row)
    if any(not {'msgctxt', 'msgid', 'msgstr'} <= r.keys() for r in rows):
        raise ValueError('incomplete PO entry')
    return rows


def decode(text):
    # Forward script inserted the tsheg WITH U+2423; removing only U+2423 is wrong.
    text = text.replace('་␣', '').replace(' ', '').replace(' ', ' ')
    if '␣' in text or ' ' in text:
        raise ValueError('unrecognized token marker')
    return text


def reconstruct(root=ROOT):
    archived = root / 'source/legacy'
    with (root / 'editions/REGISTER.csv').open() as handle:
        records = list(csv.DictReader(handle))
    for record in records:
        if digest(root / record['path']) != record['sha256']:
            raise ValueError('archival hash mismatch: ' + record['path'])
    en = read_po(archived / 'wip/en/001.po')
    bo = read_po(archived / 'wip/bo/001.po')
    if len(en) != 206 or len({r['msgctxt'] for r in en}) != 206:
        raise ValueError('expected 206 unique legacy contexts')
    if [(r['msgctxt'], r['msgid']) for r in en] != [(r['msgctxt'], r['msgid']) for r in bo]:
        raise ValueError('Tibetan and English PO contexts or source differ')
    if any(r['msgstr'] for r in bo) or any(not r['msgstr'].strip() for r in en):
        raise ValueError('unexpected reference translation coverage')
    plain = archived / 'root/001.txt'
    if plain.read_bytes() != (archived / 'root/001_v2.txt').read_bytes():
        raise ValueError('legacy root copies differ')
    lines = [s.strip() for s in plain.read_text().splitlines() if s.strip()]
    if [decode(r['msgid']) for r in en] != lines:
        raise ValueError('decoded PO does not reproduce plain source')
    anchors = [{'id':f'U{i:05d}', 'context':r['msgctxt'], 'po_line':r['po_line'],
                'encoded':r['msgid'], 'text':decode(r['msgid']), 'reference_en':r['msgstr']}
               for i, r in enumerate(en, 1)]
    pairing = json.loads((root / 'paired/pairing.json').read_text())
    if [a for pair in pairing for a in pair['anchors']] != [a['id'] for a in anchors]:
        raise ValueError('pairing omits, duplicates or reorders source anchors')
    if len({p['id'] for p in pairing}) != len(pairing):
        raise ValueError('duplicate pair identity')
    by_id = {a['id']: a for a in anchors}
    header = ('---\nschema: paired-text/2\ntext-id: gongchig\nedition: '+EDITION+
              '\nlanguage: bo\nsource-state: provisional\n'
              'source-commit: 1d815bff0e12b8eacea9d6776b89b34f82ef038b\n'
              'golden-release: none\n---\n\n')
    chunks = []
    for pair in pairing:
        if pair['format'] not in {'prose','verse','h1','h2','h3'}:
            raise ValueError('invalid structural format')
        marker = f"<!-- pair: {pair['id']} | source: {' '.join(pair['anchors'])} | role: {pair['role']} | format: {pair['format']} -->"
        # One source line per archival anchor; no punctuation/Unicode normalization.
        chunks.append(marker+'\n'+'\n'.join(by_id[a]['text'] for a in pair['anchors']))
    report = {'edition':EDITION, 'anchors':len(anchors), 'pairs':len(pairing),
              'format_counts':dict(Counter(p['format'] for p in pairing)),
              'affix_markers_removed':sum(r['msgid'].count('་␣') for r in en),
              'artificial_ascii_spaces_removed':sum(r['msgid'].count(' ') for r in en),
              'original_spaces_restored':sum(r['msgid'].count(' ') for r in en),
              'root_strings_exactly_reconstructed':206,
              'root_comparison':'strip outer line whitespace only; internal spaces unchanged',
              'source_textual_emendations':0, 'full_scan_proofreading':False,
              'independent_witness_collation':False,
              'known_duplicate':['U00132','U00133']}
    return anchors, header+'\n\n'.join(chunks)+'\n', report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write initial fixed source projections')
    args=parser.parse_args()
    anchors, source, report=reconstruct()
    values={'source/anchors.json':json.dumps(anchors,ensure_ascii=False,indent=2)+'\n',
            'source/normalization.json':json.dumps(report,ensure_ascii=False,indent=2)+'\n',
            'paired/source.md':source}
    for rel, content in values.items():
        path=ROOT/rel
        if args.write:
            path.write_text(content,encoding='utf-8')
        elif path.read_text(encoding='utf-8') != content:
            raise ValueError('source reconstruction mismatch: '+rel)
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    main()
