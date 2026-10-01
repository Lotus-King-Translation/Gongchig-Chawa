#!/usr/bin/env python3
"""Validate paired-text/2, with an explicit provisional-source exception."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FORMATS = {'prose', 'verse', 'h1', 'h2', 'h3'}
PAIR = re.compile(r'<!-- pair: ([^|>]+)(.*?) -->')


def front_matter(text):
    if not text.startswith('---\n'):
        raise ValueError('missing front matter')
    end=text.find('\n---\n',4)
    if end<0:
        raise ValueError('unterminated front matter')
    values={}
    for line in text[4:end].splitlines():
        key,sep,value=line.partition(':')
        if not sep or key.strip() in values:
            raise ValueError('invalid or duplicate front matter field')
        values[key.strip()]=value.strip()
    return values


def pairs(text, source_side):
    rows=[]
    seen=set()
    matches=list(PAIR.finditer(text))
    for i,match in enumerate(matches):
        ident=match.group(1).strip()
        if ident in seen:
            raise ValueError('duplicate pair ID: '+ident)
        seen.add(ident)
        metadata={}
        for piece in match.group(2).split('|'):
            if not piece.strip():
                continue
            key,sep,value=piece.strip().partition(':')
            if not sep or key.strip() in metadata:
                raise ValueError('invalid or duplicate pair metadata: '+ident)
            metadata[key.strip()]=value.strip()
        if source_side:
            provenance='source' if front_matter(text).get('source-state')=='provisional' else 'golden'
            if not {provenance,'role','format'} <= metadata.keys():
                raise ValueError('missing source metadata: '+ident)
            if any(not metadata[k] for k in (provenance,'role','format')):
                raise ValueError('empty source metadata: '+ident)
            if metadata['format'] not in ALLOWED_FORMATS:
                raise ValueError('unsupported source format: '+ident)
        elif metadata:
            raise ValueError('translation inherits source metadata; do not duplicate it')
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        body=text[match.end():end].strip()
        if not body:
            raise ValueError('empty pair: '+ident)
        rows.append((ident,metadata,body))
    if not rows:
        raise ValueError('empty paired edition')
    return rows


def validate(source,translation):
    sfm,tfm=front_matter(source),front_matter(translation)
    if sfm.get('schema')!='paired-text/2' or tfm.get('schema')!='paired-text/2':
        raise ValueError('incorrect paired schema')
    if not sfm.get('text-id') or sfm['text-id']=='unset' or sfm['text-id']!=tfm.get('text-id'):
        raise ValueError('text-id mismatch or unset')
    if sfm.get('edition') in (None,'','unset') or tfm.get('source-edition')!=sfm['edition']:
        raise ValueError('source edition mismatch or unset')
    if tfm.get('translation-edition') in (None,'','unset'):
        raise ValueError('translation edition missing')
    if sfm.get('language')!='bo' or tfm.get('language')!='en':
        raise ValueError('language mismatch')
    s,t=pairs(source,True),pairs(translation,False)
    if [r[0] for r in s]!=[r[0] for r in t]:
        raise ValueError('source/translation identities or order differ')
    return s,t


def main():
    s,t=validate((ROOT/'paired/source.md').read_text(),(ROOT/'paired/translation.md').read_text())
    print('paired-text/2 valid; pairs:',len(s))
    print('formats:',{f:sum(r[1]['format']==f for r in s) for f in sorted(ALLOWED_FORMATS)})


if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as e:
        print('PAIRED VALIDATION FAILED:',e,file=sys.stderr)
        raise SystemExit(1)
