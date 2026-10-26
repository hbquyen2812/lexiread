"""Pure TOEIC validation/scoring and bundled bootstrap data (not the live repository)."""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path
from .core import InputError,clean_text,validate_entry

DATA_DIR=Path(__file__).resolve().parents[2]/'data'/'toeic'
MODES={'parts-5-6','part-7'}

def _integer(value,minimum,maximum,label):
    if not isinstance(value,int) or isinstance(value,bool) or not minimum<=value<=maximum:
        raise InputError(f'{label} không hợp lệ.')
    return value

def validate_toeic_set(raw):
    if not isinstance(raw,dict):raise InputError('Bộ TOEIC phải là đối tượng JSON.')
    slug=clean_text(raw.get('slug',''),100,True)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise InputError('Slug bộ TOEIC không hợp lệ.')
    mode=raw.get('mode')
    if mode not in MODES:raise InputError('Chế độ TOEIC không hợp lệ.')
    parts=raw.get('parts',[])
    expected=set(parts) if isinstance(parts,list) and all(type(p) is int for p in parts) else set()
    if not expected or (mode=='parts-5-6' and not expected<={5,6}) or (mode=='part-7' and expected!={7}):raise InputError('Phần thi không khớp chế độ TOEIC.')
    documents=raw.get('documents',[])
    if not isinstance(documents,list) or len(documents)>10:raise InputError('Danh sách văn bản TOEIC không hợp lệ.')
    clean_documents=[];document_ids=set()
    for doc in documents:
        if not isinstance(doc,dict):raise InputError('Văn bản TOEIC không hợp lệ.')
        doc_id=clean_text(doc.get('id',''),40,True)
        if doc_id in document_ids:raise InputError('ID văn bản TOEIC bị trùng.')
        document_ids.add(doc_id)
        clean_documents.append({'id':doc_id,'kind':clean_text(doc.get('kind',''),40,True),
            'heading':clean_text(doc.get('heading',''),200,True),'body':clean_text(doc.get('body',''),8000,True)})
    questions=raw.get('questions',[])
    if not isinstance(questions,list) or not 1<=len(questions)<=100:raise InputError('Bộ TOEIC cần 1–100 câu hỏi.')
    clean_questions=[];question_ids=set()
    for q in questions:
        if not isinstance(q,dict):raise InputError('Câu hỏi TOEIC không hợp lệ.')
        qid=clean_text(q.get('id',''),40,True)
        if qid in question_ids:raise InputError('ID câu hỏi TOEIC bị trùng.')
        question_ids.add(qid)
        part=_integer(q.get('part'),5,7,'Part')
        if part not in expected:raise InputError('Câu hỏi nằm sai phần TOEIC.')
        options=q.get('options',[])
        if not isinstance(options,list) or len(options)!=4:raise InputError('Mỗi câu TOEIC cần đúng 4 lựa chọn.')
        options=[clean_text(value,1000,True) for value in options]
        if len(set(options))!=4:raise InputError('Lựa chọn TOEIC không được trùng.')
        answer=_integer(q.get('answer'),0,3,'Đáp án')
        doc_ids=q.get('document_ids',[])
        if not isinstance(doc_ids,list) or any(value not in document_ids for value in doc_ids):
            raise InputError('Câu hỏi tham chiếu văn bản không tồn tại.')
        evidence=clean_text(q.get('evidence',''),2000)
        if evidence and not any(evidence in doc['body'] and doc['id'] in doc_ids for doc in clean_documents):
            raise InputError('Bằng chứng TOEIC không khớp văn bản.')
        clean_questions.append({'id':qid,'part':part,'prompt':clean_text(q.get('prompt',''),1500,True),
            'options':options,'answer':answer,'explanation_vi':clean_text(q.get('explanation_vi',''),3000,True),
            'evidence':evidence,'document_ids':doc_ids})
    if {q['part'] for q in clean_questions}!=expected:raise InputError('Bộ TOEIC chưa có đủ các Part đã khai báo.')
    if any(q['part']==7 and (not q['document_ids'] or not q['evidence']) for q in clean_questions):
        raise InputError('Câu Part 7 cần văn bản nguồn và bằng chứng chính xác.')
    words=raw.get('focus_vocabulary',[])
    if not isinstance(words,list) or len(words)>30:raise InputError('Danh sách từ trọng tâm không hợp lệ.')
    vocabulary=[]
    for item in words:
        entry=validate_entry(item);entry.update(origin='curated',verified=False)
        vocabulary.append(entry)
    return {'slug':slug,'title':clean_text(raw.get('title',''),200,True),'mode':mode,
        'revision':_integer(raw.get('revision',1),1,10000,'Phiên bản'),
        'editorial':copy.deepcopy(raw.get('editorial',{})),
        'provenance':clean_text(raw.get('provenance') or (raw.get('editorial') or {}).get('note') or 'Bài luyện tự biên soạn, không phải đề thi ETS chính thức.',1000),
        'mode_label':clean_text(raw.get('mode_label',''),100,True),'parts':parts,
        'level':clean_text(raw.get('level',''),20,True),
        'duration_minutes':_integer(raw.get('duration_minutes'),1,75,'Thời lượng'),
        'description':clean_text(raw.get('description',''),1000,True),
        'instructions':clean_text(raw.get('instructions',''),1500,True),
        'documents':clean_documents,'questions':clean_questions,'focus_vocabulary':vocabulary,
        'question_count':len(clean_questions)}

@lru_cache(maxsize=1)
def toeic_sets():
    practices=[validate_toeic_set(json.loads(path.read_text(encoding='utf-8'))) for path in DATA_DIR.glob('*.json')]
    if len({item['slug'] for item in practices})!=len(practices):raise InputError('Slug bộ TOEIC bị trùng.')
    return tuple(sorted(practices,key=lambda item:(item['mode'],item['slug'])))

def get_toeic_set(slug):
    for practice in toeic_sets():
        if practice['slug']==slug:return copy.deepcopy(practice)
    raise InputError('Không tìm thấy bộ luyện TOEIC.')

def public_toeic_set(slug):
    practice=get_toeic_set(slug)
    practice.pop('editorial',None)
    practice['questions']=[{key:copy.deepcopy(q[key]) for key in ('id','part','prompt','options','document_ids')} for q in practice['questions']]
    return practice

def grade_toeic(practice,answers):
    questions=practice['questions']
    if not isinstance(answers,dict) or set(answers)!={q['id'] for q in questions}:
        raise InputError('Hãy trả lời đầy đủ các câu hỏi trước khi nộp.')
    results=[]
    for q in questions:
        submitted=_integer(answers[q['id']],0,3,'Lựa chọn')
        results.append({'question_id':q['id'],'correct':submitted==q['answer'],'submitted':submitted,
            'answer':q['answer'],'explanation_vi':q['explanation_vi'],'evidence':q['evidence']})
    by_part={}
    for part in practice['parts']:
        rows=[result for result,q in zip(results,questions) if q['part']==part]
        by_part[str(part)]={'score':sum(int(row['correct']) for row in rows),'total':len(rows)}
    return {'score':sum(int(row['correct']) for row in results),'total':len(results),
        'percentage':round(100*sum(int(row['correct']) for row in results)/len(results)),
        'by_part':by_part,'results':results}
