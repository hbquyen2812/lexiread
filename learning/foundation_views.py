"""Private foundation learning API. All progress belongs to the signed-in learner."""
import copy
import json
import uuid
from urllib.parse import quote
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse, Http404
from .views import api, body
from .models import LearningProfile, FoundationAttempt, Vocabulary
from .services.core import InputError, fingerprint
from .services.storage import save_entry
from .services.motivation import record_learning
from .services.foundation_content import (ROOT, LEVELS, units, get_unit, summary, quiz_snapshot,
    revision, grade, fold, word_entry)
from .services.learning_path import clean_profile, profile_for, progress_for, plan_for


def find_unit(kind, unit_id):
    unit=get_unit(kind,unit_id)
    if unit is None:raise Http404('Bài học không tồn tại.')
    return unit


@api('GET')
def overview(request):
    kind=request.GET.get('kind','grammar')
    rows=units(kind); level=request.GET.get('level',''); q=fold(request.GET.get('q','')[:100])
    if level and level not in LEVELS:raise InputError('Trình độ chưa hợp lệ.')
    rows=[r for r in rows if (not level or r['level']==level) and (not q or q in fold(r['title']+' '+r.get('summary',r.get('description',''))))]
    progress=progress_for(request.user)
    return JsonResponse({'items':[summary(r,kind)|{'progress':progress.get(kind+'/'+r['id'])} for r in rows],
                         'profile':profile_for(request.user),'kind':kind})


@api('GET')
def unit_detail(request, kind, unit_id):
    unit=find_unit(kind,unit_id); snapshot=quiz_snapshot(unit,kind)
    result=copy.deepcopy(unit);result.pop('questions',None)
    result['questions']=[{k:q[k] for k in ('id','prompt','options','prompt_lang') if k in q} for q in snapshot['questions']]
    result['version']=revision(snapshot)
    result['progress']=progress_for(request.user).get(kind+'/'+unit_id)
    if kind == 'grammar':
        course = units('grammar')
        index = next(i for i, row in enumerate(course) if row['id'] == unit_id)
        def nav_item(i):
            return {k: course[i][k] for k in ('id', 'title', 'level')} if 0 <= i < len(course) else None
        result['navigation'] = {'previous': nav_item(index - 1), 'next': nav_item(index + 1)}
    if kind=='vocabulary':
        owned=set(Vocabulary.objects.filter(owner=request.user).values_list('fingerprint',flat=True))
        for w in result['words']:w['saved']=fingerprint(w['word'],w['meaning_vi']) in owned
    return JsonResponse(result)


@api('POST')
def submit(request, kind, unit_id):
    if len(request.body)>65536:raise InputError('Dữ liệu bài làm quá lớn.')
    data=body(request);token=uuid.UUID(data.get('token',''))
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        previous=FoundationAttempt.objects.filter(owner=request.user,token=token).first()
        if previous:
            if previous.kind!=kind or previous.unit_id!=unit_id:raise InputError('Mã lượt làm bài đã dùng cho bài khác.')
            return JsonResponse(previous.result|{'duplicate':True})
        unit=find_unit(kind,unit_id);snapshot=quiz_snapshot(unit,kind)
        if data.get('version')!=revision(snapshot):raise InputError('Bài đã được cập nhật. Tải lại trang để dùng phiên bản mới.')
        result=grade(snapshot,data.get('answers'))
        FoundationAttempt.objects.create(owner=request.user,kind=kind,unit_id=unit_id,token=token,
            answers=data['answers'],result=result,snapshot=snapshot)
        record_learning(request.user)
    return JsonResponse(result|{'duplicate':False},status=201)


@api('POST')
def save_collection(request, unit_id):
    unit=find_unit('vocabulary',unit_id);selected=body(request).get('indices')
    if (not isinstance(selected,list) or not 1<=len(selected)<=len(unit['words']) or
        any(type(i) is not int or not 0<=i<len(unit['words']) for i in selected) or len(selected)!=len(set(selected))):
        raise InputError('Chọn ít nhất một từ hợp lệ để lưu.')
    entries=[word_entry(unit['words'][i],unit) for i in selected]
    made=0
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        for entry in entries:
            old=Vocabulary.objects.filter(owner=request.user,fingerprint=fingerprint(entry['word'],entry['meaning_vi'])).first()
            if old and len(set(old.tags+entry['tags']))>20:raise InputError('Một từ đã có quá nhiều nhãn. Bớt nhãn rồi thử lại nhé.')
        for entry in entries:
            _,created=save_entry(request.user,entry);made+=int(created)
    return JsonResponse({'created':made,'existing':len(entries)-made,'tag':unit['title']},status=201)


@api('GET','PATCH')
def plan(request):
    if request.method=='PATCH':
        fields=clean_profile(body(request))
        LearningProfile.objects.update_or_create(owner=request.user,defaults=fields)
    return JsonResponse(plan_for(request.user))


@api('GET')
def dictionary(request):
    q=request.GET.get('q','')[:80].strip(); key=fold(q); level=request.GET.get('level','')
    if level and level not in LEVELS:raise InputError('Trình độ chưa hợp lệ.')
    if len(key)<2:return JsonResponse({'items':[],'total':0,'links':[]})
    matches={}
    for unit in units('vocabulary'):
        if level and unit['level']!=level:continue
        for w in unit['words']:
            if key in fold(w['word']+' '+w['meaning_vi']+' '+w['usage_pattern']):
                ident=fingerprint(w['word'],w['meaning_vi'])
                matches.setdefault(ident,{**w,'levels':[],'collection_id':unit['id'],'collection':unit['title']})['levels'].append(unit['level'])
    rows=sorted(matches.values(),key=lambda r:(fold(r['word'])!=key,not fold(r['word']).startswith(key),r['word']))
    return JsonResponse({'items':rows[:40],'total':len(rows),'links':[
        {'title':'Cambridge Dictionary','url':'https://dictionary.cambridge.org/search/english/direct/?q='+quote(q,safe='')},
        {'title':'Oxford Learner’s Dictionaries','url':'https://www.oxfordlearnersdictionaries.com/search/english/?q='+quote(q,safe='')},
        {'title':'Merriam-Webster','url':'https://www.merriam-webster.com/dictionary/'+quote(q,safe='')} ]})


@api('GET')
def sources(request):
    data=json.loads((ROOT/'study_sources.json').read_text(encoding='utf-8'))
    kind=request.GET.get('kind','');level=request.GET.get('level','')
    items=[r for r in data['items'] if (not kind or r['kind']==kind) and (not level or level in r['levels'])]
    return JsonResponse({'items':items,'checked_at':data['checked_at']})
