#!/usr/bin/env python3
"""Validate frozen source, paired coverage, notes, proposals and release hashes."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

from import_legacy import EDITION, ROOT, digest, reconstruct
from validate_paired import validate
from build_support import render


def project(root=ROOT, final=False):
    anchors, expected_source, normalization = reconstruct(root)
    source=(root/'paired/source.md').read_text()
    translation=(root/'paired/translation.md').read_text()
    if source!=expected_source:
        raise ValueError('canonical source differs from exact archived reconstruction')
    expected=json.dumps(anchors,ensure_ascii=False,indent=2)+'\n'
    if (root/'source/anchors.json').read_text()!=expected:
        raise ValueError('anchor projection changed')
    if json.loads((root/'source/normalization.json').read_text())!=normalization:
        raise ValueError('normalization receipt changed')
    sp,tp=validate(source,translation)
    if len(sp)!=173:
        raise ValueError('expected 173 frozen reading pairs')
    coverage=json.loads((root/'paired/coverage.json').read_text())
    if [r['anchor'] for r in coverage]!=[a['id'] for a in anchors]:
        raise ValueError('coverage loses or reorders an anchor')
    anchor_pairs={a:p['id'] for p in json.loads((root/'paired/pairing.json').read_text()) for a in p['anchors']}
    if any(r['pair']!=anchor_pairs[r['anchor']] or r['status']!='represented' for r in coverage):
        raise ValueError('coverage pair mapping or status invalid')
    notes=json.loads((root/'translations/notes.json').read_text())
    ids={n['id'] for n in notes}
    if len(ids)!=len(notes):
        raise ValueError('duplicate note ID')
    required={'id','anchors','pairs','exact_tibetan','category','problem','working_treatment','uncertainty','review_action'}
    by_id={a['id']:a['text'] for a in anchors}
    for n in notes:
        if not required<=n.keys() or any(not n[k] for k in required):
            raise ValueError('incomplete annotation: '+n.get('id','?'))
        if any(a not in by_id for a in n['anchors']):
            raise ValueError('unknown note anchor')
        if any(p!=anchor_pairs[a] for a,p in zip(n['anchors'],n['pairs'])):
            raise ValueError('note pair provenance mismatch')
        if len(n['anchors'])!=len(n['pairs']):
            raise ValueError('note anchor/pair lengths differ')
        if not any(n['exact_tibetan'] in by_id[a] for a in n['anchors']):
            if n['exact_tibetan'] not in '\n'.join(by_id[a] for a in n['anchors']):
                raise ValueError('note quotation not exact at stated anchors: '+n['id'])
    for ident, _, body in tp:
        expected_ids={n['id'] for n in notes if ident in n['pairs']}
        found={}
        for note_id,target in re.findall(r'\[([A-Z][A-Z0-9-]*)\]\(([^)]+)\)',body):
            if target != '../translations/NOTES.md#'+note_id.lower():
                raise ValueError('wrong annotation target: '+note_id)
            found[note_id]=target
        if set(found)!=expected_ids:
            raise ValueError('annotation missing or attached to wrong pair: '+ident)
    linked=set(re.findall(r'\[([A-Z][A-Z0-9-]*)\]\(\.\./translations/NOTES\.md#[a-z0-9-]+\)',translation))
    if linked!=ids:
        raise ValueError('translation note links and records differ: '+str(linked^ids))
    rendered=(root/'translations/NOTES.md').read_text()
    for n in notes:
        if '## '+n['id']+'\n' not in rendered:
            raise ValueError('missing rendered annotation: '+n['id'])
    with (root/'translations/USAGE.csv').open() as handle:
        rows=list(csv.DictReader(handle))
    usage_fields={'anchor','pair','exact_tibetan','canonical_entry','english','category','evidence','note_id'}
    for r in rows:
        if set(r)!=usage_fields or not all(r[k] for k in usage_fields-{'canonical_entry','note_id'}):
            raise ValueError('usage schema or required content missing')
        if r['anchor'] not in by_id or r['pair']!=anchor_pairs[r['anchor']]:
            raise ValueError('usage source mapping invalid')
        if r['category'] not in {'Canonical','Grammatical','Approved exception','Provisional'}:
            raise ValueError('unsupported usage category')
        if r['exact_tibetan'] not in by_id[r['anchor']]:
            raise ValueError('usage quotation not exact at stated anchor')
        if r['note_id'] and r['note_id'] not in ids:
            raise ValueError('usage note missing')
        if r['category'].lower().startswith('provisional') and not r['note_id']:
            raise ValueError('unannotated provisional usage')
    with (root/'glossary/expanded_tibetan_english_glossary.csv').open() as f:
        glossary=list(csv.DictReader(f))
    with (root/'translations/PROPOSED-GLOSSARY.csv').open() as f:
        reader=csv.DictReader(f); fields=reader.fieldnames; proposals=list(reader)
    if fields!=list(glossary[0]) or len(glossary)!=222:
        raise ValueError('glossary schema or established row count changed')
    if any('Proposed' not in r['Status and open questions'] for r in proposals):
        raise ValueError('unapproved proposal activation')
    baseline=json.loads((root/'source/TEMPLATE.json').read_text())
    for rel,sha in baseline['preserved_files'].items():
        if digest(root/rel)!=sha:
            raise ValueError('governing template resource changed: '+rel)
    if re.search(r'\b(?:TODO|TBD|TRANSLATION PENDING)\b',translation):
        raise ValueError('unfinished translation placeholder')
    for rel,value in render(root).items():
        if (root/rel).read_text()!=value:
            raise ValueError('support projection differs: '+rel)
    if final:
        signoff=json.loads((root/'translations/SIGNOFF.json').read_text())
        if signoff.get('release_class')!='working_draft_with_review_flags' or signoff.get('independent_agent_qc_complete') is not True:
            raise ValueError('final draft signoff absent')
        for rel,sha in signoff['artifact_sha256'].items():
            if digest(root/rel)!=sha:
                raise ValueError('signed artifact changed: '+rel)
        if not {'paired/source.md','paired/translation.md','paired/pairing.json','translations/notes.json','translations/QC.md','translations/USAGE.csv','translations/PROPOSED-GLOSSARY.csv','source/PROVENANCE.json','source/TEMPLATE.json','editions/REGISTER.csv','DECISIONS.md'} <= signoff['artifact_sha256'].keys():
            raise ValueError('incomplete signoff hash coverage')
    return {'source_edition':EDITION,'anchors':206,'pairs':173,'represented_anchors':206,
            'notes':len(notes),'usage_records':len(rows),'proposed_rows':len(proposals),
            'source_textual_emendations':0,'source_exact':True,'final_mode':final,
            'semantic_certification':'not provided by this structural validator'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    print(json.dumps(project(final=args.final),indent=2))


if __name__=='__main__':
    main()
