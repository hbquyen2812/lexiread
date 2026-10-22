import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from .core import validate_entry,fingerprint,schedule,InputError,validate_progress,clean_text,MAX_READING_CHARS
from ..models import Vocabulary,Reading,ReviewLog,LessonAttempt,ReadingQuestion
VOCAB_FIELDS=('word','pos','meaning_vi','synonyms','paraphrases','example','example_vi','context',
              'note','tags','source_label','origin','verified','interval_days','ease','repetitions','lapses')

def serial_vocab(v):
    data={key:getattr(v,key) for key in VOCAB_FIELDS}
    data.update(id=str(v.id),reading_id=str(v.reading_id) if v.reading_id else None,
        due_at=v.due_at.isoformat(),last_reviewed=v.last_reviewed.isoformat() if v.last_reviewed else None,
        due=v.due_at<=timezone.now(),created_at=v.created_at.isoformat())
    return data

def serial_reading(r,full=True):
    from .core import paragraphs
    progress=r.progress or {}
    data={'id':str(r.id),'title':r.title,'source_name':r.source_name,'word_count':len(r.text.split()),
          'updated_at':r.updated_at.isoformat(),'has_analysis':bool(r.analysis),
          'favorite':progress.get('favorite') is True,
          'status':'completed' if progress.get('completed') is True else 'in_progress'}
    data.update(catalog_slug=r.catalog_slug,progress=progress)
    if full:
        from .catalog import public_lesson
        data.update(text=r.text,paragraphs=paragraphs(r.text),analysis=r.analysis,lesson=public_lesson(r.lesson_snapshot))
    return data

def save_entry(user,data,reading=None):
    fields=validate_entry(data)
    fp=fingerprint(fields['word'],fields['meaning_vi'])
    # Duplicate import never overwrites a reviewed sense or resets the review schedule.
    v,created=Vocabulary.objects.get_or_create(owner=user,fingerprint=fp,defaults={**fields,'reading':reading})
    if not created:
        new_tags=list(dict.fromkeys(v.tags+fields['tags']))[:20]
        if new_tags!=v.tags:
            v.tags=new_tags;v.save(update_fields=['tags','updated_at'])
    return v,created

@transaction.atomic
def review_entry(user,vocab_id,rating,token,mode='flashcard',correct=None):
    # Serialize the user's reviews so duplicate browser retries are genuinely idempotent.
    get_user_model().objects.select_for_update().get(pk=user.pk)
    previous=ReviewLog.objects.filter(owner=user,token=token).first()
    if previous:
        if str(previous.vocabulary_id)!=str(vocab_id): raise InputError('Mã lượt ôn đã được dùng cho thẻ khác.')
        return {'duplicate':True,'due_at':previous.next_due.isoformat()}
    v=Vocabulary.objects.select_for_update().get(owner=user,pk=vocab_id)
    values=schedule({k:getattr(v,k) for k in ('interval_days','ease','repetitions','lapses')},rating)
    for key,value in values.items(): setattr(v,key,value)
    v.save(update_fields=[*values,'updated_at'])
    ReviewLog.objects.create(owner=user,vocabulary=v,token=token,rating=rating,mode=mode,correct=correct,next_due=v.due_at)
    return {'duplicate':False,'due_at':v.due_at.isoformat(),'interval_days':v.interval_days}

def export_library(user):
    return {'format':'lexiread-backup','version':2,'exported_at':timezone.now().isoformat(),
            'readings':[backup_reading(r) for r in Reading.objects.filter(owner=user)],
            'vocabulary':[serial_vocab(v) for v in Vocabulary.objects.filter(owner=user)],
            'reviews':[{'vocabulary_id':str(r.vocabulary_id),'token':str(r.token),'rating':r.rating,
              'mode':r.mode,'correct':r.correct,'next_due':r.next_due.isoformat(),'created_at':r.created_at.isoformat()}
              for r in ReviewLog.objects.filter(owner=user)]}

@transaction.atomic
def import_library(user,payload):
    """Merge-only restoration. Existing senses / schedules are deliberately preserved."""
    if isinstance(payload,list): payload={'vocabulary':payload}
    if not isinstance(payload,dict): raise InputError('Cần một danh sách từ hoặc một backup JSON.')
    is_backup=payload.get('format')=='lexiread-backup'
    if is_backup and payload.get('version') not in (1,2): raise InputError('Phiên bản backup chưa được hỗ trợ.')
    entries=payload.get('vocabulary',[]); readings=payload.get('readings',[]) if is_backup else []
    if not isinstance(entries,list) or len(entries)>5000 or not isinstance(readings,list) or len(readings)>100:
        raise InputError('Mỗi lần nhập tối đa 5.000 thẻ và 100 bài đọc.')
    # Validate all entries before any write; transaction also rolls back later errors.
    clean=[validate_entry(d) for d in entries]
    reading_map={};word_map={};new_readings=0;created=0
    from .analysis import validate_analysis
    for raw in readings:
        rid=str(raw.get('id',''))
        try: uuid.UUID(rid)
        except (ValueError,TypeError): raise InputError('ID bài đọc trong backup không hợp lệ.')
        title=clean_text(raw.get('title',''),200,True); text=clean_text(raw.get('text',''),MAX_READING_CHARS,True)
        slug=clean_text(raw.get('catalog_slug',''),100)
        r=Reading.objects.filter(owner=user,catalog_slug=slug).first() if slug else None
        if not r:r=Reading.objects.filter(owner=user,title=title,text=text).first()
        if not r:
            # Never trust an imported primary key: avoid clashes with other accounts.
            analysis=raw.get('analysis') or {}
            if analysis:
                basic={k:analysis[k] for k in ('translations','vocabulary','grammar') if k in analysis}
                # AI candidates in exported data also have app metadata: remove it.
                if 'vocabulary' in basic:
                    from .analysis import VOCAB_SCHEMA
                    basic['vocabulary']=[{k:v[k] for k in VOCAB_SCHEMA['properties']} for v in basic['vocabulary']]
                analysis=validate_analysis(basic,text)
            r=Reading.objects.create(owner=user,title=title,text=text,source_name=clean_text(raw.get('source_name',''),200),analysis=analysis)
            restore_reading_extras(r,raw)
            new_readings+=1
        reading_map[rid]=r
    for raw,fields in zip(entries,clean):
        fields['origin']='import'
        reading=reading_map.get(str(raw.get('reading_id','')))
        v,is_new=save_entry(user,fields,reading)
        if is_new and is_backup:
            progress=validate_progress(raw)
            for k,value in progress.items():setattr(v,k,value)
            v.save(update_fields=[*progress,'updated_at'])
        word_map[str(raw.get('id',''))]=v
        created+=int(is_new)
    imported_logs=0
    if is_backup:
        logs=payload.get('reviews',[])
        if not isinstance(logs,list) or len(logs)>100000:raise InputError('Backup có quá nhiều lượt ôn.')
        for log in logs:
            v=word_map.get(str(log.get('vocabulary_id','')))
            if not v:continue
            try:token=uuid.UUID(log['token'])
            except (KeyError,ValueError,TypeError):raise InputError('Mã lượt ôn trong backup không hợp lệ.')
            if log.get('rating') not in {'again','hard','good','easy'}:raise InputError('Mức ôn trong backup không hợp lệ.')
            dates=validate_progress({'due_at':log.get('next_due'),'last_reviewed':log.get('created_at')})
            correct=log.get('correct')
            if correct is not None and not isinstance(correct,bool):raise InputError('Kết quả ôn không hợp lệ.')
            rec,new=ReviewLog.objects.get_or_create(owner=user,token=token,defaults={'vocabulary':v,'rating':log['rating'],
                'mode':clean_text(log.get('mode','flashcard'),20),'correct':correct,'next_due':dates.get('due_at',timezone.now())})
            if new and dates.get('last_reviewed'):
                ReviewLog.objects.filter(pk=rec.pk).update(created_at=dates['last_reviewed'])
            imported_logs+=int(new)
    return {'created':created,'skipped':len(entries)-created,'readings_created':new_readings,'reviews_created':imported_logs}


def backup_reading(r):
    from .qa import source_hash
    current=source_hash(r.text)
    return {**serial_reading(r),'lesson_snapshot':r.lesson_snapshot,
        'lesson_attempts':[{'token':str(a.token),'answers':a.answers,'created_at':a.created_at.isoformat()}
                           for a in r.lesson_attempts.all()],
        'qa_history':[{'question':q.question,'selected_text':q.selected_text,'result':q.result,
                       'origin':q.origin,'created_at':q.created_at.isoformat()}
                      for q in r.questions.filter(source_hash=current)]}

def restore_reading_extras(r,raw):
    """Only for newly created user readings. Never creates/changes shared editorial content."""
    from .catalog import validate_lesson,clean_reading_progress,grade_lesson
    from .qa import validate_answer,source_hash,question_context
    snapshot=raw.get('lesson_snapshot') or {}
    if snapshot:
        snapshot=validate_lesson(snapshot)
        if snapshot['text']!=r.text or snapshot['title']!=r.title:raise InputError('Snapshot bài học không khớp nội dung backup.')
        r.lesson_snapshot=snapshot;r.catalog_slug=snapshot['slug'];r.analysis=snapshot['analysis']
    r.progress=clean_reading_progress(raw.get('progress',{}),r.text)
    attempts=raw.get('lesson_attempts',[])
    if not isinstance(attempts,list) or len(attempts)>10000:raise InputError('Quá nhiều lượt làm bài trong backup.')
    for a in attempts:
        result=grade_lesson(snapshot,a.get('answers'))
        token=uuid.UUID(a.get('token',''))
        rec,made=LessonAttempt.objects.get_or_create(reading=r,token=token,defaults={'answers':a['answers'],'result':result})
        if made:
            r.progress['quiz_best']=max(r.progress.get('quiz_best',0),result['score'])
            r.progress['quiz_total']=result['total'];r.progress['quiz_attempts']=r.progress.get('quiz_attempts',0)+1
    qs=raw.get('qa_history',[])
    if not isinstance(qs,list) or len(qs)>1000:raise InputError('Quá nhiều câu hỏi trong backup.')
    for q in qs:
        _,question,selected=question_context(r.text,q.get('question',''),q.get('selected_text',''))
        answer=validate_answer(q.get('result'),r.text)
        ReadingQuestion.objects.create(reading=r,question=question,selected_text=selected,result=answer,
            origin='import',source_hash=source_hash(r.text))
    r.save(update_fields=['catalog_slug','lesson_snapshot','analysis','progress','updated_at'])
