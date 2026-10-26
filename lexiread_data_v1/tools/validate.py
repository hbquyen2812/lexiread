"""Validate the authored lesson pack. No third-party packages or network required."""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from grading import grade,normalize_answer,word_count

CEFR={'pre-A1','A1','A2','B1','B2','C1','C2'}
TRACKS={'ielts_academic','toeic','school_primary','school_lower_secondary','school_upper_secondary'}
TYPES={'mcq_single','true_false_not_given','yes_no_not_given','short_answer','gap_fill','matching_heading','matching_information'}

def validate(pack,sources=None):
    errors=[]; warnings=[]; question_ids=set(); passage_hashes={}; ids=set()
    source_ids={s['id'] for s in sources} if sources is not None else None
    for lesson in pack['lessons']:
        lid=lesson.get('id','?')
        def check(test,message):
            if not test: errors.append(f'{lid}: {message}')
        check(lid not in ids,'duplicate lesson id'); ids.add(lid)
        for key in ['title_en','title_vi','instructions_en','topic','exam_part','learning_objectives_vi']:
            check(bool(lesson.get(key)),f'missing {key}')
        check(lesson.get('track') in TRACKS,'invalid track')
        check(lesson.get('cefr_estimate') in CEFR,'invalid CEFR')
        check(0<lesson.get('age_min',0)<=lesson.get('age_max',0),'invalid age range')
        check(lesson.get('estimated_minutes',0)>0,'invalid time')
        check(bool(lesson.get('source_ids')),'no format reference')
        if source_ids is not None:
            check(set(lesson.get('source_ids',[]))<=source_ids,'unknown source id')
        passages={p['id']:p['text'] for p in lesson['passages']}
        check(len(passages)==len(lesson['passages']),'duplicate paragraph label')
        for pid,txt in passages.items():
            check(bool(txt.strip()),f'empty passage {pid}')
            h=hashlib.sha256(normalize_answer(txt).encode()).hexdigest()
            if h in passage_hashes: errors.append(f'{lid}: passage duplicates {passage_hashes[h]}')
            passage_hashes[h]=lid+'/'+pid
        for q in lesson['questions']+lesson.get('vocabulary_questions',[]):
            qid=q.get('id','?')
            check(qid not in question_ids,f'duplicate question {qid}'); question_ids.add(qid)
            check(q.get('type') in TYPES,f'{qid}: unknown question type')
            check(bool(q.get('prompt_en')) and bool(q.get('explanation_vi')),f'{qid}: missing prompt/explanation')
            check(1<=q.get('difficulty',0)<=5,f'{qid}: invalid difficulty')
            ans=q.get('answer',[]); options=q.get('options',[])
            check(len(ans)==1,f'{qid}: expected one answer')
            keys=[o['key'] for o in options]
            check(len(keys)==len(set(keys)),f'{qid}: duplicate option key')
            check(len(options)==len({normalize_answer(o['text']) for o in options}),f'{qid}: duplicate option text')
            if q['type']=='mcq_single': check(len(options)==4,f'{qid}: MCQ needs four options')
            if q['type'] in ('mcq_single','matching_heading','matching_information'):
                check(bool(options) and set(ans)<=set(keys),f'{qid}: answer not an option')
            if q['type']=='true_false_not_given': check(set(ans)<={'TRUE','FALSE','NOT GIVEN'},f'{qid}: invalid TFNG')
            if q['type']=='yes_no_not_given': check(set(ans)<={'YES','NO','NOT GIVEN'},f'{qid}: invalid YNNG')
            check(bool(q.get('evidence')),f'{qid}: no evidence')
            for e in q.get('evidence',[]):
                check(e['passage_id'] in passages,f'{qid}: missing passage {e["passage_id"]}')
                check(bool(e['quote']) and e['quote'] in passages.get(e['passage_id'],''),f'{qid}: evidence not exact substring')
            if q['type'] in ('gap_fill','short_answer'):
                check(isinstance(q.get('max_words'),int) and q['max_words']>0,f'{qid}: missing max_words')
                check(bool(q.get('accepted_answers')),f'{qid}: no accepted answers')
                if q.get('max_words'):
                    check(all(word_count(a)<=q['max_words'] for a in ans+q.get('accepted_answers',[])),f'{qid}: answer exceeds word limit')
                text=' '.join(e['quote'] for e in q['evidence'])
                check(all(normalize_answer(a) in normalize_answer(text) for a in ans),f'{qid}: free-text answer absent from evidence')
            if ans: check(grade(q,ans[0]),f'{qid}: canonical answer fails grading')
        terms=set()
        for i,v in enumerate(lesson['vocabulary'],1):
            label=f'v{i:02d} {v.get("term")}'
            key=(normalize_answer(v['term']),v['pos'])
            check(key not in terms,f'{label}: duplicate term within lesson');terms.add(key)
            check(v['cefr_estimate'] in CEFR,f'{label}: invalid CEFR')
            for k in ('meaning_vi','definition_en','example_en','collocation','context_quote'):
                check(bool(v.get(k)),f'{label}: missing {k}')
            check(v['passage_id'] in passages,f'{label}: missing passage')
            check(v['context_quote'] in passages.get(v['passage_id'],''),f'{label}: context not exact substring')
            check(normalize_answer(v['term']) in normalize_answer(v['context_quote']),f'{label}: term absent from context')
            check(normalize_answer(v['term']) in normalize_answer(v['example_en']),f'{label}: term absent from example')
            ds=v.get('distractors_vi',[])
            check(len(ds)==3,f'{label}: needs 3 distractors')
            check(len({normalize_answer(x) for x in ds+[v['meaning_vi']]})==4,f'{label}: duplicate meaning option')
        wc=sum(word_count(x) for x in passages.values())
        ranges={'ielts_academic':(300,450),'school_primary':(60,140),'school_lower_secondary':(120,230),'school_upper_secondary':(210,330)}
        if lesson['track'] in ranges:
            lo,hi=ranges[lesson['track']]
            if not lo<=wc<=hi: warnings.append(f'{lid}: {wc} words, design target {lo}–{hi}')
    return {'errors':errors,'warnings':warnings,'lesson_count':len(pack['lessons']),'question_count':len(question_ids),'vocabulary_contexts':sum(len(l['vocabulary']) for l in pack['lessons'])}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('file',nargs='?',default=str(Path(__file__).resolve().parents[1]/'data'/'lessons.json'))
    parser.add_argument('--sources',default=None);parser.add_argument('--output',default=None)
    a=parser.parse_args(); pack=json.loads(Path(a.file).read_text(encoding='utf-8'))
    sources=json.loads(Path(a.sources).read_text(encoding='utf-8')) if a.sources else None
    result=validate(pack,sources)
    if a.output: Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if result['errors'] else 0
if __name__=='__main__': sys.exit(main())
