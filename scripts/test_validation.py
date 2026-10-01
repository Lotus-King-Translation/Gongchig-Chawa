#!/usr/bin/env python3
"""Corrupt copies, never live editions; prove fixed release invariants reject them."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from import_legacy import ROOT, decode
from validate_project import project
from validate_paired import validate


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/'project'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','__pycache__'))
        self.source=(self.root/'paired/source.md').read_text()
        self.english=(self.root/'paired/translation.md').read_text()

    def tearDown(self):
        self.temp.cleanup()

    def change(self,path,old,new):
        f=self.root/path
        text=f.read_text()
        self.assertIn(old,text)
        f.write_text(text.replace(old,new,1))

    def test_baseline(self):
        self.assertEqual(project(self.root)['anchors'],206)

    def test_affix_marker_regression(self):
        self.assertEqual(decode('རྡོ་རྗེ་␣འི་ གསུང་ ། །'),'རྡོ་རྗེའི་གསུང་། །')
        self.assertEqual(decode('ངོ་  བོ་'),'ངོ་ བོ་')
        with self.assertRaises(ValueError):decode('ཀ␣')

    def test_missing_format(self):
        with self.assertRaises(ValueError):validate(self.source.replace(' | format: h1','',1),self.english)

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):validate(self.source.replace('format: h1','format: heading',1),self.english)

    def test_duplicate_metadata(self):
        with self.assertRaises(ValueError):validate(self.source.replace('format: h1','format: h1 | format: verse',1),self.english)

    def test_duplicate_translation_pair(self):
        with self.assertRaises(ValueError):validate(self.source,self.english.replace('GC-000002','GC-000001',1))

    def test_omitted_closing_pair(self):
        with self.assertRaises(ValueError):validate(self.source,self.english.split('<!-- pair: GC-000173')[0])

    def test_wrong_source_edition(self):
        with self.assertRaises(ValueError):validate(self.source,self.english.replace('source-edition: gongchig-provisional-source-v1','source-edition: unset',1))

    def test_changed_tibetan(self):
        self.change('paired/source.md','དམ་ཆོས་','དམ་ཆས་')
        with self.assertRaises(ValueError):project(self.root)

    def test_omitted_anchor(self):
        f=self.root/'paired/pairing.json';rows=json.loads(f.read_text());rows[-1]['anchors'].pop();f.write_text(json.dumps(rows))
        with self.assertRaises(ValueError):project(self.root)

    def test_reordered_anchor(self):
        f=self.root/'paired/pairing.json';rows=json.loads(f.read_text());rows[3]['anchors'].reverse();f.write_text(json.dumps(rows))
        with self.assertRaises(ValueError):project(self.root)

    def test_changed_archive(self):
        self.change('source/legacy/root/001.txt','དམ་ཆོས་','དམ་ཆས་')
        with self.assertRaises(ValueError):project(self.root)

    def test_dropped_annotation(self):
        f=self.root/'translations/notes.json';rows=json.loads(f.read_text());rows.pop();f.write_text(json.dumps(rows))
        with self.assertRaises(ValueError):project(self.root)

    def test_changed_glossary(self):
        self.change('glossary/expanded_tibetan_english_glossary.csv','Ordinary mind','Mind')
        with self.assertRaises(ValueError):project(self.root)

    def test_promoted_proposal(self):
        f=self.root/'translations/PROPOSED-GLOSSARY.csv'
        import csv
        with f.open() as h:reader=csv.DictReader(h);fields=reader.fieldnames;rows=list(reader)
        rows[0]['Status and open questions']='Established'
        with f.open('w') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
        with self.assertRaises(ValueError):project(self.root)

    def test_unsigned_final_gate(self):
        (self.root/'translations/SIGNOFF.json').unlink(missing_ok=True)
        with self.assertRaises((ValueError,FileNotFoundError)):project(self.root,final=True)


    def test_complete_pair_identity(self):
        source,english=validate(self.source,self.english)
        self.assertEqual(source[0][0],'GC-000001')
        self.assertEqual(english[-1][0],'GC-000173')

    def test_wrong_note_slug(self):
        self.change('paired/translation.md','NOTES.md#f001','NOTES.md#wrong')
        with self.assertRaises(ValueError):project(self.root)

    def test_misplaced_note(self):
        f=self.root/'paired/translation.md';text=f.read_text();link='[F001](../translations/NOTES.md#f001)'
        self.assertIn(link,text);f.write_text(text.replace(link,'',1)+' '+link)
        with self.assertRaises(ValueError):project(self.root)

    def test_changed_note_body(self):
        self.change('translations/NOTES.md','- Issue/evidence:','- Missing explanation:')
        with self.assertRaises(ValueError):project(self.root)

    def test_false_scan_coverage(self):
        f=self.root/'paired/coverage.json';rows=json.loads(f.read_text());rows[0]['physical_witness_verified']=True;f.write_text(json.dumps(rows))
        with self.assertRaises(ValueError):project(self.root)

    def alter_usage(self,key,value):
        import csv
        f=self.root/'translations/USAGE.csv'
        with f.open() as h:reader=csv.DictReader(h);fields=reader.fieldnames;rows=list(reader)
        rows[0][key]=value
        with f.open('w') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)

    def test_wrong_usage_quote(self):
        self.alter_usage('exact_tibetan','མེད་མེད་མེད')
        with self.assertRaises(ValueError):project(self.root)

    def test_unknown_usage_category(self):
        self.alter_usage('category','Automatically approved')
        with self.assertRaises(ValueError):project(self.root)

    def test_empty_translation_edition(self):
        self.change('paired/translation.md','translation-edition: gongchig-working-translation-v0.1','translation-edition: ')
        with self.assertRaises(ValueError):project(self.root)

    def test_empty_source_provenance(self):
        with self.assertRaises(ValueError):validate(self.source.replace('source: U00001','source: ',1),self.english)

    def signoff(self):
        from import_legacy import digest
        paths=['paired/source.md','paired/translation.md','paired/pairing.json','translations/notes.json','translations/QC.md','translations/USAGE.csv','translations/PROPOSED-GLOSSARY.csv','source/PROVENANCE.json','source/TEMPLATE.json','editions/REGISTER.csv','DECISIONS.md']
        return {'release_class':'working_draft_with_review_flags','independent_agent_qc_complete':True,'artifact_sha256':{p:digest(self.root/p) for p in paths}}

    def test_string_false_signoff(self):
        data=self.signoff();data['independent_agent_qc_complete']='false'
        (self.root/'translations/SIGNOFF.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):project(self.root,final=True)

    def test_missing_terminology_signoff(self):
        data=self.signoff();del data['artifact_sha256']['translations/USAGE.csv']
        (self.root/'translations/SIGNOFF.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):project(self.root,final=True)

    def test_valid_signoff(self):
        (self.root/'translations/SIGNOFF.json').write_text(json.dumps(self.signoff()))
        self.assertTrue(project(self.root,final=True)['final_mode'])


if __name__=='__main__':
    unittest.main(verbosity=2)
