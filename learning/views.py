import csv
import hashlib
import ipaddress
import io
import json
import uuid
from datetime import timedelta
from functools import wraps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction,IntegrityError
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import (Reading,Vocabulary,ReviewLog,ExerciseAttempt,AICall,LoginFailure,
                     CuratedLesson,LessonAttempt,ReadingQuestion,VocabularyOccurrence)
from .models import ToeicAttempt
from .services.core import (InputError,clean_text,parse_json,validate_entry,fingerprint,normalise,
                            calculate_review_streak,MAX_READING_CHARS)
from .services.storage import (serial_vocab,serial_reading,save_entry,review_entry,
                               export_library,import_library,MAX_BACKUP_BYTES)
from .services.analysis import ANALYSIS_SCHEMA,ENTRY_SCHEMA,arr,obj,prompt_for_reading,prompt_for_word,validate_analysis,SYSTEM
from .services.exercises import build_question,MODES
from .services import ai
from .forms import EmailAuthenticationForm
from .services.presentation import cover_metadata
from .services.motivation import record_learning, study_summary

def api(*methods):
    def decorate(fn):
        @wraps(fn)
        def wrapped(request,*args,**kwargs):
            if not request.user.is_authenticated:return JsonResponse({'error':'Bạn cần đăng nhập lại.'},status=401)
            if request.method not in methods:return JsonResponse({'error':'Phương thức không được hỗ trợ.'},status=405)
            try:return fn(request,*args,**kwargs)
            except InputError as e:return JsonResponse({'error':str(e)},status=400)
            except (ValueError,TypeError,KeyError):return JsonResponse({'error':'Dữ liệu không hợp lệ. Kiểm tra các trường đã nhập.'},status=400)
            except (Vocabulary.DoesNotExist,Reading.DoesNotExist,ExerciseAttempt.DoesNotExist,CuratedLesson.DoesNotExist):return JsonResponse({'error':'Không tìm thấy dữ liệu trong tài khoản này.'},status=404)
            except IntegrityError:return JsonResponse({'error':'Dữ liệu trùng hoặc xung đột. Tải lại rồi thử lại.'},status=409)
        return wrapped
    return decorate

def body(request):
    if not request.body:return {}
    data=parse_json(request.body.decode('utf-8'))
    if not isinstance(data,dict):raise InputError('Nội dung gửi lên phải là đối tượng JSON.')
    return data

def login_key(request):
    address=request.META.get('REMOTE_ADDR','unknown')
    if settings.TRUST_PROXY_HTTPS and request.META.get('HTTP_X_FORWARDED_FOR'):
        address=request.META['HTTP_X_FORWARDED_FOR'].split(',',1)[0].strip()
    try:address=str(ipaddress.ip_address(address))
    except ValueError:address='unknown'
    return hashlib.sha256((settings.SECRET_KEY+address).encode()).hexdigest()

class EmailLoginView(LoginView):
    template_name='registration/login.html'
    authentication_form=EmailAuthenticationForm
    redirect_authenticated_user=True
    def get(self,request,*args,**kwargs):
        from .services.traffic import record_visit
        response=super().get(request,*args,**kwargs)
        record_visit(request,'login')
        return response
    def post(self,request,*args,**kwargs):
        cutoff=timezone.now()-timedelta(minutes=15)
        if LoginFailure.objects.filter(key=login_key(request),created_at__gte=cutoff).count()>=10:
            return render(request,self.template_name,{'form':self.get_form(),'throttled':True},status=429)
        return super().post(request,*args,**kwargs)
    def form_invalid(self,form):
        LoginFailure.objects.create(key=login_key(self.request))
        return super().form_invalid(form)
    def form_valid(self,form):
        LoginFailure.objects.filter(key=login_key(self.request)).delete()
        return super().form_valid(form)

@ensure_csrf_cookie
def index(request):
    from .services.traffic import record_visit
    from .services.public_resources import public_resources
    from .services.strategy_guides import strategy_guides
    from .services.learning_channels import learning_channels
    record_visit(request,'home')
    resources=public_resources()
    if request.user.is_authenticated:return render(request,'app.html',{'official_resources':resources,'strategy_guides':strategy_guides(),'learning_channels':learning_channels()})
    from .services.toeic_repository import toeic_sets
    lessons=[]
    for lesson in CuratedLesson.objects.filter(published=True).order_by('order','title'):
        content=lesson.content or {}
        lessons.append({'slug':lesson.slug,'title':lesson.title,'level':lesson.level,'topic':lesson.topic,
            'track':content.get('track','general'),'translation_status':content.get('translation_status','complete'),
            **cover_metadata(lesson.topic,lesson.title),
            'summary':content.get('summary',''),'word_count':len(content.get('text','').split()),
            'question_count':len(content.get('questions',[])),
            'vocabulary_count':len(content.get('analysis',{}).get('vocabulary',[]))})
    practices=[{key:practice[key] for key in ('slug','title','mode_label','parts','level','duration_minutes','description','question_count')}
        for practice in toeic_sets()]
    return render(request,'landing.html',{'lessons':lessons,'practices':practices,'official_resources':resources,
        'topic_count':len({lesson['topic'] for lesson in lessons}),
        'general_count':sum(x['track']=='general' for x in lessons),
        'ielts_count':sum(x['track']=='ielts' for x in lessons)})

def health(request):
    from django.db import connection
    try:
        with connection.cursor() as c:c.execute('SELECT 1')
        return JsonResponse({'status':'ok'})
    except Exception:return JsonResponse({'status':'database-unavailable'},status=503)

def guides(request):
    from .services.strategy_guides import strategy_guides
    from .services.learning_channels import learning_channels
    return render(request,'guides.html',{'strategy_guides':strategy_guides(),'learning_channels':learning_channels()})

def filtered_vocab(request):
    qs=Vocabulary.objects.filter(owner=request.user)
    q=request.GET.get('q','')[:200].strip()
    if q:qs=qs.filter(Q(word__icontains=q)|Q(meaning_vi__icontains=q)|Q(note__icontains=q)|
                      Q(source_label__icontains=q)|Q(context__icontains=q)|Q(example__icontains=q))
    if request.GET.get('tag'):qs=qs.filter(tags__contains=[request.GET['tag'][:300]])
    scope=request.GET.get('scope','all')
    now=timezone.now()
    if scope=='due':qs=qs.filter(due_at__lte=now)
    elif scope=='overdue':qs=qs.filter(due_at__lte=now-timedelta(days=1))
    elif scope=='new':qs=qs.filter(last_reviewed__isnull=True)
    elif scope=='learning':qs=qs.filter(last_reviewed__isnull=False,interval_days__lt=21)
    elif scope=='mastered':qs=qs.filter(interval_days__gte=21)
    elif scope=='weak':qs=qs.filter(lapses__gte=3)
    elif scope=='mistakes':qs=qs.filter(lapses__gt=0)
    elif scope=='unchecked':qs=qs.filter(verified=False)
    elif scope!='all':raise InputError('Phạm vi từ vựng không hợp lệ.')
    if request.GET.get('reading'):
        reading_id=uuid.UUID(request.GET['reading'])
        qs=qs.filter(Q(reading_id=reading_id)|Q(occurrences__reading_id=reading_id)).distinct()
    sort=request.GET.get('sort','')
    if sort=='due':qs=qs.order_by('due_at','created_at')
    elif sort=='newest':qs=qs.order_by('-created_at','-id')
    elif sort=='oldest':qs=qs.order_by('created_at','id')
    elif sort=='word':qs=qs.order_by(Lower('word'),'id')
    elif sort:raise InputError('Cách sắp xếp từ vựng không hợp lệ.')
    elif scope in {'due','overdue'}:qs=qs.order_by('due_at','created_at')
    elif scope in {'weak','mistakes'}:qs=qs.order_by('-lapses','due_at')
    return qs

@api('GET')
def bootstrap(request):
    vs=Vocabulary.objects.filter(owner=request.user); now=timezone.now()
    logs=ReviewLog.objects.filter(owner=request.user)
    today=timezone.localdate()
    reviews_today=logs.filter(created_at__date=today).count()
    daily_goal=20
    review_days=logs.order_by().values_list('created_at__date',flat=True).distinct()
    review_streak=calculate_review_streak(review_days,today)
    quiz=logs.filter(correct__isnull=False)
    n=quiz.count();good=quiz.filter(correct=True).count()
    tags=sorted({tag for row in vs.values_list('tags',flat=True) for tag in row})
    days=[]
    for i in range(6,-1,-1):
        d=today-timedelta(days=i)
        days.append({'date':d.isoformat(),'label':d.strftime('%d/%m'),'count':logs.filter(created_at__date=d).count()})
    from .services.traffic import personal_activity
    activity=personal_activity(request.user);toeic=ToeicAttempt.objects.filter(owner=request.user)
    study=study_summary(request.user)
    return JsonResponse({'user':request.user.get_full_name().strip() or request.user.get_username(),'is_staff':request.user.is_staff,'ai_enabled':ai.enabled(),
        'model':settings.OPENAI_MODEL if ai.enabled() else '',
        'ai_calls_today':AICall.objects.filter(owner=request.user,created_at__date=today).count(),
        'ai_daily_limit':settings.AI_DAILY_LIMIT,'stats':{'total':vs.count(),'due':vs.filter(due_at__lte=now).count(),
        'new':vs.filter(last_reviewed__isnull=True).count(),
        'learning':vs.filter(last_reviewed__isnull=False,interval_days__lt=21).count(),
        'mastered':vs.filter(interval_days__gte=21).count(),
        'weak':vs.filter(lapses__gte=3).count(),
        'overdue':vs.filter(due_at__lte=now-timedelta(days=1)).count(),
        'readings':Reading.objects.filter(owner=request.user,catalog_slug='').count(),'lessons':CuratedLesson.objects.filter(published=True).count(),'completed_readings':Reading.objects.filter(owner=request.user,progress__completed=True).count(),'reviews_today':reviews_today,
        'review_streak':review_streak,'study':study,'daily_goal':daily_goal,
        'daily_goal_progress':min(reviews_today,daily_goal),
        'daily_goal_percent':min(100,round(100*reviews_today/daily_goal)),
        'mistakes':vs.filter(lapses__gt=0).count(),'accuracy':round(100*good/n) if n else None,
        'active_days_30':study['active_days_30'],'page_views_today':activity['page_views_today'],
        'toeic_attempts':toeic.count(),'toeic_best':max((row.get('score',0) for row in toeic.values_list('result',flat=True)),default=None)},'tags':tags,'activity':days})

@api('POST')
def activity_visit(request):
    from .services.traffic import record_visit
    page=body(request).get('page','')
    row=record_visit(request,page)
    return JsonResponse({'recorded':True,'views_today':row.views})

@api('GET')
def analytics(request):
    if not request.user.is_staff:return JsonResponse({'error':'Chỉ quản trị viên được xem thống kê tổng.'},status=403)
    from .services.traffic import traffic_summary
    try:days=int(request.GET.get('days',30))
    except (TypeError,ValueError):raise InputError('Số ngày thống kê không hợp lệ.')
    return JsonResponse(traffic_summary(days))

@api('GET','POST')
def readings(request):
    if request.method=='GET':
        qs=Reading.objects.filter(owner=request.user,catalog_slug='')
        q=clean_text(request.GET.get('q',''),200)
        if q:qs=qs.filter(Q(title__icontains=q)|Q(source_name__icontains=q)|Q(text__icontains=q))
        status=request.GET.get('status','all')
        if status=='completed':qs=qs.filter(progress__completed=True)
        elif status=='in_progress':qs=qs.filter(Q(progress__completed=False)|~Q(progress__has_key='completed'))
        elif status!='all':raise InputError('Trạng thái bài đọc không hợp lệ.')
        favorite=request.GET.get('favorite','all')
        if favorite=='yes':qs=qs.filter(progress__favorite=True)
        elif favorite=='no':qs=qs.filter(Q(progress__favorite=False)|~Q(progress__has_key='favorite'))
        elif favorite!='all':raise InputError('Bộ lọc yêu thích không hợp lệ.')
        sort=request.GET.get('sort','updated')
        if sort=='updated':qs=qs.order_by('-updated_at','-created_at','id')
        elif sort=='newest':qs=qs.order_by('-created_at','id')
        elif sort=='oldest':qs=qs.order_by('created_at','id')
        elif sort=='title':qs=qs.order_by(Lower('title'),'id')
        else:raise InputError('Cách sắp xếp bài đọc không hợp lệ.')
        try:page=int(request.GET.get('page',1));limit=int(request.GET.get('limit',24))
        except (TypeError,ValueError):raise InputError('Trang và số mục mỗi trang phải là số nguyên.')
        if page<1 or not 1<=limit<=100:raise InputError('Trang phải từ 1; mỗi trang cho phép 1–100 bài.')
        total=qs.count();start=(page-1)*limit
        return JsonResponse({'items':[serial_reading(r,False) for r in qs[start:start+limit]],
                             'total':total,'page':page,'limit':limit})
    if request.FILES:
        from .services.importers import extract_reading
        upload=request.FILES.get('file')
        if not upload:raise InputError('Chưa chọn file.')
        text=extract_reading(upload);title=clean_text(request.POST.get('title') or upload.name,200,True)
        source=clean_text(upload.name,200)
    else:
        data=body(request);text=clean_text(data.get('text',''),MAX_READING_CHARS,True)
        title=clean_text(data.get('title',''),200,True);source=clean_text(data.get('source_name',''),200)
    r=Reading.objects.create(owner=request.user,title=title,text=text,source_name=source)
    return JsonResponse(serial_reading(r),status=201)

@api('GET','PATCH','DELETE')
def reading_detail(request,pk):
    r=Reading.objects.get(owner=request.user,pk=pk)
    if request.method=='DELETE':r.delete();return JsonResponse({'deleted':True})
    if request.method=='PATCH':
        if r.catalog_slug:raise InputError('Bài soạn sẵn là bản học cố định. Không sửa nội dung chuẩn trong khu vực cá nhân.')
        data=body(request)
        r.title=clean_text(data.get('title',r.title),200,True)
        new_text=clean_text(data.get('text',r.text),MAX_READING_CHARS,True)
        if new_text!=r.text:
            r.analysis={}
            r.progress={'favorite':True} if r.progress.get('favorite') is True else {}
        r.text=new_text;r.save()
    return JsonResponse(serial_reading(r))

@api('GET','POST')
def vocabulary(request):
    if request.method=='GET':
        qs=filtered_vocab(request)
        try:page=int(request.GET.get('page',1));limit=int(request.GET.get('limit',24))
        except (TypeError,ValueError):raise InputError('Trang và số mục mỗi trang phải là số nguyên.')
        if page<1 or not 1<=limit<=500:raise InputError('Trang phải từ 1; mỗi trang cho phép 1–500 thẻ.')
        total=qs.count();start=(page-1)*limit
        return JsonResponse({'items':[serial_vocab(v) for v in qs[start:start+limit]],'total':total,'page':page,'limit':limit})
    data=body(request);items=data.get('items',[data])
    if not isinstance(items,list) or not 1<=len(items)<=100:raise InputError('Mỗi lần lưu 1–100 thẻ.')
    clean=[validate_entry(i) for i in items]
    reading=None
    if data.get('reading_id'):reading=Reading.objects.get(owner=request.user,pk=data['reading_id'])
    made=[];created=0
    with transaction.atomic():
        for v in clean:
            if reading and not v['source_label']:v['source_label']=reading.title
            word,new=save_entry(request.user,v,reading);made.append(serial_vocab(word));created+=int(new)
    return JsonResponse({'items':made,'created':created,'skipped':len(items)-created},status=201)

@api('GET','POST')
def personal_deck(request):
    from .services.personal_decks import validate_deck,pack,MAX_ITEMS,MAX_BYTES
    if request.method=='GET':
        name=clean_text(request.GET.get('name',''),100,True)
        words=[serial_vocab(v) for v in Vocabulary.objects.filter(owner=request.user) if name in v.tags]
        if not words:raise InputError('Chưa có từ nào trong bộ này.')
        if len(words)>MAX_ITEMS:raise InputError('Bộ này có hơn 500 từ. Bạn có thể xuất toàn bộ kho ở phần Sao lưu.')
        result=pack(name,words)
        if len(json.dumps(result,ensure_ascii=False,indent=2).encode('utf-8'))>MAX_BYTES-1024:
            raise InputError('Bộ từ quá lớn để nhập lại trong một file. Bạn chia nhỏ bộ hoặc dùng sao lưu toàn bộ kho nhé.')
        return JsonResponse(result)
    if len(request.body)>MAX_BYTES:raise InputError('File quá lớn. Mỗi lần nhập tối đa 2 MB.')
    data=body(request)
    if type(data.get('preview')) is not bool:raise InputError('Hãy xem trước bộ từ rồi chọn lưu vào kho.')
    name,items,duplicates=validate_deck(data.get('deck'))
    fingerprints=[fingerprint(v['word'],v['meaning_vi']) for v in items]
    if data['preview']:
        existing=set(Vocabulary.objects.filter(owner=request.user,fingerprint__in=fingerprints).values_list('fingerprint',flat=True))
        return JsonResponse({'name':name,'items':[{**v,'exists':fp in existing} for v,fp in zip(items,fingerprints)],
            'new':sum(fp not in existing for fp in fingerprints),'existing':sum(fp in existing for fp in fingerprints),
            'duplicates':duplicates})
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        existing=Vocabulary.objects.filter(owner=request.user,fingerprint__in=fingerprints)
        if any(name not in v.tags and len(v.tags)>=20 for v in existing):
            raise InputError('Một từ trùng đã có 20 nhãn. Bớt nhãn của từ đó hoặc bỏ chọn từ trước khi nhập.')
        created=0
        for fields in items:
            _,new=save_entry(request.user,fields)
            created+=int(new)
    return JsonResponse({'name':name,'created':created,'existing':len(items)-created,'duplicates':duplicates,'total':len(items)},status=201)


@api('GET')
def vocabulary_sources(request):
    rows=VocabularyOccurrence.objects.filter(owner=request.user,reading__isnull=False).values(
        'reading_id','reading__title').distinct().order_by('reading__title','reading_id')
    items=[{'id':str(row['reading_id']),'title':row['reading__title']} for row in rows]
    return JsonResponse({'items':items})

@api('PATCH','DELETE')
def vocabulary_detail(request,pk):
    v=Vocabulary.objects.get(owner=request.user,pk=pk)
    if request.method=='DELETE':v.delete();return JsonResponse({'deleted':True})
    fields=validate_entry({**serial_vocab(v),**body(request)})
    fp=fingerprint(fields['word'],fields['meaning_vi'])
    if Vocabulary.objects.filter(owner=request.user,fingerprint=fp).exclude(pk=pk).exists():raise InputError('Nghĩa này đã có trong kho. Không gộp tự động để tránh mất tiến độ.')
    for k,value in fields.items():setattr(v,k,value)
    v.fingerprint=fp;v.save()
    return JsonResponse(serial_vocab(v))

@api('POST')
def review(request,pk):
    data=body(request);token=uuid.UUID(data.get('token',''))
    result=review_entry(request.user,pk,data.get('rating'),token)
    return JsonResponse(result)

@api('GET')
def next_exercise(request):
    mode=request.GET.get('mode','meaning')
    # Avoid a closed session repeatedly returning the same word.
    qs=filtered_vocab(request)
    exclude=[uuid.UUID(v) for v in request.GET.get('exclude','').split(',')[:100] if v]
    pool=[serial_vocab(v) for v in qs[:1000]]
    chosen,question,answer=build_question(pool,mode,exclude=[str(v) for v in exclude])
    attempt=ExerciseAttempt.objects.create(owner=request.user,vocabulary_id=chosen['id'],mode=mode,question=question,correct_answer=answer)
    return JsonResponse({'id':str(attempt.pk),'word_id':chosen['id'],**question})

@api('POST')
@transaction.atomic
def answer_exercise(request,pk):
    a=ExerciseAttempt.objects.select_for_update().get(owner=request.user,pk=pk)
    if a.created_at<timezone.now()-timedelta(hours=2):raise InputError('Câu hỏi đã hết hạn. Bắt đầu lượt mới.')
    data=body(request);value=clean_text(data.get('answer',''),2000,True)
    if not a.answered:
        if a.mode!='typing' and value not in a.question.get('options',[]):raise InputError('Đáp án không thuộc các lựa chọn của câu hỏi.')
        a.correct=normalise(value)==normalise(a.correct_answer)
        a.answered=True;a.submitted_answer=value;a.save(update_fields=['correct','answered','submitted_answer'])
        review_entry(request.user,a.vocabulary_id,'good' if a.correct else 'again',a.id,mode=a.mode,correct=a.correct)
    v=a.vocabulary
    return JsonResponse({'correct':a.correct,'answer':a.correct_answer,'submitted_answer':a.submitted_answer,
                         'note':v.note,'meaning_vi':v.meaning_vi,'word':v.word})

def reserve_ai(request,task):
    if not ai.enabled():raise InputError('Chưa bật API; dùng Copy prompt và Dán JSON hoặc cấu hình .env.')
    data=body(request)
    if data.get('allow_cloud') is not True:raise InputError('Cần đồng ý gửi phần nội dung này tới nhà cung cấp AI.')
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        calls=AICall.objects.filter(owner=request.user,created_at__date=timezone.localdate())
        if calls.count()>=settings.AI_DAILY_LIMIT:raise InputError('Đã đạt giới hạn gọi AI trong ngày của ứng dụng.')
        if calls.filter(created_at__gte=timezone.now()-timedelta(seconds=5)).exists():raise InputError('Vui lòng không gửi hai yêu cầu AI quá sát nhau.')
        return AICall.objects.create(owner=request.user,task=task,model=settings.OPENAI_MODEL)

def do_ai(request,task,prompt,schema,max_tokens=12000):
    log=reserve_ai(request,task)
    try:
        result=ai.request_json(prompt,schema,task,max_tokens)
    except Exception:
        log.status='failed';log.save(update_fields=['status']);raise
    log.status='completed';log.save(update_fields=['status']);return result

@api('POST')
def analyse_reading(request,pk):
    r=Reading.objects.get(owner=request.user,pk=pk);data=body(request)
    if r.catalog_slug:raise InputError('Bài soạn sẵn đã có bản dịch và gợi ý cố định. Dùng Hỏi đáp để giải thích thêm.')
    # Manual imports pass through exactly the same schema and grounding checks.
    if 'result' in data:raw=parse_json(data['result']) if isinstance(data['result'],str) else data['result']
    else:raw=do_ai(request,'reading',prompt_for_reading(r.text),ANALYSIS_SCHEMA)
    analysis=validate_analysis(raw,r.text)
    latest=Reading.objects.get(owner=request.user,pk=pk)
    if latest.text!=r.text:raise InputError('Bài đọc đã được sửa trong lúc phân tích. Không lưu kết quả cũ.')
    latest.analysis=analysis;latest.save(update_fields=['analysis','updated_at'])
    return JsonResponse(serial_reading(latest))

@api('POST')
def prompts(request):
    params=body(request)  # Keep passages/word contexts out of URL/access logs.
    task=params.get('task','reading')
    if task=='reading':
        r=Reading.objects.get(owner=request.user,pk=params.get('reading_id'))
        p=prompt_for_reading(r.text)
    elif task=='question':
        from .services.qa import prompt_for_question
        r=Reading.objects.get(owner=request.user,pk=params.get('reading_id'))
        p=prompt_for_question(r.text,params.get('question',''),params.get('selected_text',''))
    elif task=='word':
        p=prompt_for_word(clean_text(params.get('word',''),160,True),clean_text(params.get('context',''),4000))
    elif task=='words':
        text=clean_text(params.get('text',''),6000,True)
        p=words_prompt(text)
    else:raise InputError('Loại prompt không hợp lệ.')
    return JsonResponse({'prompt':p})

def words_prompt(text):
    schema=obj({'vocabulary':arr(ENTRY_SCHEMA)})
    return SYSTEM+'\nTASK: Produce a study entry for each item below (at most 50). Fix obvious typos, preserving that correction in note. For ambiguous words pick one common sense and say context is absent. Do not treat user-supplied equals signs as proof of equivalence. Explain misleading synonym pairs. Use blank context and fill short examples. Return schema:\n'+json.dumps(schema,ensure_ascii=False)+'\nSTUDY DATA:\n'+json.dumps({'word_list':text},ensure_ascii=False)

@api('POST')
def lookup(request):
    data=body(request);word=clean_text(data.get('word',''),160,True);context=clean_text(data.get('context',''),4000)
    if data.get('reading_id'):Reading.objects.get(owner=request.user,pk=data['reading_id'])
    result=do_ai(request,'word',prompt_for_word(word,context),ENTRY_SCHEMA,2000)
    v=validate_entry(result);v.update(origin='ai',verified=False)
    return JsonResponse(v)

@api('POST')
def enrich_words(request):
    text=clean_text(body(request).get('text',''),6000,True)
    if len([x for x in text.splitlines() if x.strip()])>50:raise InputError('Tối đa 50 dòng từ một lần.')
    schema=obj({'vocabulary':arr(ENTRY_SCHEMA)})
    result=do_ai(request,'words',words_prompt(text),schema,12000)
    if len(result['vocabulary'])>60:raise InputError('AI trả quá nhiều mục. Chưa lưu dữ liệu.')
    return JsonResponse({'vocabulary':[{**validate_entry(v),'origin':'ai','verified':False} for v in result['vocabulary']]})

@api('GET')
def backup(request):
    data=export_library(request.user)
    raw=json.dumps(data,ensure_ascii=False,indent=2)
    if len(raw.encode('utf-8'))>MAX_BACKUP_BYTES:
        raise InputError('Backup vượt 8 MB nên không thể bảo đảm nhập lại qua ứng dụng. Hãy dùng pg_dump cho database này.')
    response=HttpResponse(raw,content_type='application/json; charset=utf-8')
    response['Content-Disposition']='attachment; filename="lexiread-backup.json"'
    return response

@api('GET')
def export_csv(request):
    out=io.StringIO(newline='');writer=csv.writer(out)
    fields=['word','pos','meaning_vi','synonyms','paraphrases','usage_pattern','example','example_vi','context','note','tags']
    writer.writerow(fields)
    for v in Vocabulary.objects.filter(owner=request.user):
        row=[]
        for key in fields:
            value=getattr(v,key);s=' | '.join(value) if isinstance(value,list) else str(value)
            # Protect spreadsheet readers from CSV formula injection.
            if s.lstrip().startswith(('=','+','-','@','\t','\r')):s="'"+s
            row.append(s)
        writer.writerow(row)
    response=HttpResponse('\ufeff'+out.getvalue(),content_type='text/csv; charset=utf-8')
    response['Content-Disposition']='attachment; filename="lexiread-vocabulary.csv"';return response

@api('POST')
def restore(request):
    if request.FILES:
        f=request.FILES.get('file')
        if not f or f.size>MAX_BACKUP_BYTES:raise InputError('Chọn file JSON/CSV không quá 8 MB.')
        raw=f.read().decode('utf-8-sig')
        if f.name.lower().endswith('.csv'):
            reader=csv.DictReader(io.StringIO(raw));payload=[]
            for i,row in enumerate(reader):
                if i>=5000:raise InputError('CSV tối đa 5.000 dòng.')
                payload.append({k:(v or '') for k,v in row.items()})
        else:payload=parse_json(raw)
    else:payload=body(request).get('data',{})
    return JsonResponse(import_library(request.user,payload))


@api('GET')
def toeic_catalog(request):
    from .services.toeic_repository import toeic_sets
    attempts=ToeicAttempt.objects.filter(owner=request.user)
    items=[]
    for practice in toeic_sets():
        rows=attempts.filter(set_slug=practice['slug'],snapshot__revision=practice['revision'])
        best=max((row.result.get('score',0) for row in rows),default=None)
        latest=rows.first()
        items.append({k:practice[k] for k in ('slug','title','mode','mode_label','parts','level','duration_minutes','description','question_count')}|{
            'attempt_count':rows.count(),'best_score':best,
            'latest_score':latest.result.get('score') if latest else None,
            'latest_at':latest.created_at.isoformat() if latest else None})
    return JsonResponse({'items':items,'official_format':{
        'reading_minutes':75,'reading_questions':100,
        'parts':[{'part':5,'name':'Incomplete Sentences','questions':30},
                 {'part':6,'name':'Text Completion','questions':16},
                 {'part':7,'name':'Reading Comprehension','questions':54}],
        'note':'Bộ luyện trong LexiRead là nội dung tự biên soạn theo dạng bài, không phải đề ETS chính thức và không quy đổi điểm TOEIC.'}})


@api('GET')
def toeic_detail(request,slug):
    from .services.toeic_repository import public_toeic_set
    practice=public_toeic_set(slug)
    rows=ToeicAttempt.objects.filter(owner=request.user,set_slug=slug,snapshot__revision=practice['revision'])
    best=max((row.result.get('score',0) for row in rows),default=None)
    practice['progress']={'attempt_count':rows.count(),'best_score':best}
    return JsonResponse(practice)


@api('POST')
@transaction.atomic
def toeic_submit(request,slug):
    from .services.toeic_repository import get_toeic_set
    from .services.toeic import grade_toeic
    data=body(request);token=uuid.UUID(data.get('token',''))
    get_user_model().objects.select_for_update().get(pk=request.user.pk)
    previous=ToeicAttempt.objects.filter(owner=request.user,token=token).first()
    if previous:
        if previous.set_slug!=slug:raise InputError('Mã lượt làm bài đã được dùng cho bộ khác.')
        return JsonResponse({**previous.result,'duplicate':True})
    practice=get_toeic_set(slug)
    if data.get('revision',1)!=practice['revision']:
        raise InputError('Bộ luyện đã được cập nhật. Tải lại trang và bắt đầu lượt mới để không chấm nhầm phiên bản.')
    duration=data.get('duration_seconds',0)
    if not isinstance(duration,int) or isinstance(duration,bool) or not 0<=duration<=7200:
        raise InputError('Thời gian làm bài không hợp lệ.')
    result=grade_toeic(practice,data.get('answers'))
    ToeicAttempt.objects.create(owner=request.user,set_slug=slug,token=token,answers=data['answers'],
        result=result,duration_seconds=duration,snapshot=practice)
    record_learning(request.user)
    return JsonResponse({**result,'duplicate':False})


@api('GET')
def catalog(request):
    qs=CuratedLesson.objects.filter(published=True)
    track=request.GET.get('track','')
    if track not in {'','general','ielts'}:raise InputError('Loại bài đọc không hợp lệ.')
    if track:qs=qs.filter(track=track)
    q=clean_text(request.GET.get('q',''),200)
    if q:qs=qs.filter(Q(title__icontains=q)|Q(topic__icontains=q))
    if request.GET.get('level'):qs=qs.filter(level=request.GET['level'][:6])
    if request.GET.get('topic'):qs=qs.filter(topic=request.GET['topic'][:120])
    kind=request.GET.get('kind','')
    if kind:
        if kind not in {'main_idea','detail','tfng','ynng','vocabulary','inference','matching_heading','matching_information','gap_fill','short_answer'}:
            raise InputError('Dạng câu hỏi không hợp lệ.')
        matched=[lesson.pk for lesson in qs.only('slug','content') if any(q.get('kind')==kind for q in lesson.content.get('questions',[]))]
        qs=qs.filter(pk__in=matched)
    favorite=request.GET.get('favorite','all')
    if favorite not in {'all','yes','no'}:raise InputError('Bộ lọc yêu thích không hợp lệ.')
    personal=Reading.objects.filter(owner=request.user).exclude(catalog_slug='')
    status_filter=request.GET.get('status','')
    if status_filter not in {'','new','started','completed'}:raise InputError('Bộ lọc trạng thái không hợp lệ.')
    completed=personal.filter(progress__completed=True).values('catalog_slug')
    favorites=personal.filter(progress__favorite=True).values('catalog_slug')
    if status_filter=='new':qs=qs.exclude(slug__in=personal.values('catalog_slug'))
    elif status_filter=='completed':qs=qs.filter(slug__in=completed)
    elif status_filter=='started':qs=qs.filter(slug__in=personal.values('catalog_slug')).exclude(slug__in=completed)
    if favorite=='yes':qs=qs.filter(slug__in=favorites)
    elif favorite=='no':qs=qs.exclude(slug__in=favorites)
    page=max(1,int(request.GET.get('page',1)))
    limit=max(1,min(300,int(request.GET.get('limit',300))))
    total=qs.count()
    selected=list(qs[(page-1)*limit:page*limit])
    progress={r.catalog_slug:r for r in personal.filter(catalog_slug__in=[lesson.slug for lesson in selected])}
    items=[]
    for lesson in selected:
        r=progress.get(lesson.slug); c=lesson.content
        lesson_track=c.get('track','general')
        item={'slug':lesson.slug,'title':lesson.title,'level':lesson.level,'topic':lesson.topic,
            'track':lesson_track,'translation_status':c.get('translation_status','complete'),
            **cover_metadata(lesson.topic,lesson.title),
            'summary':c.get('summary',''),'revision':lesson.revision,'order':lesson.order,
            'word_count':len(c.get('text','').split()),'question_count':len(c.get('questions',[])),
            'question_types':sorted({q.get('kind') for q in c.get('questions',[]) if q.get('kind')}),
            'estimated_minutes':max(5,round(len(c.get('text','').split())/120+len(c.get('questions',[]))*.75)),
            'vocabulary_count':len(c.get('analysis',{}).get('vocabulary',[])),
            'reading_id':str(r.pk) if r else None,'progress':r.progress if r else {},
            'favorite':bool(r and r.progress.get('favorite') is True)}
        status='completed' if item['progress'].get('completed') else 'started' if r else 'new'
        item['status']=status
        items.append(item)
    return JsonResponse({'items':items,'total':total,'page':page,'limit':limit,'has_more':page*limit<total,
                         'topics':sorted(set(CuratedLesson.objects.filter(published=True,**({'track':track} if track else {})).values_list('topic',flat=True)))})

@api('POST')
def open_lesson(request,slug):
    lesson=CuratedLesson.objects.get(slug=slug,published=True)
    from .services.catalog import validate_lesson
    snapshot=validate_lesson(lesson.content)
    r,created=Reading.objects.get_or_create(owner=request.user,catalog_slug=slug,
        defaults={'title':snapshot['title'],'text':snapshot['text'],'source_name':'LexiRead · bài soạn sẵn',
                  'analysis':snapshot['analysis'],'lesson_snapshot':snapshot,'progress':{'paragraph':0,'completed':False}})
    return JsonResponse(serial_reading(r),status=201 if created else 200)

@api('POST')
@transaction.atomic
def reading_progress(request,pk):
    from .services.catalog import clean_reading_progress
    r=Reading.objects.select_for_update().get(owner=request.user,pk=pk)
    values=clean_reading_progress(body(request),r.text)
    if values.get('completed') is True and r.progress.get('completed') is not True:
        record_learning(request.user)
    r.progress={**r.progress,**values};r.save(update_fields=['progress','updated_at'])
    return JsonResponse({'progress':r.progress})

@api('POST')
@transaction.atomic
def reading_quiz(request,pk):
    from .services.catalog import grade_lesson
    r=Reading.objects.select_for_update().get(owner=request.user,pk=pk)
    d=body(request);token=uuid.UUID(d.get('token',''))
    previous=LessonAttempt.objects.filter(reading=r,token=token).first()
    if previous:return JsonResponse({**previous.result,'duplicate':True,'progress':r.progress})
    result=grade_lesson(r.lesson_snapshot,d.get('answers'))
    LessonAttempt.objects.create(reading=r,token=token,answers=d['answers'],result=result)
    record_learning(request.user)
    best=max(int(r.progress.get('quiz_best',0)),result['score'])
    r.progress={**r.progress,'quiz_best':best,'quiz_total':result['total'],
                'quiz_attempts':int(r.progress.get('quiz_attempts',0))+1}
    r.save(update_fields=['progress','updated_at'])
    return JsonResponse({**result,'duplicate':False,'progress':r.progress})

@api('GET','POST')
def reading_questions(request,pk):
    from .services.qa import QA_SCHEMA,prompt_for_question,validate_answer,question_context,source_hash
    r=Reading.objects.get(owner=request.user,pk=pk)
    current_hash=source_hash(r.text)
    if request.method=='GET':
        items=ReadingQuestion.objects.filter(reading=r,source_hash=current_hash)[:30]
        return JsonResponse({'items':[{'id':q.pk,'question':q.question,'selected_text':q.selected_text,
            'result':q.result,'origin':q.origin,'created_at':q.created_at.isoformat()} for q in items]})
    d=body(request)
    _,question,selected=question_context(r.text,d.get('question',''),d.get('selected_text',''))
    if 'result' in d:
        raw=parse_json(d['result']) if isinstance(d['result'],str) else d['result'];origin='manual'
    else:
        raw=do_ai(request,'question',prompt_for_question(r.text,question,selected),QA_SCHEMA,4000);origin='ai'
    result=validate_answer(raw,r.text)
    with transaction.atomic():
        latest=Reading.objects.select_for_update().get(owner=request.user,pk=pk)
        if source_hash(latest.text)!=current_hash:raise InputError('Bài đọc đã đổi trong lúc hỏi. Chưa lưu kết quả cũ.')
        q=ReadingQuestion.objects.create(reading=latest,question=question,selected_text=selected,
            result=result,source_hash=current_hash,origin=origin)
    return JsonResponse({'id':q.pk,'question':q.question,'selected_text':q.selected_text,
        'result':q.result,'origin':q.origin,'created_at':q.created_at.isoformat()},status=201)
