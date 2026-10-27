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
    user,created=User.objects.get_or_create(username=name)
    if not created: continue
    user.email=f'{name}@example.test'
    user.is_active=True
    user.is_staff=user.is_superuser=staff
    user.set_password('LexiRead-QA-2026!')
    user.save()
editor=User.objects.get(username='qa-editor')
call_command('seed_content_v3')
print(f'Published: {CuratedLesson.objects.filter(published=True).count()} readings; {ToeicPractice.objects.filter(published=True).count()} TOEIC sets.')
print('QA ONLY: http://127.0.0.1:8766/')
print('Learner email: qa-reader@example.test; admin email: qa-editor@example.test')
print('Django admin username: qa-editor')
print('Both disposable QA passwords: LexiRead-QA-2026!')
print('Never use these accounts/settings on a public deployment.')
