"""Adapt supplied reading packs without executing their SQL or tools."""
import copy
from learning.services.core import InputError, paragraphs
from learning.services.toeic import validate_toeic_set


def adapt_dataset(pack,kind):
    lessons=pack.get('lessons')
    if not isinstance(lessons,list) or not 1<=len(lessons)<=100: raise InputError('Gói cần 1–100 bài.')
    result=[]
    for lesson in lessons:
        if not isinstance(lesson,dict): raise InputError('Bài trong gói không hợp lệ.')
        is_toeic=lesson.get('track')=='toeic'
        if is_toeic!=(kind=='toeic'): continue
        try: result.append(adapt_one(lesson,pack.get('metadata',{}),kind))
        except (ValueError,KeyError,TypeError,IndexError,AttributeError) as exc:
            raise InputError(f"{lesson.get('id','?')}: không chuyển được bài: {exc}") from exc
    if not result: raise InputError('Không có bài thuộc loại đã chọn trong gói.')
    return result


def adapt_one(source,metadata,kind,slug=None):
    passages=source['passages']
    indexes={p['id']:index for index,p in enumerate(passages)}
    if len(indexes)!=len(passages): raise InputError('ID đoạn bị trùng.')
    # A source passage can itself contain blank-line-separated paragraphs.
    offsets={}; offset=0
    for p in passages:
        offsets[p['id']]=offset
        offset+=len(paragraphs(p['text']))
    def paragraph_index(passage_id, quote):
        parts=paragraphs(passages[indexes[passage_id]]['text'])
        for index, text in enumerate(parts):
            if quote and quote in text:
                return offsets[passage_id]+index
        raise InputError('Trích dẫn không nằm trọn trong một đoạn nguồn.')
    editorial={'dataset':metadata,'original':copy.deepcopy(source),
               'note':'AI biên soạn; chưa có giáo viên duyệt. Nguồn tham khảo chỉ đối chiếu cấu trúc/trình độ.'}
    base={'slug':slug or 'pack-v1-'+source['id'].replace('_','-'),'title':source['title_en'],
          'level':source['cefr_estimate'],'revision':1,'published':False,'editorial':editorial}
    vocabulary=[{'word':v['term'],'pos':v['pos'],'meaning_vi':v['meaning_vi'],
                 'example':v['example_en'],'context':v['context_quote'],
                 'synonyms':v.get('synonyms',[]),'paraphrases':v.get('paraphrases') or ([v['definition_en']] if v.get('definition_en') else []),
                 'usage_pattern':v.get('collocation',''),
                 'tags':[source['track'],source['topic']], 'note':'Diễn giải nghĩa để hiểu từ, không mặc định thay thế trực tiếp trong câu.',
                 'source_label':source['title_en'],'paragraph_index':paragraph_index(v['passage_id'],v['context_quote'])} for v in source['vocabulary']]
    questions=[]
    for q in source['questions']:
        evidence=q['evidence'][0]
        # Verify every quotation before mapping; retain all original references in editorial.
        for e in q['evidence']:
            if not e['quote'] or e['quote'] not in passages[indexes[e['passage_id']]]['text']:
                raise InputError('Bằng chứng không khớp đoạn nguồn.')
        options=q.get('options',[])
        if q['type']=='true_false_not_given': options=[{'key':v,'text':v} for v in ('TRUE','FALSE','NOT GIVEN')]
        if q['type']=='yes_no_not_given': options=[{'key':v,'text':v} for v in ('YES','NO','NOT GIVEN')]
        answer=q['answer'][0]
        answer_index=next((i for i,o in enumerate(options) if o['key']==answer),None)
        if options and answer_index is None: raise InputError('Đáp án không khớp lựa chọn.')
        row={'id':q['id'],'prompt':q['prompt_en'],'options':[o['text'] for o in options],
             'answer':answer_index if options else answer,'evidence':evidence['quote'],
             'explanation_vi':q['explanation_vi']}
        if kind=='toeic':
            if q['type']!='mcq_single': raise InputError('TOEIC cần câu trắc nghiệm 4 lựa chọn.')
            doc_ids=list(dict.fromkeys(e['passage_id'] for e in q['evidence']))
            groups=source.get('metadata',{}).get('document_groups',[])
            group=next((g for g in groups if g['id']==q.get('group_id')),None)
            if group:
                if not set(doc_ids)<=set(group['passage_ids']) or not set(group['passage_ids'])<=set(indexes):
                    raise InputError('Nhóm văn bản TOEIC không khớp bằng chứng.')
                doc_ids=group['passage_ids']
            row.update(part=int(source['exam_part'].rsplit(' ',1)[-1]),document_ids=doc_ids)
        else:
            question_kind={'mcq_single':q.get('skill','detail'),'true_false_not_given':'tfng','yes_no_not_given':'ynng'}.get(q['type'],q['type'])
            if q['type']=='mcq_single' and question_kind not in ('main_idea','detail','vocabulary','inference'): question_kind='detail'
            row.update(kind=question_kind,paragraph_index=paragraph_index(evidence['passage_id'],evidence['quote']))
            if not options: row.update(accepted_answers=q['accepted_answers'],max_words=q['max_words'])
        questions.append(row)
    if kind=='toeic':
        part=int(source['exam_part'].rsplit(' ',1)[-1])
        return {**validate_toeic_set({**base,'mode':'part-7' if part==7 else 'parts-5-6',
            'parts':[part],'mode_label':source['exam_part'],'duration_minutes':source['estimated_minutes'],
            'description':source['title_vi'],'instructions':source['instructions_en'],
            'documents':[{'id':p['id'],'kind':'text','heading':p['title_en'],'body':p['text']} for p in passages],
            'questions':questions,'focus_vocabulary':vocabulary}),'published':False}
    return {**base,'track':'ielts' if source['track'] in ('ielts_academic','ielts_general') else 'general',
            'topic':source['topic'],'summary':source['title_vi'],'order':1000,
            'text':'\n\n'.join(p['text'] for p in passages),
            'analysis':{'translations':[],'vocabulary':vocabulary,'grammar':[]},'translation_status':'not_provided',
            'questions':questions,'faqs':[],
            'author':'LexiRead · '+str(metadata.get('version','1.0.0')),'provenance':editorial['note'],
            'level_note':'CEFR ước lượng, chưa hiệu chuẩn. Không phải đề thi chính thức.'}
