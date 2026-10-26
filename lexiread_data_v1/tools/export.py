"""Build normalized JSON, UTF-8 CSV, PostgreSQL schema/seed and manifest.

Usage: python tools/export.py
Edit data/lessons.json, then regenerate. No network or external packages.
"""
import collections
import copy
import csv
import hashlib
import json
import re
from pathlib import Path
from validate import validate
from grading import normalize_answer,word_count

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='lexiread_seed_v1'
DATASET_ID='lexiread_reading_vocab_20261026_v1'
TABLES={
 'datasets': [('id','text PRIMARY KEY'),('version','text NOT NULL'),('created_on','date NOT NULL'),('metadata','jsonb NOT NULL')],
 'sources': [('id','text PRIMARY KEY'),('title','text NOT NULL'),('publisher','text NOT NULL'),('url','text NOT NULL'),('details','jsonb NOT NULL')],
 'lessons': [('id','text PRIMARY KEY'),('dataset_id','text NOT NULL REFERENCES lexiread_seed_v1.datasets(id)'),('track','text NOT NULL'),('title_en','text NOT NULL'),('title_vi','text NOT NULL'),('cefr_estimate','text NOT NULL'),('age_min','integer NOT NULL'),('age_max','integer NOT NULL'),('topic','text NOT NULL'),('estimated_minutes','integer NOT NULL'),('exam_part','text NOT NULL'),('learning_objectives_vi','jsonb NOT NULL'),('instructions_en','text NOT NULL'),('publication_status',"text NOT NULL CHECK (publication_status IN ('draft','reviewed','published','archived'))"),('content_origin','text NOT NULL'),('passage_word_count','integer NOT NULL'),('metadata','jsonb NOT NULL')],
 'lesson_sources': [('id','text PRIMARY KEY'),('lesson_id','text NOT NULL REFERENCES lexiread_seed_v1.lessons(id)'),('source_id','text NOT NULL REFERENCES lexiread_seed_v1.sources(id)'),('relation','text NOT NULL')],
 'passages': [('id','text PRIMARY KEY'),('lesson_id','text NOT NULL REFERENCES lexiread_seed_v1.lessons(id)'),('label','text NOT NULL'),('title_en','text NOT NULL'),('text','text NOT NULL'),('position','integer NOT NULL'),('word_count','integer NOT NULL')],
 'words': [('id','text PRIMARY KEY'),('term','text NOT NULL'),('normalized_term','text NOT NULL'),('pos','text NOT NULL')],
 'senses': [('id','text PRIMARY KEY'),('word_id','text NOT NULL REFERENCES lexiread_seed_v1.words(id)'),('meaning_vi','text NOT NULL'),('definition_en','text NOT NULL')],
 'lesson_vocabulary': [('id','text PRIMARY KEY'),('lesson_id','text NOT NULL REFERENCES lexiread_seed_v1.lessons(id)'),('passage_id','text NOT NULL REFERENCES lexiread_seed_v1.passages(id)'),('sense_id','text NOT NULL REFERENCES lexiread_seed_v1.senses(id)'),('position','integer NOT NULL'),('cefr_estimate','text NOT NULL'),('context_quote','text NOT NULL'),('example_en','text NOT NULL'),('collocation','text NOT NULL'),('synonyms','jsonb NOT NULL'),('antonyms','jsonb NOT NULL'),('distractors_vi','jsonb NOT NULL')],
 'questions': [('id','text PRIMARY KEY'),('lesson_id','text NOT NULL REFERENCES lexiread_seed_v1.lessons(id)'),('vocabulary_context_id','text REFERENCES lexiread_seed_v1.lesson_vocabulary(id)'),('position','integer NOT NULL'),('category',"text NOT NULL CHECK (category IN ('reading_practice','vocabulary_practice'))"),('type','text NOT NULL'),('skill','text NOT NULL'),('prompt_en','text NOT NULL'),('options','jsonb NOT NULL'),('answer','jsonb NOT NULL'),('accepted_answers','jsonb NOT NULL'),('max_words','integer CHECK (max_words IS NULL OR max_words > 0)'),('evidence','jsonb NOT NULL'),('explanation_vi','text NOT NULL'),('difficulty','integer NOT NULL CHECK (difficulty BETWEEN 1 AND 5)'),('generation_method','text NOT NULL')]
}
CONSTRAINTS={
 'lessons':["CHECK (age_min > 0 AND age_max >= age_min)","CHECK (estimated_minutes > 0)","CHECK (cefr_estimate IN ('pre-A1','A1','A2','B1','B2','C1','C2'))"],
 'lesson_sources':['UNIQUE (lesson_id, source_id)'],
 'passages':['UNIQUE (lesson_id, label)','UNIQUE (lesson_id, position)','UNIQUE (id, lesson_id)'],
 'words':['UNIQUE (normalized_term, pos)'],
 'lesson_vocabulary':['UNIQUE (lesson_id, position)','UNIQUE (id, lesson_id)','FOREIGN KEY (passage_id, lesson_id) REFERENCES lexiread_seed_v1.passages(id, lesson_id)'],
 'questions':['UNIQUE (lesson_id, category, position)',"CHECK (jsonb_typeof(options) = 'array')","CHECK (jsonb_array_length(answer) = 1)",'FOREIGN KEY (vocabulary_context_id, lesson_id) REFERENCES lexiread_seed_v1.lesson_vocabulary(id, lesson_id)']
}

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def ident(prefix,parts):
    return prefix+'_'+hashlib.sha256('\x1f'.join(parts).encode('utf-8')).hexdigest()[:16]

def cell(value,typ):
    if value is None: return 'NULL'
    if typ.startswith('integer'): return str(int(value))
    if typ.startswith('jsonb'): value=json.dumps(value,ensure_ascii=False,separators=(',',':'))
    if '\x00' in str(value): raise ValueError('NUL byte cannot be stored in PostgreSQL text')
    return "'"+str(value).replace("'","''")+"'"+('::jsonb' if typ.startswith('jsonb') else '')

def vocab_question(lesson,v,i):
    qid=f'{lesson["id"]}_vq{i:02d}'
    meanings=[v['meaning_vi']]+v['distractors_vi']
    # Stable order from a hash; independent of input ordering and Python hash seed.
    meanings=sorted(meanings,key=lambda x:hashlib.sha256((qid+'|'+x).encode()).hexdigest())
    options=[{'key':chr(65+j),'text':s} for j,s in enumerate(meanings)]
    answer=next(o['key'] for o in options if o['text']==v['meaning_vi'])
    return dict(id=qid,type='mcq_single',category='vocabulary_practice',skill='vocabulary',prompt_en=f'What does "{v["term"]}" mean in this context?\n\n{v["context_quote"]}',options=options,answer=[answer],accepted_answers=[],max_words=None,evidence=[{'passage_id':v['passage_id'],'quote':v['context_quote']}],explanation_vi=f'Trong ngữ cảnh này, "{v["term"]}" có nghĩa là {v["meaning_vi"]}. Cụm từ: {v["collocation"]}.',difficulty={'pre-A1':1,'A1':1,'A2':2,'B1':3,'B2':4,'C1':5,'C2':5}[lesson['cefr_estimate']],vocabulary_context_id=v['id'],generation_method='assembled_from_authored_context_and_distractors',option_language='vi')

def main():
    pack=json.loads((ROOT/'data'/'lessons.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'data'/'sources.json').read_text(encoding='utf-8'))
    check=validate(pack,sources)
    if check['errors']: raise ValueError('\n'.join(check['errors']))
    tables={k:[] for k in TABLES}; word_index={}; sense_index={}; flashcards=[]
    tables['datasets']=[dict(id=DATASET_ID,version='1.0.0',created_on='2026-10-26',metadata=pack['metadata'])]
    for s in sources:
        tables['sources'].append({**{k:s[k] for k in ['id','title','publisher','url']},'details':{k:v for k,v in s.items() if k not in ['id','title','publisher','url']}})
    for l in pack['lessons']:
        lid=l['id']; l['vocabulary_questions']=[]
        l['passage_word_count']=sum(word_count(p['text']) for p in l['passages'])
        row={k:l[k] for k in ['id','track','title_en','title_vi','cefr_estimate','age_min','age_max','topic','estimated_minutes','exam_part','learning_objectives_vi','instructions_en','publication_status','content_origin','passage_word_count']}
        row.update(dataset_id=DATASET_ID,metadata=l['metadata']);tables['lessons'].append(row)
        for s in l['source_ids']:
            tables['lesson_sources'].append(dict(id=lid+'__'+s,lesson_id=lid,source_id=s,relation='format_or_level_reference'))
        pmap={p['id']:p for p in l['passages']}
        for i,p in enumerate(l['passages'],1):
            tables['passages'].append(dict(id=lid+'_p_'+p['id'],lesson_id=lid,label=p['id'],title_en=p['title_en'],text=p['text'],position=i,word_count=word_count(p['text'])))
        for i,v in enumerate(l['vocabulary'],1):
            v['id']=f'{lid}_v{i:02d}'
            wid=ident('w',[normalize_answer(v['term']),v['pos']])
            if wid not in word_index:
                word_index[wid]=dict(id=wid,term=v['term'],normalized_term=normalize_answer(v['term']),pos=v['pos'])
            # Merge only identical term, POS and meaning. Different senses stay separate.
            sid=ident('s',[wid,normalize_answer(v['meaning_vi'])])
            if sid not in sense_index:
                sense_index[sid]=dict(id=sid,word_id=wid,meaning_vi=v['meaning_vi'],definition_en=v['definition_en'])
            v['word_id']=wid;v['sense_id']=sid
            vr={k:v[k] for k in ['id','cefr_estimate','context_quote','example_en','collocation','synonyms','antonyms','distractors_vi']}
            vr.update(lesson_id=lid,passage_id=lid+'_p_'+v['passage_id'],sense_id=sid,position=i)
            tables['lesson_vocabulary'].append(vr)
            l['vocabulary_questions'].append(vocab_question(l,v,i))
            flashcards.append(dict(id='fc_'+v['id'],lesson_id=lid,word_id=wid,sense_id=sid,vocabulary_context_id=v['id'],front_en=v['term'],back_vi=v['meaning_vi'],pos=v['pos'],context_en=v['context_quote'],example_en=v['example_en'],collocation=v['collocation'],synonyms=v['synonyms'],antonyms=v['antonyms'],cefr_estimate=v['cefr_estimate'],track=l['track'],topic=l['topic']))
        for category,qs in [('reading_practice',l['questions']),('vocabulary_practice',l['vocabulary_questions'])]:
            for i,q in enumerate(qs,1):
                q['category']=category
                q['generation_method']=q.get('generation_method','original_ai_authored')
                row={k:q[k] for k in ['id','category','type','skill','prompt_en','options','answer','accepted_answers','max_words','explanation_vi','difficulty','generation_method']}
                evidence=[]
                for e in q['evidence']:
                    start=pmap[e['passage_id']]['text'].index(e['quote'])
                    evidence.append(dict(passage_id=lid+'_p_'+e['passage_id'],passage_label=e['passage_id'],quote=e['quote'],start_char=start,end_char=start+len(e['quote'])))
                row.update(lesson_id=lid,vocabulary_context_id=q.get('vocabulary_context_id'),position=i,evidence=evidence)
                tables['questions'].append(row)
    tables['words']=list(word_index.values());tables['senses']=list(sense_index.values())
    check=validate(pack,sources)
    if check['errors']: raise ValueError('\n'.join(check['errors']))
    dump(ROOT/'data'/'lessons.json',pack)
    with (ROOT/'data'/'lessons.jsonl').open('w',encoding='utf-8') as f:
        for l in pack['lessons']:f.write(json.dumps(l,ensure_ascii=False,separators=(',',':'))+'\n')
    dump(ROOT/'data'/'normalized.json',{'metadata':pack['metadata'],'tables':tables})
    dump(ROOT/'data'/'flashcards.json',flashcards)
    for name,rows in tables.items():
        path=ROOT/'data'/'csv'/f'{name}.csv';path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=[x[0] for x in TABLES[name]],lineterminator='\n');writer.writeheader()
            for row in rows:
                writer.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(list,dict)) else ('' if v is None else v) for k,v in row.items()})
    ddl=['-- PostgreSQL. Isolated seed schema; no DROP/DELETE/UPDATE.','CREATE SCHEMA IF NOT EXISTS '+SCHEMA+';']
    for table,cols in TABLES.items():
        definitions=[f'  {col} {typ}' for col,typ in cols]+['  '+x for x in CONSTRAINTS.get(table,[])]
        ddl.append(f'CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n'+',\n'.join(definitions)+'\n);')
    ddl += [
      f'CREATE INDEX IF NOT EXISTS lr_lessons_track_level ON {SCHEMA}.lessons(track, cefr_estimate);',
      f'CREATE INDEX IF NOT EXISTS lr_questions_lesson ON {SCHEMA}.questions(lesson_id, category);',
      f'CREATE INDEX IF NOT EXISTS lr_vocab_sense ON {SCHEMA}.lesson_vocabulary(sense_id);',
      f'CREATE OR REPLACE VIEW {SCHEMA}.lesson_overview AS SELECT l.id,l.track,l.title_en,l.cefr_estimate,l.publication_status,l.passage_word_count,(SELECT count(*) FROM {SCHEMA}.questions q WHERE q.lesson_id=l.id AND q.category=\'reading_practice\') AS reading_questions,(SELECT count(*) FROM {SCHEMA}.lesson_vocabulary v WHERE v.lesson_id=l.id) AS vocabulary_contexts FROM {SCHEMA}.lessons l;',
      f'CREATE OR REPLACE VIEW {SCHEMA}.flashcard_view AS SELECT v.id,v.lesson_id,w.term,w.pos,s.meaning_vi,s.definition_en,v.context_quote,v.example_en,v.collocation,v.synonyms,v.antonyms,v.cefr_estimate FROM {SCHEMA}.lesson_vocabulary v JOIN {SCHEMA}.senses s ON s.id=v.sense_id JOIN {SCHEMA}.words w ON w.id=s.word_id;',
      f'CREATE OR REPLACE VIEW {SCHEMA}.question_prompts AS SELECT id,lesson_id,category,position,type,skill,prompt_en,options,max_words,difficulty FROM {SCHEMA}.questions;'
    ]
    schema='\n\n'.join(ddl)+'\n'
    (ROOT/'sql'/'schema_postgresql.sql').write_text(schema,encoding='utf-8')
    sql=['-- Run with psql -v ON_ERROR_STOP=1 -f sql/seed_postgresql.sql','BEGIN;','SET LOCAL standard_conforming_strings = on;','SET LOCAL client_encoding = \'UTF8\';',schema]
    for table,rows in tables.items():
        cols=TABLES[table]
        for row in rows:
            sql.append(f'INSERT INTO {SCHEMA}.{table} ('+', '.join(k for k,t in cols)+') VALUES ('+', '.join(cell(row.get(k),t) for k,t in cols)+') ON CONFLICT DO NOTHING;')
    sql.append('COMMIT;')
    (ROOT/'sql'/'seed_postgresql.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
    check['checks_passed']=['unique ids','existing source references','existing passage references','exact evidence substrings','exact vocabulary contexts','term presence','four distinct MCQ options','valid answer keys','free-text word limits','canonical grading','no exact duplicate passages']
    check['limitations']=['Structural checks do not prove semantic correctness or validated CEFR.','No independent teacher review or learner pilot.','Foreign-key definitions generated; database execution status is recorded separately.']
    dump(ROOT/'docs'/'validation_report.json',check)
    bytrack={}
    for track in sorted({l['track'] for l in pack['lessons']}):
        ls=[l for l in pack['lessons'] if l['track']==track]
        bytrack[track]=dict(lessons=len(ls),reading_questions=sum(len(l['questions']) for l in ls),vocabulary_contexts=sum(len(l['vocabulary']) for l in ls),vocabulary_questions=sum(len(l['vocabulary_questions']) for l in ls),word_count_min=min(l['passage_word_count'] for l in ls),word_count_max=max(l['passage_word_count'] for l in ls),cefr_estimates=dict(collections.Counter(l['cefr_estimate'] for l in ls)))
    manifest={'dataset_id':DATASET_ID,'version':'1.0.0','created_on':'2026-10-26','content_origin':'original_ai_authored','publication_status':'draft','counts':{k:len(v) for k,v in tables.items()},'distinct_terms':len({w['normalized_term'] for w in tables['words']}),'distinct_topics':len({l['topic'] for l in pack['lessons']}),'flashcards':len(flashcards),'question_types':dict(collections.Counter(q['type'] for q in tables['questions'] if q['category']=='reading_practice')),'by_track':bytrack,'files':{}}
    for p in sorted((ROOT/'data').rglob('*'))+sorted((ROOT/'sql').rglob('*')):
        if p.is_file():manifest['files'][p.relative_to(ROOT).as_posix()]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    dump(ROOT/'manifest.json',manifest)
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
