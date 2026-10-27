"""Run with PostgreSQL normally; config.test_settings gives isolated SQLite smoke tests."""
import copy
import json
from datetime import timedelta
from io import StringIO
from pathlib import Path
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, Client
from django.utils import timezone
from learning.models import CuratedLesson, ToeicPractice, ContentImport, Reading, ToeicAttempt
from learning.editorial.services import read_package, preview_import, apply_import, publish_batch, version_of
from learning.editorial.forms import LessonEditorForm
from learning.services.catalog import validate_lesson, grade_lesson, public_lesson
from learning.services.core import InputError
from learning.services.toeic_repository import public_toeic_set
from learning.services.toeic import toeic_sets


class EditorialTests(TestCase):
    def test_english_only_is_explicit_and_partial_translations_stay_invalid(self):
        raw=copy.deepcopy(self.raw)
        raw['analysis']['translations']=[]
        with self.assertRaises(InputError): validate_lesson(raw)
        raw['translation_status']='not_provided'
        validated=validate_lesson(raw)
        self.assertEqual(validated['analysis']['translations'],[])
        self.assertEqual(public_lesson(validated)['translation_status'],'not_provided')
        raw['analysis']['translations']=[{'index':0,'vi':'Một đoạn.'}]
        with self.assertRaises(InputError): validate_lesson(raw)

    def test_batch_publish_is_atomic_authorized_and_rejects_stale_confirmation(self):
        apply_import(self.editor,self.prepare([self.raw,{**self.raw,'slug':'second-lesson'}]).pk)
        expected={obj.pk:version_of(obj) for obj in CuratedLesson.objects.all()}
        with self.assertRaises(PermissionDenied): publish_batch(self.learner,'lesson',expected)
        bad=CuratedLesson.objects.get(pk='second-lesson')
        bad.content['questions']=[];bad.save()
        with self.assertRaises(InputError): publish_batch(self.editor,'lesson',expected)
        expected={obj.pk:version_of(obj) for obj in CuratedLesson.objects.all()}
        with self.assertRaises(ValidationError): publish_batch(self.editor,'lesson',expected)
        self.assertFalse(CuratedLesson.objects.filter(published=True).exists())
        bad.content={**self.raw,'slug':'second-lesson'};bad.save()
        expected={obj.pk:version_of(obj) for obj in CuratedLesson.objects.all()}
        self.assertEqual(publish_batch(self.editor,'lesson',expected),2)
        self.assertEqual(CuratedLesson.objects.filter(published=True).count(),2)

    def test_admin_batch_confirmation_is_signed_and_new_content_roundtrips(self):
        raw=copy.deepcopy(self.raw);raw['translation_status']='not_provided';raw['analysis']['translations']=[]
        raw['analysis']['vocabulary'][0]['usage_pattern']='a daily routine'
        apply_import(self.editor,self.prepare(raw).pk)
        url='/admin/learning/curatedlesson/'
        data={'action':'publish_selected','_selected_action':[raw['slug']]}
        response=self.client.post(url,data)
        self.assertContains(response,'Xác nhận xuất bản')
        self.assertFalse(CuratedLesson.objects.get().published)
        response=self.client.post(url,{**data,'confirm_publish':'yes','preview_token':response.context['preview_token']})
        self.assertEqual(response.status_code,302)
        self.assertTrue(CuratedLesson.objects.get().published)
        reading=self.client.post(f"/api/catalog/{raw['slug']}/open/").json()
        self.assertEqual(reading['analysis']['translations'],[])
        from learning.services.storage import export_library, import_library
        import_library(self.learner,export_library(self.editor))
        restored=Reading.objects.get(owner=self.learner)
        self.assertEqual(restored.lesson_snapshot['translation_status'],'not_provided')
        self.assertEqual(restored.analysis['vocabulary'][0]['usage_pattern'],'a daily routine')
        malformed=export_library(self.editor)
        malformed['readings'][0]['lesson_snapshot']='not-an-object'
        third=get_user_model().objects.create_user('third-reader')
        with self.assertRaises(InputError): import_library(third,malformed)
        self.assertFalse(Reading.objects.filter(owner=third).exists())

    def setUp(self):
        self.editor=get_user_model().objects.create_superuser('editor','editor@example.com','test-password')
        self.learner=get_user_model().objects.create_user('learner')
        self.raw=json.loads((settings.BASE_DIR/'data/lessons/a-quiet-start.json').read_text(encoding='utf-8'))
        self.client.force_login(self.editor)

    def upload(self,data,name='lessons.json'):
        return SimpleUploadedFile(name,json.dumps(data,ensure_ascii=False).encode('utf-8'))

    def prepare(self,data=None,update=False):
        rows=read_package(self.upload(data if data is not None else self.raw),'lesson',{})
        return preview_import(self.editor,'lesson',rows,update)

    def test_preview_does_not_publish_and_apply_is_idempotent(self):
        batch=self.prepare()
        self.assertEqual(CuratedLesson.objects.count(),0)
        _,count=apply_import(self.editor,batch.pk)
        self.assertEqual(count,1)
        self.assertFalse(CuratedLesson.objects.get().published)
        self.assertEqual(apply_import(self.editor,batch.pk)[1],0)
        self.assertEqual(LogEntry.objects.count(),1)

    def test_permissions_and_preview_ownership(self):
        with self.assertRaises(PermissionDenied): preview_import(self.learner,'lesson',[self.raw])
        batch=self.prepare()
        with self.assertRaises(ContentImport.DoesNotExist): apply_import(self.learner,batch.pk)
        self.learner.is_staff=True;self.learner.save()
        self.client.force_login(self.learner)
        self.assertEqual(self.client.get('/admin/learning/curatedlesson/import/').status_code,403)
        self.client.force_login(self.editor)
        other=get_user_model().objects.create_superuser('other','other@example.com','test-password')
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/admin/learning/curatedlesson/import/{batch.pk}/').status_code,404)

    def test_document_becomes_unpublished_draft(self):
        rows=read_package(SimpleUploadedFile('test.txt',b'An English paragraph.'),'lesson',{
            'slug':'imported-document','title':'Imported','level':'A1','track':'general','topic':'School'})
        batch=preview_import(self.editor,'lesson',rows)
        apply_import(self.editor,batch.pk)
        lesson=CuratedLesson.objects.get()
        self.assertFalse(lesson.published)
        lesson.published=True
        with self.assertRaises(ValidationError): lesson.full_clean()

    def test_duplicate_slugs_and_bad_package_rejected(self):
        for data in ([self.raw,self.raw],{'format':'lexiread-content','version':9,'kind':'lesson','items':[self.raw]},[self.raw,{'slug':'broken'}]):
            with self.subTest(data=str(data)[:40]),self.assertRaises(InputError): read_package(self.upload(data),'lesson',{})
        self.assertEqual(ContentImport.objects.count(),0)

    def test_update_requires_optin_new_revision_and_unpublished(self):
        apply_import(self.editor,self.prepare().pk)
        with self.assertRaises(InputError): self.prepare()
        with self.assertRaises(InputError): self.prepare(update=True)
        new={**self.raw,'revision':2,'title':'Updated title'}
        batch=self.prepare(new,update=True)
        apply_import(self.editor,batch.pk)
        obj=CuratedLesson.objects.get();obj.published=True;obj.save()
        with self.assertRaises(InputError): self.prepare({**new,'revision':3},update=True)

    def test_expired_preview_and_concurrent_changes_fail_without_partial_write(self):
        apply_import(self.editor,self.prepare().pk)
        new={**self.raw,'slug':'brand-new'}
        batch=self.prepare([new,{**self.raw,'revision':2}],update=True)
        obj=CuratedLesson.objects.get();obj.title='Concurrent edit';obj.save()
        with self.assertRaises(InputError): apply_import(self.editor,batch.pk)
        self.assertFalse(CuratedLesson.objects.filter(pk='brand-new').exists())
        self.assertEqual(LogEntry.objects.count(),1)
        batch2=self.prepare(new)
        ContentImport.objects.filter(pk=batch2.pk).update(created_at=timezone.now()-timedelta(minutes=31))
        with self.assertRaises(InputError): apply_import(self.editor,batch2.pk)

    def test_update_preserves_personal_snapshot(self):
        apply_import(self.editor,self.prepare().pk)
        reading=Reading.objects.create(owner=self.learner,title=self.raw['title'],text=self.raw['text'],catalog_slug=self.raw['slug'],lesson_snapshot=self.raw,progress={'completed':True})
        apply_import(self.editor,self.prepare({**self.raw,'revision':2,'title':'Updated'},update=True).pk)
        reading.refresh_from_db()
        self.assertEqual(reading.lesson_snapshot['revision'],1)
        self.assertTrue(reading.progress['completed'])

    def test_http_preview_confirmation_and_csrf(self):
        url='/admin/learning/curatedlesson/import/'
        response=self.client.post(url,{'file':self.upload(self.raw),'level':'A2','track':'general'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(CuratedLesson.objects.count(),0)
        preview=self.client.get(response.url)
        self.assertContains(preview,self.raw['title'])
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.editor)
        self.assertEqual(strict.post(response.url,{'confirm':'yes'}).status_code,403)
        self.assertEqual(self.client.post(response.url,{'confirm':'yes'}).status_code,302)
        self.assertEqual(CuratedLesson.objects.count(),1)

    def test_admin_edit_can_publish_valid_content_and_errors_stay_in_form(self):
        apply_import(self.editor,self.prepare().pk)
        obj=CuratedLesson.objects.get()
        data={'title':obj.title,'level':obj.level,'track':obj.track,'topic':obj.topic,'order':obj.order,
              'summary':self.raw['summary'],'text':self.raw['text'],'translations':'\n\n'.join(t['vi'] for t in self.raw['analysis']['translations']),
              'questions':json.dumps(self.raw['questions']),'vocabulary':json.dumps(self.raw['analysis']['vocabulary']),
              'grammar':json.dumps(self.raw['analysis']['grammar']),'faqs':json.dumps(self.raw['faqs']),
              'published':'on','edit_version':obj.updated_at.isoformat(),'_save':'Save'}
        url=f'/admin/learning/curatedlesson/{obj.pk}/change/'
        self.assertEqual(self.client.get(url).status_code,200)
        bad=self.client.post(url,{**data,'translations':''})
        self.assertEqual(bad.status_code,200)
        self.assertContains(bad,'Bản dịch bị thiếu')
        good=self.client.post(url,data)
        self.assertEqual(good.status_code,302)
        obj.refresh_from_db();self.assertTrue(obj.published);self.assertEqual(obj.revision,2)
        stale=self.client.post(url,data)
        self.assertEqual(stale.status_code,200)
        self.assertContains(stale,'người khác sửa')

    def test_new_question_types_grade_and_do_not_leak_keys(self):
        raw=copy.deepcopy(self.raw)
        raw['questions']=[{'id':'gap','kind':'gap_fill','prompt':'What did she change?','options':[],
            'answer':'routine','accepted_answers':['routine'],'max_words':1,'paragraph_index':0,
            'evidence':'she decided to change her morning routine.','explanation_vi':'Thói quen.'}]
        lesson=validate_lesson(raw)
        self.assertEqual(grade_lesson(lesson,{'gap':' ROUTINE '})['score'],1)
        self.assertEqual(grade_lesson(lesson,{'gap':'morning routine'})['score'],0)
        public=public_lesson(lesson)['questions'][0]
        self.assertEqual(public['max_words'],1)
        self.assertNotIn('answer',public);self.assertNotIn('accepted_answers',public)

    def test_toeic_database_publish_and_revision_guard(self):
        content=toeic_sets()[0]
        obj=ToeicPractice.objects.create(slug=content['slug'],title=content['title'],content=content,published=False)
        self.client.force_login(self.learner)
        self.assertEqual(self.client.get('/api/toeic/').json()['items'],[])
        obj.published=True;obj.save()
        response=self.client.get(f'/api/toeic/{obj.pk}/').json()
        self.assertNotIn('editorial',response)
        self.assertNotIn('answer',response['questions'][0])
        obj.revision=2;obj.full_clean();obj.save()
        data={'token':'72f7b0e8-733a-4381-89ca-8c5a13c47401','revision':1,'answers':{q['id']:q['answer'] for q in content['questions']}}
        self.assertEqual(self.client.post(f'/api/toeic/{obj.pk}/submit/',json.dumps(data),content_type='application/json').status_code,400)

    def test_export_import_roundtrip(self):
        apply_import(self.editor,self.prepare().pk)
        response=self.client.post('/admin/learning/curatedlesson/',{'action':'export_selected','_selected_action':[self.raw['slug']]})
        self.assertEqual(response.status_code,200)
        payload=json.loads(response.content)
        self.assertEqual(payload['format'],'lexiread-content')
        self.assertEqual(read_package(self.upload(payload),'lesson',{})[0]['slug'],self.raw['slug'])

    def test_toeic_result_backup_uses_original_snapshot_after_source_edit(self):
        from learning.services.storage import export_library, import_library
        from learning.services.toeic import grade_toeic
        import uuid
        content=copy.deepcopy(toeic_sets()[0])
        obj=ToeicPractice.objects.create(slug=content['slug'],title=content['title'],content=content,published=True)
        answers={q['id']:q['answer'] for q in content['questions']}
        ToeicAttempt.objects.create(owner=self.learner,set_slug=obj.pk,answers=answers,result=grade_toeic(content,answers),snapshot=content,token=uuid.uuid4())
        obj.content=copy.deepcopy(content);obj.revision=content['revision']+1
        obj.content['questions'][0]['answer']=(obj.content['questions'][0]['answer']+1)%4
        obj.full_clean();obj.save()
        import_library(self.editor,export_library(self.learner))
        self.assertEqual(ToeicAttempt.objects.get(owner=self.editor).result['score'],len(answers))
        self.assertEqual(self.client.get('/api/toeic/').json()['items'][0]['attempt_count'],0)

    def test_catalog_filters_before_pagination_and_supports_pre_a1(self):
        for index in range(3):
            content=validate_lesson({**self.raw,'slug':f'lesson-{index}','level':'pre-A1'})
            CuratedLesson.objects.create(slug=content['slug'],title=content['title'],level=content['level'],topic=content['topic'],content=content,published=True,order=index)
        Reading.objects.create(owner=self.editor,title='Personal',text='Text',catalog_slug='lesson-2',progress={'favorite':True})
        result=self.client.get('/api/catalog/?level=pre-A1&favorite=yes&limit=1').json()
        self.assertEqual(result['total'],1)
        self.assertEqual(result['items'][0]['slug'],'lesson-2')
        result=self.client.get('/api/catalog/?limit=1&page=2').json()
        self.assertEqual(result['total'],3);self.assertEqual(result['items'][0]['slug'],'lesson-1')
        self.assertTrue(result['has_more'])

    def test_full_supplied_dataset_converts_without_dropping_questions_or_vocab(self):
        from learning.services.content_release import load_release
        source,manifest=load_release()
        source={**source,'lessons':[l for l in source['lessons'] if l['id'] in manifest['legacy_ids']]}
        converted=[]
        for kind,count in [('lesson',42),('toeic',18)]:
            rows=read_package(self.upload(source),kind,{})
            self.assertEqual(len(rows),count)
            batch=preview_import(self.editor,kind,rows)
            self.assertEqual(apply_import(self.editor,batch.pk)[1],count)
            converted.extend(rows)
        self.assertEqual(sum(len(row['questions']) for row in converted),336)
        self.assertEqual(sum(len(row.get('focus_vocabulary',row.get('analysis',{}).get('vocabulary',[]))) for row in converted),504)
        self.assertEqual(sum(len(row['editorial']['original']['vocabulary_questions']) for row in converted),504)
        self.assertFalse(CuratedLesson.objects.filter(published=True).exists())
        self.assertFalse(ToeicPractice.objects.filter(published=True).exists())
        # Explicit English-only publication still validates every question and quotation.
        for row in converted:
            if 'text' not in row: continue
            row=copy.deepcopy(row)
            self.assertEqual(row['translation_status'],'not_provided')
            self.assertEqual(len(validate_lesson(row)['questions']),len(row['questions']))
