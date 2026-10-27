"""Versioned, original learning materials. No network or model calls at runtime."""
import copy
import hashlib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
from .core import InputError

ROOT = Path(__file__).resolve().parents[2] / 'data'
LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')
GOALS = ('general', 'ielts', 'toeic')


def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFD', str(value).casefold().replace('đ','d'))
                   if unicodedata.category(c) != 'Mn')


def source_url(value):
    p = urlsplit(value)
    return p.scheme == 'https' and bool(p.hostname) and not p.username and not p.password and p.port in (None,443)


def validate_unit(unit, kind):
    if not isinstance(unit, dict) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', unit.get('id','')):
        raise InputError('Mã bài học chưa hợp lệ.')
    if unit.get('level') not in LEVELS or not isinstance(unit.get('title'),str) or not unit['title'].strip():
        raise InputError('Bài học cần tên và trình độ hợp lệ.')
    if kind == 'grammar':
        if not 1 <= len(unit.get('explanation',[])) <= 10:
            raise InputError('Bài ngữ pháp cần phần giải thích.')
        for section in unit['explanation']:
            if not all(isinstance(section.get(k),str) and section[k].strip() for k in ('title','body','example','translation_vi')):
                raise InputError('Phần giải thích ngữ pháp còn thiếu.')
        teaching = unit.get('teaching')
        if teaching is not None:
            if not isinstance(teaching, dict) or not all(
                isinstance(teaching.get(k), str) and teaching[k].strip()
                for k in ('objective', 'context', 'example', 'translation_vi')
            ):
                raise InputError('Bài hướng dẫn cần mục tiêu và ví dụ đầy đủ.')
            for name in ('steps', 'takeaways'):
                if not isinstance(teaching.get(name), list) or not 1 <= len(teaching[name]) <= 5 or not all(
                    isinstance(item, str) and item.strip() for item in teaching[name]
                ):
                    raise InputError('Các bước hướng dẫn và ý cần nhớ chưa đầy đủ.')
            check = teaching.get('quick_check')
            if not isinstance(check, dict) or not all(
                isinstance(check.get(k), str) and check[k].strip()
                for k in ('prompt', 'answer', 'explanation_vi')
            ):
                raise InputError('Câu tự luyện cần đề, đáp án và lời giải.')
        validate_questions(unit.get('questions'))
    elif kind == 'vocabulary':
        words=unit.get('words')
        if not isinstance(words,list) or not 4 <= len(words) <= 100:
            raise InputError('Bộ từ cần 4–100 mục.')
        seen=set()
        for w in words:
            if not all(isinstance(w.get(k),str) and w[k].strip() for k in ('word','meaning_vi','example','example_translation','usage_pattern','part_of_speech')):
                raise InputError('Một mục từ còn thiếu nghĩa hoặc ví dụ.')
            key=fold(w['word'])
            if key in seen:raise InputError('Từ bị lặp trong cùng bộ.')
            seen.add(key)
        if len({w['meaning_vi'] for w in words}) != len(words):
            raise InputError('Nghĩa trùng trong bộ từ có thể làm câu hỏi mơ hồ.')
    else:raise InputError('Loại bài không được hỗ trợ.')
    if not unit.get('source_urls') or not all(source_url(u) for u in unit['source_urls']):
        raise InputError('Nguồn tham khảo cần đường dẫn HTTPS.')
    return unit


def validate_questions(questions):
    if not isinstance(questions,list) or not 1<=len(questions)<=100:
        raise InputError('Bộ bài cần 1–100 câu hỏi.')
    ids=set()
    for q in questions:
        if not isinstance(q,dict) or not isinstance(q.get('id'),str) or q['id'] in ids:
            raise InputError('Mã câu hỏi trùng hoặc không hợp lệ.')
        ids.add(q['id'])
        if q.get('prompt_lang','en') not in ('en','vi'):
            raise InputError('Ngôn ngữ câu hỏi chưa hợp lệ.')
        choices=q.get('options')
        if (not isinstance(choices,list) or len(choices)!=4 or
            not all(isinstance(x,str) and x.strip() for x in choices) or len(set(choices))!=4 or
            type(q.get('answer')) is not int or not 0<=q['answer']<4 or
            not isinstance(q.get('prompt'),str) or not q['prompt'].strip() or
            not isinstance(q.get('explanation_vi'),str) or not q['explanation_vi'].strip()):
            raise InputError('Câu hỏi cần bốn lựa chọn khác nhau, một đáp án và lời giải.')
    return questions


@lru_cache(maxsize=2)
def _units(kind):
    name, key = ('grammar_lessons','lessons') if kind=='grammar' else ('vocabulary_collections','collections')
    data=json.loads((ROOT/f'{name}.json').read_text(encoding='utf-8'))
    if data.get('version')!=1:raise InputError('Phiên bản nội dung chưa được hỗ trợ.')
    result=[validate_unit(row,kind) for row in data[key]]
    ids=[r['id'] for r in result]
    if len(ids)!=len(set(ids)):raise InputError('Mã bài học bị trùng.')
    if kind=='grammar':
        earlier=set()
        for row in result:
            if not set(row.get('prerequisites',[]))<=earlier:raise InputError('Thứ tự bài nền tảng chưa hợp lệ.')
            earlier.add(row['id'])
    return result


def units(kind):
    if kind not in ('grammar','vocabulary'):raise InputError('Loại bài không được hỗ trợ.')
    if kind == 'vocabulary':
        from django.apps import apps
        if apps.ready:
            from learning.models import VocabularyCollection
            saved = list(VocabularyCollection.objects.all())
            if saved:
                return [{**row.content, 'id': row.slug, 'title': row.title, 'topic': row.topic, 'level': row.level}
                        for row in saved]
    return copy.deepcopy(_units(kind))


def get_unit(kind, unit_id):
    return next((row for row in units(kind) if row['id']==unit_id),None)


def questions_for(unit, kind):
    if kind=='grammar':return copy.deepcopy(unit['questions'])
    if unit.get('questions'):
        return copy.deepcopy(validate_questions(unit['questions']))
    words=unit['words']; questions=[]
    for i,w in enumerate(words):
        distractors=[words[(i+j)%len(words)]['meaning_vi'] for j in (1,2,3)]
        slot=int(hashlib.sha256((unit['id']+w['word']).encode()).hexdigest()[:8],16)%4
        options=distractors[:];options.insert(slot,w['meaning_vi'])
        questions.append({'id':f'w{i+1}','prompt':f'Trong câu “{w["example"]}”, “{w["word"]}” có nghĩa là gì?',
            'options':options,'answer':slot,'explanation_vi':f'{w["word"]}: {w["meaning_vi"]}. {w["example_translation"]} Cách dùng: {w["usage_pattern"]}.'})
    return questions


def quiz_snapshot(unit, kind):
    return {'id':unit['id'],'title':unit['title'],'level':unit['level'],'kind':kind,'questions':questions_for(unit,kind)}


def revision(snapshot):
    return hashlib.sha256(json.dumps(snapshot,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16]


def grade(snapshot, answers):
    qs=validate_questions(snapshot['questions'])
    if not isinstance(answers,dict) or set(answers)!={q['id'] for q in qs}:
        raise InputError('Bạn hãy trả lời đủ các câu trước khi xem kết quả.')
    if any(type(v) is not int or not 0<=v<4 for v in answers.values()):
        raise InputError('Mỗi câu cần một lựa chọn hợp lệ.')
    results=[{**q,'submitted':answers[q['id']],'correct':answers[q['id']]==q['answer']} for q in qs]
    score=sum(r['correct'] for r in results)
    return {'score':score,'total':len(qs),'percent':round(score/len(qs)*100),'results':results}


def summary(unit, kind):
    categories={'everyday_english':'Everyday English','focused_practice':'Reading Skills',
                'ielts_academic':'IELTS Academic','ielts_general':'IELTS General Training','toeic':'TOEIC',
                'school_primary':'School English','school_lower_secondary':'School English','school_upper_secondary':'School English'}
    return {k:unit[k] for k in ('id','title','level','tags','topic') if k in unit} | {
        'category':categories.get(unit.get('track'),unit.get('topic','')),
        'description':unit.get('summary',unit.get('description','')),
        'minutes':unit.get('minutes',8), 'question_count':len(questions_for(unit,kind)),
        'word_count':len(unit.get('words',[]))}


def word_entry(word, unit):
    return {'word':word['word'],'meaning_vi':word['meaning_vi'],'pos':word['part_of_speech'],
            'example':word['example'],'example_vi':word['example_translation'],'usage_pattern':word['usage_pattern'],
            'context':word.get('context',''),
            'source_label':'LexiRead · '+unit['title'],'tags':[unit['title'],unit['level']],
            'origin':'curated','verified':False}
