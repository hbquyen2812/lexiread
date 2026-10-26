"""PostgreSQL integration tests. Prepared here; must be executed on a real test DB.
Run: python manage.py test learning -v 2
"""
import copy,json,uuid
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase,override_settings
from django.test import RequestFactory
from learning.models import Reading,CuratedLesson,Vocabulary,LessonAttempt,ReadingQuestion,ToeicAttempt,DailyVisit
from learning.services.toeic import toeic_sets
from learning.services.catalog import validate_lesson
from learning.services.storage import import_library,export_library
from learning.forms import EmailUserCreationForm
from learning.views import login_key

@override_settings(AI_PROVIDER='none',OPENAI_API_KEY='',ALLOWED_HOSTS=['testserver','localhost'],
    STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},
              'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class ReadingPlatformTests(TestCase):
    def setUp(self):
        call_command('seed_toeic',stdout=StringIO())
        U=get_user_model();self.alice=U.objects.create_user(username='reading-alice',email='alice@example.com',password='S3cure-test-pass!');self.bob=U.objects.create_user(username='reading-bob',email='bob@example.com')
        self.client.force_login(self.alice)
        self.lesson=validate_lesson(json.loads((settings.BASE_DIR/'data/lessons/a-quiet-start.json').read_text(encoding='utf-8')))
        c=self.lesson
        self.standard=CuratedLesson.objects.create(**{k:c[k] for k in ('slug','title','level','topic','revision','order','published')},content=c)
        self.private=Reading.objects.create(owner=self.alice,title='Private',text='A private story.\n\nAn ending.')
        self.other=Reading.objects.create(owner=self.bob,title='Other',text='Another private story.')
    def post(self,path,data):return self.client.post(path,json.dumps(data),content_type='application/json')
    def open(self):
        response=self.post('/api/catalog/a-quiet-start/open/',{})
        self.assertIn(response.status_code,[200,201]);return response.json()
    def submit(self,rid,answers=None,token=None):
        if answers is None:answers={q['id']:q['answer'] for q in self.lesson['questions']}
        return self.post(f'/api/readings/{rid}/quiz/',{'answers':answers,'token':str(token or uuid.uuid4())})
    def qa_payload(self):return {'question':'Routine nghĩa là gì?','selected_text':'routine','result':{
        'answer_vi':'Thói quen buổi sáng trong bài.','cannot_answer':False,'limitation_vi':'Cần đối chiếu ngữ cảnh.',
        'evidence':[{'paragraph_index':0,'quote':'she decided to change her morning routine.'}],'language_notes':[]}}
    def test_catalog_does_not_publish_private_readings(self):
        data=self.client.get('/api/catalog/').json();self.assertEqual(len(data['items']),1)
        self.assertEqual(data['items'][0]['title'],self.lesson['title'])
        self.assertEqual(len(self.client.get('/api/readings/').json()['items']),1)

    def test_public_landing_lists_lessons_but_actions_stay_private(self):
        self.client.logout();response=self.client.get('/')
        self.assertEqual(response.status_code,200);self.assertTemplateUsed(response,'landing.html')
        self.assertContains(response,self.lesson['title']);self.assertContains(response,'/login/?next=/%23lesson/a-quiet-start')
        self.assertNotContains(response,self.private.text)
        self.assertEqual(self.client.get('/api/catalog/').status_code,401)
        self.assertEqual(self.post('/api/catalog/a-quiet-start/open/',{}).status_code,401)

    def test_login_accepts_username_and_legacy_email(self):
        self.client.logout()
        success=self.client.post('/login/',{'username':'READING-ALICE','password':'S3cure-test-pass!'})
        self.assertEqual(success.status_code,302)
        self.client.logout()
        success=self.client.post('/login/',{'username':'ALICE@EXAMPLE.COM','password':'S3cure-test-pass!','next':'/#catalog'})
        self.assertRedirects(success,'/#catalog',fetch_redirect_response=False)
        duplicate=EmailUserCreationForm(data={'username':'another','email':'Alice@example.com',
            'password1':'Another-S3cure-pass!','password2':'Another-S3cure-pass!'})
        self.assertFalse(duplicate.is_valid());self.assertIn('email',duplicate.errors)

    def test_login_throttle_trusts_forwarded_ip_only_in_proxy_mode(self):
        factory=RequestFactory();first=factory.get('/',REMOTE_ADDR='172.18.0.4',HTTP_X_FORWARDED_FOR='203.0.113.10')
        second=factory.get('/',REMOTE_ADDR='172.18.0.4',HTTP_X_FORWARDED_FOR='203.0.113.11')
        with override_settings(TRUST_PROXY_HTTPS=False):self.assertEqual(login_key(first),login_key(second))
        with override_settings(TRUST_PROXY_HTTPS=True):self.assertNotEqual(login_key(first),login_key(second))
    def test_catalog_favorite_filter_uses_personal_snapshot(self):
        rid=self.open()['id']
        self.post(f'/api/readings/{rid}/progress/',{'favorite':True})
        item=self.client.get('/api/catalog/?favorite=yes').json()['items'][0]
        self.assertEqual(item['reading_id'],rid);self.assertTrue(item['favorite'])
        self.assertEqual(self.client.get('/api/catalog/?favorite=no').json()['items'],[])
    def test_english_topics_search_filter_aliases_and_public_labels(self):
        self.standard.topic='Dữ liệu & quyết định';self.standard.save(update_fields=['topic'])
        other=copy.deepcopy(self.lesson);other.update(slug='topic-alias',topic='data_decisions')
        CuratedLesson.objects.create(**{k:other[k] for k in ('slug','title','level','topic','revision','order','published')},content=other)
        catalog=self.client.get('/api/catalog/').json()
        self.assertEqual(catalog['topics'],['Data & Decisions'])
        self.assertTrue(all(item['topic_label']=='Data & Decisions' for item in catalog['items']))
        self.assertEqual(self.client.get('/api/catalog/',{'q':'data & decisions'}).json()['total'],2)
        self.assertEqual(self.client.get('/api/catalog/',{'topic':'Data & Decisions'}).json()['total'],2)
        self.assertEqual(self.client.get('/api/catalog/',{'topic':'data_decisions'}).json()['total'],1)
        self.client.logout()
        self.assertContains(self.client.get('/'),'<span class="cover-topic" lang="en" data-no-i18n>Data &amp; Decisions</span>',count=2,html=True)
    def test_open_idempotent_and_owner_specific(self):
        first=self.open();again=self.open();self.assertEqual(first['id'],again['id'])
        self.client.force_login(self.bob);second=self.open();self.assertNotEqual(second['id'],first['id'])
        self.assertEqual(Reading.objects.exclude(catalog_slug='').count(),2)
    def test_reading_api_has_no_quiz_keys(self):
        r=self.open();self.assertNotIn('lesson_snapshot',r)
        for q in r['lesson']['questions']:self.assertEqual(set(q),{'id','kind','prompt','options'})
    def test_shared_update_does_not_overwrite_snapshot(self):
        r=self.open();c=copy.deepcopy(self.standard.content);c['revision']=2;c['title']='Changed title'
        self.standard.title='Changed title';self.standard.revision=2;self.standard.content=c;self.standard.save()
        reopened=self.open();self.assertEqual(reopened['id'],r['id']);self.assertEqual(reopened['title'],r['title'])
        self.assertEqual(reopened['lesson']['revision'],1)
    def test_curated_text_read_only(self):
        rid=self.open()['id'];resp=self.client.patch(f'/api/readings/{rid}/',json.dumps({'text':'changed'}),content_type='application/json')
        self.assertEqual(resp.status_code,400);self.assertEqual(Reading.objects.get(pk=rid).text,self.lesson['text'])
    def test_foreign_reading_endpoints_denied(self):
        base=f'/api/readings/{self.other.id}'
        self.assertEqual(self.client.get(base+'/questions/').status_code,404)
        self.assertEqual(self.post(base+'/progress/',{'completed':True}).status_code,404)
        self.assertEqual(self.post(base+'/quiz/',{'token':str(uuid.uuid4()),'answers':{}}).status_code,404)
        self.assertEqual(self.post(base+'/questions/',self.qa_payload()).status_code,404)
    def test_progress_cannot_forge_score(self):
        rid=self.open()['id'];response=self.post(f'/api/readings/{rid}/progress/',{'paragraph':2,'completed':True,'quiz_best':999})
        self.assertEqual(response.status_code,200);self.assertNotIn('quiz_best',response.json()['progress'])
    def test_incomplete_quiz_does_not_write_attempt(self):
        response=self.submit(self.open()['id'],{})
        self.assertEqual(response.status_code,400);self.assertEqual(LessonAttempt.objects.count(),0)
    def test_quiz_grade_and_retry(self):
        rid=self.open()['id'];token=uuid.uuid4();first=self.submit(rid,token=token);second=self.submit(rid,token=token)
        self.assertEqual(first.json()['score'],4);self.assertTrue(second.json()['duplicate']);self.assertEqual(LessonAttempt.objects.count(),1)
        self.assertEqual(second.json()['progress']['quiz_attempts'],1)
    def test_imported_text_has_no_fixed_quiz(self):
        self.assertEqual(self.submit(str(self.private.id)).status_code,400)
    def test_manual_answer_and_fake_quote(self):
        rid=self.open()['id'];self.assertEqual(self.post(f'/api/readings/{rid}/questions/',self.qa_payload()).status_code,201)
        bad=self.qa_payload();bad['result']['evidence'][0]['quote']='Invented quotation'
        self.assertEqual(self.post(f'/api/readings/{rid}/questions/',bad).status_code,400);self.assertEqual(ReadingQuestion.objects.count(),1)
    @override_settings(AI_PROVIDER='openai',OPENAI_API_KEY='test-not-a-real-key')
    def test_cloud_requires_consent(self):
        rid=self.open()['id']
        with patch('learning.services.ai.request_json') as generate:
            response=self.post(f'/api/readings/{rid}/questions/',{'question':'What is routine?'})
        self.assertEqual(response.status_code,400);generate.assert_not_called()
    def test_edited_private_text_hides_old_answers(self):
        self.private.progress={'favorite':True};self.private.save(update_fields=['progress'])
        rid=str(self.private.id);payload={'question':'Nghĩa?','result':{'answer_vi':'Một câu chuyện riêng.','cannot_answer':False,
            'limitation_vi':'','evidence':[{'paragraph_index':0,'quote':'A private story.'}],'language_notes':[]}}
        self.assertEqual(self.post(f'/api/readings/{rid}/questions/',payload).status_code,201)
        self.client.patch(f'/api/readings/{rid}/',json.dumps({'text':'A new private story.'}),content_type='application/json')
        self.assertEqual(self.client.get(f'/api/readings/{rid}/questions/').json()['items'],[])
        self.assertTrue(Reading.objects.get(pk=rid).progress['favorite'])
    def test_backup_roundtrip_includes_attempts_and_help(self):
        rid=self.open()['id'];self.submit(rid);self.post(f'/api/readings/{rid}/questions/',self.qa_payload())
        self.post(f'/api/readings/{rid}/progress/',{'paragraph':2,'completed':True})
        payload=export_library(self.alice);self.assertEqual(payload['version'],5)
        import_library(self.bob,payload);clone=Reading.objects.get(owner=self.bob,catalog_slug='a-quiet-start')
        self.assertNotEqual(str(clone.id),rid);self.assertEqual(clone.progress['quiz_best'],4)
        self.assertEqual(clone.progress['paragraph'],2);self.assertEqual(clone.questions.count(),1);self.assertEqual(clone.lesson_attempts.count(),1)
        self.assertEqual(import_library(self.bob,payload)['readings_created'],0)
        self.assertEqual(CuratedLesson.objects.count(),1)
    def test_failed_restore_is_atomic(self):
        self.open();payload=export_library(self.alice)
        snap=next(x for x in payload['readings'] if x['catalog_slug'])
        snap['lesson_snapshot']['questions'][0]['evidence']='Not an original quotation'
        before=Reading.objects.filter(owner=self.bob).count()
        with self.assertRaises(ValueError):import_library(self.bob,payload)
        self.assertEqual(Reading.objects.filter(owner=self.bob).count(),before)
    def test_seed_default_preserves_curated_edits_and_user_words(self):
        self.standard.title='Edited standard';self.standard.save()
        call_command('seed_lessons',stdout=StringIO());call_command('seed_lessons',stdout=StringIO())
        self.standard.refresh_from_db();self.assertEqual(self.standard.title,'Edited standard')
        self.assertEqual(CuratedLesson.objects.count(),len(list((settings.BASE_DIR/'data/lessons').glob('*.json'))));self.assertEqual(Vocabulary.objects.count(),0)
    def test_seed_update_changes_standard_not_user_snapshot(self):
        rid=self.open()['id'];call_command('seed_lessons',update=True,stdout=StringIO())
        self.assertEqual(Reading.objects.get(pk=rid).lesson_snapshot['revision'],1)
        self.assertEqual(CuratedLesson.objects.count(),len(list((settings.BASE_DIR/'data/lessons').glob('*.json'))))
    def test_unpublished_cannot_open(self):
        self.standard.published=False;self.standard.save()
        self.assertEqual(self.client.get('/api/catalog/').json()['items'],[])
        self.assertEqual(self.post('/api/catalog/a-quiet-start/open/',{}).status_code,404)

    def test_toeic_attempt_is_private_idempotent_and_does_not_leak_keys(self):
        catalog=self.client.get('/api/toeic/').json();self.assertEqual(len(catalog['items']),len(toeic_sets()))
        practice=toeic_sets()[0];public=self.client.get(f"/api/toeic/{practice['slug']}/").json()
        self.assertTrue(all('answer' not in question for question in public['questions']))
        answers={q['id']:q['answer'] for q in practice['questions']};token=str(uuid.uuid4())
        first=self.post(f"/api/toeic/{practice['slug']}/submit/",{'answers':answers,'token':token,'duration_seconds':240,'revision':public['revision']})
        second=self.post(f"/api/toeic/{practice['slug']}/submit/",{'answers':answers,'token':token,'duration_seconds':240,'revision':public['revision']})
        self.assertEqual(first.json()['score'],practice['question_count']);self.assertTrue(second.json()['duplicate'])
        self.assertEqual(ToeicAttempt.objects.filter(owner=self.alice).count(),1)
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get('/api/toeic/').json()['items'][0]['attempt_count'],0)
        restored=import_library(self.bob,export_library(self.alice));self.assertEqual(restored['toeic_attempts_created'],1)
        self.assertEqual(ToeicAttempt.objects.filter(owner=self.bob).count(),1)

    def test_private_traffic_and_admin_analytics(self):
        self.client.get('/')
        self.post('/api/activity/visit/',{'page':'toeic'})
        row=DailyVisit.objects.get(owner=self.alice)
        self.assertEqual(len(row.visitor_key),64);self.assertNotIn('127.0.0.1',row.visitor_key)
        self.assertEqual(row.views,2);self.assertEqual(row.page_counts,{'home':1,'toeic':1})
        boot=self.client.get('/api/bootstrap/').json()
        self.assertEqual(boot['stats']['active_days_30'],0)
        self.assertEqual(boot['stats']['page_views_today'],2)
        self.assertFalse(boot['stats']['study']['active_today'])
        self.assertEqual(self.client.get('/api/analytics/').status_code,403)
        self.alice.is_staff=True;self.alice.save(update_fields=['is_staff'])
        data=self.client.get('/api/analytics/?days=7').json()
        self.assertEqual(data['totals']['visitors'],1);self.assertEqual(data['totals']['views'],2)

    def test_anonymous_visit_becomes_owned_after_login(self):
        self.client.logout();self.client.get('/login/')
        self.assertEqual(DailyVisit.objects.count(),1);self.assertIsNone(DailyVisit.objects.get().owner_id)
        self.client.force_login(self.alice);self.client.get('/')
        self.assertEqual(DailyVisit.objects.count(),1);self.assertEqual(DailyVisit.objects.get().owner_id,self.alice.pk)
