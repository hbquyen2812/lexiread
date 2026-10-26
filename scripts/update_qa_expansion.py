"""Apply reviewed bundled revisions only to the disposable QA database."""
import json
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
from django.db import transaction
from learning.models import CuratedLesson,ToeicPractice
from learning.editorial.services import audit
from learning.services.catalog import validate_lesson
from learning.services.toeic import validate_toeic_set

db=settings.DATABASES['default']
if not settings.QA_ONLY or (db['HOST'],db['NAME'],db['USER'])!=('qa-db','lexiread_qa','lexiread_qa'):
    raise SystemExit('This script only updates the disposable Docker QA database.')
editor=get_user_model().objects.get(username='qa-editor',is_superuser=True)
count=0
with transaction.atomic():
    for folder,model,validate in [('lessons',CuratedLesson,validate_lesson),('toeic',ToeicPractice,validate_toeic_set)]:
        for path in (root/'data'/folder).glob('*.json'):
            content=json.loads(path.read_text(encoding='utf-8'))
            if content.get('revision')!=2:continue
            content=validate(content)
            obj=model.objects.select_for_update().get(pk=content['slug'])
            if obj.content==content:continue
            if obj.revision>=content['revision']:
                raise RuntimeError(f'{obj.pk}: unexpected existing revision; review manually.')
            for field in ('title','revision') if folder=='toeic' else ('title','revision','level','topic','track','order'):
                setattr(obj,field,content[field])
            obj.content=content
            obj.full_clean();obj.save()
            audit(editor,obj,False,'QA ONLY: reviewed Vietnamese wording revision; personal reading snapshots unchanged.')
            count+=1
print(f'Updated {count} reviewed QA practices. Existing personal readings and attempts preserved.')
