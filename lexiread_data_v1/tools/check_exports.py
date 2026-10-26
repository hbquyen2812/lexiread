"""Cross-check normalized foreign keys and CSV/JSON consistency."""
import csv
import hashlib
import json
from pathlib import Path
from export import ROOT,TABLES

def main():
    n=json.loads((ROOT/'data'/'normalized.json').read_text(encoding='utf-8'))['tables']
    ids={t:{r['id'] for r in rows} for t,rows in n.items()}
    errors=[]; comparisons=0
    refs={'lessons':{'dataset_id':'datasets'},'lesson_sources':{'lesson_id':'lessons','source_id':'sources'},'passages':{'lesson_id':'lessons'},'senses':{'word_id':'words'},'lesson_vocabulary':{'lesson_id':'lessons','passage_id':'passages','sense_id':'senses'},'questions':{'lesson_id':'lessons','vocabulary_context_id':'lesson_vocabulary'}}
    for t,columns in refs.items():
        for r in n[t]:
            for col,parent in columns.items():
                if r[col] is not None and r[col] not in ids[parent]: errors.append(f'{t}/{r["id"]}: invalid {col}')
    pm={r['id']:r for r in n['passages']};vm={r['id']:r for r in n['lesson_vocabulary']}
    for v in n['lesson_vocabulary']:
        if pm[v['passage_id']]['lesson_id']!=v['lesson_id']:errors.append(f'{v["id"]}: cross-lesson context')
    for q in n['questions']:
        for e in q['evidence']:
            p=pm[e['passage_id']]
            if p['lesson_id']!=q['lesson_id'] or p['text'][e['start_char']:e['end_char']]!=e['quote']:
                errors.append(f'{q["id"]}: invalid evidence span')
        if q['vocabulary_context_id'] and vm[q['vocabulary_context_id']]['lesson_id']!=q['lesson_id']:
            errors.append(f'{q["id"]}: cross-lesson vocabulary')
    for t,rows in n.items():
        with (ROOT/'data'/'csv'/f'{t}.csv').open(encoding='utf-8',newline='') as f: back=list(csv.DictReader(f))
        if len(back)!=len(rows):errors.append(f'{t}: CSV row count mismatch');continue
        for original,restored in zip(rows,back):
            for col,typ in TABLES[t]:
                val=restored[col]
                if typ.startswith('jsonb'):val=json.loads(val)
                elif typ.startswith('integer'):val=int(val) if val else None
                elif original[col] is None and val=='':val=None
                if val!=original[col]:errors.append(f'{t}/{original["id"]}/{col}: CSV round-trip mismatch')
                comparisons+=1
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    for filename,entry in manifest['files'].items():
        p=ROOT/filename
        if hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append(f'{filename}: checksum mismatch')
    report={'errors':errors,'csv_cells_compared':comparisons,'tables_checked':len(n),'checks':['normalized foreign keys','same-lesson references','evidence offsets','CSV JSON round-trip','SHA-256 manifest'],'postgresql_execution':'not_run_no_postgresql_server_available','sql_note':'Schema and seed generated for PostgreSQL; database execution has not been claimed.'}
    (ROOT/'docs'/'export_validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
