#!/usr/bin/env python3
"""Rebuild/check support files from the canonical pairs and authored notes."""
import argparse
import json
from pathlib import Path
from import_legacy import ROOT
from validate_paired import pairs


def render(root=ROOT):
    notes=json.loads((root/'translations/notes.json').read_text())
    mapping=json.loads((root/'paired/pairing.json').read_text())
    anchor_pair={a:p['id'] for p in mapping for a in p['anchors']}
    anchors=json.loads((root/'source/anchors.json').read_text())
    note_by_anchor={a['id']:[] for a in anchors}
    text=['# Translation notes\n\nSource: gongchig-provisional-source-v1, legacy commit `1d815bff0e12b8eacea9d6776b89b34f82ef038b`. Each locator refers to the archived PO context and decoded anchor recorded in `../source/anchors.json`. These are working review flags, not approved glossary changes or Tibetan emendations.\n']
    for n in notes:
        for a in n['anchors']:note_by_anchor[a].append(n['id'])
        text.append(f"## {n['id']}\n\n- Location: {', '.join(n['anchors'])}; pairs {', '.join(dict.fromkeys(n['pairs']))}.\n- Exact Tibetan: {n['exact_tibetan']}\n- Category: {n['category']}.\n- Issue/evidence: {n['problem']}\n- Working treatment: {n['working_treatment']}\n- Uncertainty: {n['uncertainty']}\n- Review action: {n['review_action']}\n")
    coverage=[{'anchor':a['id'],'context':a['context'],'pair':anchor_pair[a['id']],
               'status':'represented','human_review_notes':note_by_anchor[a['id']],
               'resolution':'review_flags' if note_by_anchor[a['id']] else 'working_translation',
               'physical_witness_verified':False} for a in anchors]
    src=pairs((root/'paired/source.md').read_text(),True)
    eng=pairs((root/'paired/translation.md').read_text(),False)
    if [p[0] for p in src]!=[p[0] for p in eng]:raise ValueError('pair identities differ')
    bilingual=['# Gongchig — bilingual working draft\n\nGenerated from `source.md` and `translation.md`. Source is provisional; notes and proposed usages remain open for human review.\n']
    for (ident,meta,bo),(_,_,en) in zip(src,eng):
        if meta['format']=='verse':
            bo=bo.replace('\n','  \n');en=en.replace('\n','  \n')
        bilingual.append(f"## {ident}\n\n{bo}\n\n{en}\n")
    return {'translations/NOTES.md':'\n'.join(text),
            'paired/coverage.json':json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',
            'paired/bilingual.md':'\n'.join(bilingual)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    for rel,value in render().items():
        path=ROOT/rel
        if args.write:path.write_text(value,encoding='utf-8')
        elif path.read_text(encoding='utf-8')!=value:raise ValueError('support reconstruction differs: '+rel)
    print('support projections reproducible')


if __name__=='__main__':main()
