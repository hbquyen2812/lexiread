"""Prepare fake users and content in disposable Docker QA, never production."""
import os
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['DJANGO_SETTINGS_MODULE']='config.qa_settings'
import django
django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from learning.models import CuratedLesson, ToeicPractice
from learning.editorial.services import read_package, preview_import, apply_import, publish_batch, version_of, audit
from django.db import transaction

db=settings.DATABASES['default']
if not settings.QA_ONLY or (db['HOST'],db['NAME'],db['USER'])!=('qa-db','lexiread_qa','lexiread_qa'):
    raise SystemExit('Refusing to prepare a database that is not the disposable QA target.')
call_command('migrate',interactive=False)
call_command('seed_lessons')
call_command('seed_toeic')
User=get_user_model()
for name,staff in [('qa-editor',True),('qa-reader',False)]:
    user,_=User.objects.get_or_create(username=name)
    user.email=f'{name}@example.test'
    user.is_active=True
    user.is_staff=user.is_superuser=staff
    user.set_password('LexiRead-QA-2026!')
    user.save()
editor=User.objects.get(username='qa-editor')
source=root/'lexiread_data_v1/data/lessons.json'
if source.exists():
    for kind,model in [('lesson',CuratedLesson),('toeic',ToeicPractice)]:
        rows=read_package(SimpleUploadedFile('lessons.json',source.read_bytes()),kind,{})
        existing=set(model.objects.values_list('slug',flat=True))
        rows=[row for row in rows if row['slug'] not in existing]
        if rows:
            batch=preview_import(editor,kind,rows)
            _,count=apply_import(editor,batch.pk)
            print(f'QA: imported {count} {kind} drafts.')
    if '--publish-pack' in sys.argv:
        # QA publication only: this is NOT a claim of independent academic review.
        for kind,model in [('lesson',CuratedLesson),('toeic',ToeicPractice)]:
            adapted=read_package(SimpleUploadedFile('lessons.json',source.read_bytes()),kind,{})
            mapped={row['slug']:row for row in adapted}
            with transaction.atomic():
                for obj in model.objects.select_for_update().filter(pk__in=mapped,published=False):
                    if kind=='lesson' and not obj.content.get('analysis',{}).get('translations'):
                        obj.content.setdefault('translation_status','not_provided')
                    key='focus_vocabulary' if kind=='toeic' else 'vocabulary'
                    container=obj.content if kind=='toeic' else obj.content.get('analysis',{})
                    incoming=mapped[obj.pk] if kind=='toeic' else mapped[obj.pk]['analysis']
                    words={(w['word'],w.get('context','')):w for w in incoming[key]}
                    for word in container.get(key,[]):
                        source_word=words.get((word['word'],word.get('context','')),{})
                        for field in ('usage_pattern','paraphrases'):
                            if not word.get(field) and source_word.get(field): word[field]=source_word[field]
                    obj.full_clean();obj.save()
                    audit(editor,obj,False,'QA ONLY: bổ sung trường mới còn trống, giữ chỉnh sửa có sẵn.')
                expected={obj.pk:version_of(obj) for obj in model.objects.filter(pk__in=mapped,published=False)}
                count=publish_batch(editor,kind,expected) if expected else 0
                print(f'QA ONLY: published {count} {kind} mini-practices; not official exam papers.')
print(f'Published: {CuratedLesson.objects.filter(published=True).count()} readings; {ToeicPractice.objects.filter(published=True).count()} TOEIC sets.')
print('QA ONLY: http://127.0.0.1:8766/')
print('Learner email: qa-reader@example.test; admin email: qa-editor@example.test')
print('Django admin username: qa-editor')
print('Both disposable QA passwords: LexiRead-QA-2026!')
print('Never use these accounts/settings on a public deployment.')
