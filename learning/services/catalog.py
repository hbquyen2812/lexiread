"""Validation and scoring for fixed, versioned lessons. Pure functions: no DB/network."""
import copy
import re
from .core import InputError, clean_text, paragraphs, MAX_READING_CHARS
from .analysis import validate_analysis, VOCAB_SCHEMA

LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')

def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise InputError(f'{label}: cần số nguyên từ {low} đến {high}.')
    return value

def exact_evidence(raw, paras):
    if not isinstance(raw, dict): raise InputError('Bằng chứng phải là một JSON object.')
    idx = integer(raw.get('paragraph_index'), 0, len(paras)-1, 'Đoạn bằng chứng')
    quote = clean_text(raw.get('evidence', ''), 4000, True)
    if quote not in paras[idx]:
        raise InputError('Trích dẫn không khớp nguyên văn đoạn được chỉ định.')
    return idx, quote

def validate_lesson(raw):
    if not isinstance(raw, dict):
        raise InputError('Mỗi bài soạn sẵn phải là một JSON object.')
    slug = clean_text(raw.get('slug', ''), 100, True)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise InputError('Slug chỉ gồm chữ thường, số và dấu gạch nối.')
    level = raw.get('level')
    if level not in LEVELS: raise InputError('Trình độ bài đọc không hợp lệ.')
    text = clean_text(raw.get('text', ''), MAX_READING_CHARS, True)
    paras = paragraphs(text)
    a = raw.get('analysis', {})
    if not isinstance(a, dict): raise InputError('analysis phải là JSON object.')
    if not isinstance(a.get('vocabulary', []), list) or any(not isinstance(v, dict) for v in a.get('vocabulary', [])):
        raise InputError('vocabulary phải là danh sách các JSON object.')
    basic = {k: a.get(k, []) for k in ('translations', 'vocabulary', 'grammar')}
    basic['vocabulary'] = [{k: v.get(k, [] if k in ('synonyms','paraphrases','tags') else '')
                            for k in VOCAB_SCHEMA['properties']} for v in basic['vocabulary']]
    analysis = validate_analysis(basic, text)
    if analysis['warnings']: raise InputError('Bài soạn sẵn chứa từ/cấu trúc không khớp nguồn: '+str(analysis['warnings']))
    analysis['origin'] = 'curated'
    for v in analysis['vocabulary']: v.update(origin='curated', verified=False)
    questions = raw.get('questions', [])
    if not isinstance(questions, list) or not 1 <= len(questions) <= 20:
        raise InputError('Mỗi bài cần 1–20 câu hỏi.')
    clean_questions, ids = [], set()
    for q in questions:
        if not isinstance(q, dict): raise InputError('Câu hỏi phải là JSON object.')
        qid = clean_text(q.get('id', ''), 60, True)
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',qid) or qid in ids: raise InputError('ID câu hỏi trùng hoặc không hợp lệ.')
        ids.add(qid)
        kind = q.get('kind')
        if kind not in {'main_idea', 'detail', 'tfng', 'vocabulary', 'inference'}: raise InputError('Dạng câu hỏi không hợp lệ.')
        opts = q.get('options', [])
        if not isinstance(opts,list) or not 2 <= len(opts) <= 4: raise InputError('Cần 2–4 lựa chọn.')
        opts = [clean_text(x, 1000, True) for x in opts]
        if len(set(x.casefold() for x in opts)) != len(opts): raise InputError('Lựa chọn bị trùng.')
        if kind == 'tfng' and opts != ['TRUE', 'FALSE', 'NOT GIVEN']: raise InputError('TFNG cần đúng ba nhãn.')
        idx, quote = exact_evidence(q, paras)
        clean_questions.append(dict(id=qid,kind=kind,prompt=clean_text(q.get('prompt',''),2000,True),
            options=opts,answer=integer(q.get('answer'),0,len(opts)-1,'Đáp án'),paragraph_index=idx,
            evidence=quote,explanation_vi=clean_text(q.get('explanation_vi',''),4000,True)))
    faqs = raw.get('faqs', [])
    if not isinstance(faqs,list) or len(faqs)>20: raise InputError('Tối đa 20 phần giải đáp soạn sẵn.')
    clean_faqs=[]
    for f in faqs:
        idx,quote=exact_evidence(f,paras)
        clean_faqs.append(dict(question=clean_text(f.get('question',''),1000,True),
            answer_vi=clean_text(f.get('answer_vi',''),6000,True),paragraph_index=idx,evidence=quote))
    return dict(slug=slug,title=clean_text(raw.get('title',''),200,True),level=level,
        topic=clean_text(raw.get('topic',''),120,True),summary=clean_text(raw.get('summary',''),800,True),
        revision=integer(raw.get('revision',1),1,10000,'Phiên bản'),
        order=integer(raw.get('order',0),0,100000,'Thứ tự'),published=raw.get('published',True) is True,
        author=clean_text(raw.get('author','LexiRead'),200),
        provenance=clean_text(raw.get('provenance','Nội dung học tham khảo; không phải đề IELTS chính thức.'),1000),
        level_note=clean_text(raw.get('level_note','Mức độ ước lượng, chưa hiệu chuẩn CEFR.'),1000),
        text=text,analysis=analysis,questions=clean_questions,faqs=clean_faqs)

def public_lesson(snapshot):
    """Answer keys stay on the backend until submission. Not an examination system."""
    if not snapshot: return None
    result={k:copy.deepcopy(snapshot.get(k)) for k in
            ('slug','title','level','topic','summary','revision','author','provenance','level_note','faqs')}
    result['questions']=[{k:copy.deepcopy(q[k]) for k in ('id','kind','prompt','options')} for q in snapshot.get('questions',[])]
    return result

def grade_lesson(snapshot, answers):
    questions=snapshot.get('questions',[])
    if not questions: raise InputError('Bài này chưa có bộ câu hỏi cố định.')
    if not isinstance(answers,dict) or set(answers) != {q['id'] for q in questions}:
        raise InputError('Hãy trả lời đầy đủ các câu hỏi trước khi nộp.')
    results=[]
    for q in questions:
        value=integer(answers[q['id']],0,len(q['options'])-1,'Lựa chọn')
        results.append(dict(question_id=q['id'],correct=value==q['answer'],submitted=value,answer=q['answer'],
            explanation_vi=q['explanation_vi'],paragraph_index=q['paragraph_index'],evidence=q['evidence']))
    return dict(score=sum(int(x['correct']) for x in results),total=len(results),results=results)

def clean_reading_progress(raw, text):
    if not isinstance(raw,dict): raise InputError('Tiến độ đọc không hợp lệ.')
    out={}
    if 'paragraph' in raw: out['paragraph']=integer(raw['paragraph'],0,len(paragraphs(text))-1,'Vị trí đọc')
    for key in ('completed','favorite'):
        if key in raw:
            if type(raw[key]) is not bool: raise InputError(f'{key} phải là boolean.')
            out[key]=raw[key]
    return out
