"""Integration tests requiring Django + PostgreSQL. Never run against a production DB.
Run: python manage.py test learning -v 2 (Django creates a separate test database).
"""
import json,uuid
from datetime import timedelta
from django.test import TestCase,Client,override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from learning.models import Reading,Vocabulary,ReviewLog,VocabularyOccurrence
from learning.services.storage import save_entry,review_entry,export_library,import_library

@override_settings(AI_PROVIDER='none',OPENAI_API_KEY='',ALLOWED_HOSTS=['testserver','localhost'],
    STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},
              'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class PrivateLibraryTests(TestCase):
    def setUp(self):
        U=get_user_model()
        self.alice=U.objects.create_user(username='alice-test')
        self.bob=U.objects.create_user(username='bob-test')
        self.client.force_login(self.alice)
        self.reading=Reading.objects.create(owner=self.alice,title='Test reading',text='A bold decision.\n\nAn apt example.')
        self.word,_=save_entry(self.alice,{'word':'bold','meaning_vi':'táo bạo'},self.reading)
        self.other,_=save_entry(self.bob,{'word':'hidden','meaning_vi':'ẩn'})
    def post_json(self,path,data):return self.client.post(path,json.dumps(data),content_type='application/json')
    def test_auth_required(self):
        self.client.logout();self.assertEqual(self.client.get('/api/bootstrap/').status_code,401)
    def test_owner_isolation(self):
        items=self.client.get('/api/vocabulary/').json()['items']
        self.assertEqual(len(items),1);self.assertEqual(items[0]['word'],'bold')
    def test_no_other_user_edit(self):
        r=self.client.patch(f'/api/vocabulary/{self.other.id}/',json.dumps({'word':'stolen'}),content_type='application/json')
        self.assertEqual(r.status_code,404)
    def test_owner_cannot_be_injected(self):
        r=self.post_json('/api/vocabulary/',{'word':'apt','meaning_vi':'phù hợp','owner':self.bob.id})
        self.assertEqual(r.status_code,201)
        self.assertTrue(Vocabulary.objects.filter(owner=self.alice,word='apt').exists())
    def test_duplicate_preserves_schedule(self):
        review_entry(self.alice,self.word.id,'good',uuid.uuid4());self.word.refresh_from_db()
        due=self.word.due_at
        duplicate,new=save_entry(self.alice,{'word':' BOLD ','meaning_vi':'Táo bạo'})
        self.assertFalse(new);self.assertEqual(duplicate.id,self.word.id);self.assertEqual(duplicate.due_at,due)
    def test_same_sense_keeps_multiple_reading_occurrences(self):
        second=Reading.objects.create(owner=self.alice,title='Second source',text='A bold new example.')
        duplicate,new=save_entry(self.alice,{'word':'bold','meaning_vi':'táo bạo','context':'A bold new example.'},second)
        self.assertFalse(new);self.assertEqual(duplicate.id,self.word.id)
        self.assertEqual(VocabularyOccurrence.objects.filter(vocabulary=self.word).count(),2)
        filtered=self.client.get(f'/api/vocabulary/?reading={second.id}').json()['items']
        self.assertEqual([item['id'] for item in filtered],[str(self.word.id)])
        sources=self.client.get('/api/vocabulary/sources/').json()['items']
        self.assertEqual({item['id'] for item in sources},{str(self.reading.id),str(second.id)})
        loose,_=save_entry(self.alice,{'word':'linked later','meaning_vi':'được liên kết sau'})
        save_entry(self.alice,{'word':'linked later','meaning_vi':'được liên kết sau','context':'A later context.'},second)
        loose.refresh_from_db();self.assertEqual(loose.reading_id,second.id);self.assertEqual(loose.context,'A later context.')
    def test_review_idempotency(self):
        token=uuid.uuid4()
        a=review_entry(self.alice,self.word.id,'good',token)
        b=review_entry(self.alice,self.word.id,'good',token)
        self.word.refresh_from_db()
        self.assertTrue(b['duplicate']);self.assertEqual(a['due_at'],b['due_at'])
        self.assertEqual(self.word.repetitions,1);self.assertEqual(ReviewLog.objects.count(),1)
    def test_bulk_is_atomic(self):
        r=self.post_json('/api/vocabulary/',{'items':[{'word':'fine','meaning_vi':'tốt'},{'word':'empty'}]})
        self.assertEqual(r.status_code,400);self.assertFalse(Vocabulary.objects.filter(word='fine').exists())
    def test_no_key_no_cloud_call(self):
        r=self.post_json('/api/ai/lookup/',{'word':'apt','allow_cloud':True})
        self.assertEqual(r.status_code,400)
    def test_csrf_required(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.alice)
        r=c.post('/api/vocabulary/',json.dumps({'word':'x','meaning_vi':'y'}),content_type='application/json')
        self.assertEqual(r.status_code,403)
    def test_delete_reading_preserves_words(self):
        self.assertEqual(self.client.delete(f'/api/readings/{self.reading.id}/').status_code,200)
        self.word.refresh_from_db();self.assertIsNone(self.word.reading_id)
    def test_backup_ownership_and_merge(self):
        payload=export_library(self.alice)
        self.assertEqual(payload['version'],5);self.assertEqual(len(payload['vocabulary']),1)
        self.assertEqual(payload['counts'],{'readings':1,'vocabulary':1,'reviews':0,'toeic_attempts':0,'foundation_attempts':0})
        result=import_library(self.bob,payload)
        self.assertEqual(result['created'],1)
        clone=Vocabulary.objects.get(owner=self.bob,word='bold')
        self.assertNotEqual(clone.id,self.word.id)
        self.assertEqual(clone.occurrences.count(),1)
        self.assertEqual(import_library(self.bob,payload)['created'],0)
    def test_backup_preserves_distinct_identical_readings(self):
        Reading.objects.create(owner=self.alice,title='Duplicate title',text='Exactly the same text.')
        Reading.objects.create(owner=self.alice,title='Duplicate title',text='Exactly the same text.')
        payload=export_library(self.alice)
        first=import_library(self.bob,payload)
        self.assertEqual(first['readings_created'],3)
        self.assertEqual(Reading.objects.filter(owner=self.bob,title='Duplicate title').count(),2)
        second=import_library(self.bob,payload)
        self.assertEqual(second['readings_created'],0)
        self.assertEqual(Reading.objects.filter(owner=self.bob,title='Duplicate title').count(),2)
    def test_exercise_answer_once(self):
        for word,meaning in [('apt','phù hợp'),('new','mới'),('old','cũ')]:
            save_entry(self.alice,{'word':word,'meaning_vi':meaning})
        q=self.client.get('/api/exercises/next/?mode=meaning&scope=all').json()
        self.assertNotIn('correct_answer',q);self.assertEqual(len(q['options']),4)
        url=f'/api/exercises/{q["id"]}/answer/'
        a=self.post_json(url,{'answer':q['options'][0]}).json()
        b=self.post_json(url,{'answer':q['options'][1]}).json()
        self.assertEqual(a,b);self.assertEqual(ReviewLog.objects.count(),1)
    def test_reading_filters_pagination_and_favorite_progress(self):
        favorite=Reading.objects.create(owner=self.alice,title='Grammar Notes',text='A searchable grammar article.',
            source_name='Course notes',progress={'completed':True,'favorite':True})
        Reading.objects.create(owner=self.bob,title='Grammar Notes',text='Must stay private.',progress={'completed':True,'favorite':True})
        response=self.client.get('/api/readings/?q=grammar&status=completed&favorite=yes&sort=title&page=1&limit=1')
        self.assertEqual(response.status_code,200)
        data=response.json();self.assertEqual(set(data),{'items','total','page','limit'})
        self.assertEqual((data['total'],data['page'],data['limit']),(1,1,1))
        self.assertEqual(data['items'][0]['id'],str(favorite.id));self.assertTrue(data['items'][0]['favorite'])
        self.assertEqual(data['items'][0]['status'],'completed')
        unfinished=self.client.get('/api/readings/?status=in_progress&favorite=no').json()['items']
        self.assertEqual([item['id'] for item in unfinished],[str(self.reading.id)])
        progress=self.post_json(f'/api/readings/{self.reading.id}/progress/',{'favorite':True}).json()['progress']
        self.assertTrue(progress['favorite'])
    def test_reading_filter_rejects_invalid_values(self):
        for query in ['status=unknown','favorite=maybe','sort=rank','page=0','limit=101','page=nope']:
            with self.subTest(query=query):self.assertEqual(self.client.get('/api/readings/?'+query).status_code,400)
    def test_vocabulary_search_scopes_and_sort(self):
        now=timezone.now()
        context,_=save_entry(self.alice,{'word':'contextual','meaning_vi':'theo ngữ cảnh','context':'Unique context needle'})
        source,_=save_entry(self.alice,{'word':'source','meaning_vi':'nguồn','source_label':'Unique source needle'})
        example,_=save_entry(self.alice,{'word':'example','meaning_vi':'ví dụ','example':'Unique example needle'})
        learning,_=save_entry(self.alice,{'word':'learning','meaning_vi':'đang học'})
        mastered,_=save_entry(self.alice,{'word':'mastered','meaning_vi':'đã thuộc'})
        forgotten,_=save_entry(self.alice,{'word':'forgotten','meaning_vi':'đã quên lại'})
        Vocabulary.objects.filter(pk=learning.pk).update(repetitions=2,interval_days=5,
            due_at=now-timedelta(days=2),last_reviewed=now)
        Vocabulary.objects.filter(pk=mastered.pk).update(repetitions=8,interval_days=21,
            due_at=now+timedelta(days=5),last_reviewed=now)
        Vocabulary.objects.filter(pk=forgotten.pk).update(repetitions=0,interval_days=10/1440,
            due_at=now+timedelta(minutes=10),last_reviewed=now)
        for needle,expected in [('context needle',context),('source needle',source),('example needle',example)]:
            with self.subTest(needle=needle):
                ids={x['id'] for x in self.client.get('/api/vocabulary/?q='+needle.replace(' ','%20')).json()['items']}
                self.assertEqual(ids,{str(expected.id)})
        self.assertIn(str(learning.id),{x['id'] for x in self.client.get('/api/vocabulary/?scope=learning').json()['items']})
        self.assertIn(str(forgotten.id),{x['id'] for x in self.client.get('/api/vocabulary/?scope=learning').json()['items']})
        self.assertNotIn(str(forgotten.id),{x['id'] for x in self.client.get('/api/vocabulary/?scope=new').json()['items']})
        self.assertIn(str(mastered.id),{x['id'] for x in self.client.get('/api/vocabulary/?scope=mastered').json()['items']})
        Vocabulary.objects.filter(pk=forgotten.pk).update(lapses=3)
        self.assertEqual([x['id'] for x in self.client.get('/api/vocabulary/?scope=weak').json()['items']],[str(forgotten.id)])
        self.assertEqual([x['id'] for x in self.client.get('/api/vocabulary/?scope=overdue').json()['items']],[str(learning.id)])
        words=[x['word'] for x in self.client.get('/api/vocabulary/?sort=word&limit=100').json()['items']]
        self.assertEqual(words,sorted(words,key=str.casefold))
        self.assertEqual(self.client.get('/api/vocabulary/?scope=unknown').status_code,400)
        self.assertEqual(self.client.get('/api/vocabulary/?sort=unknown').status_code,400)
        for query in ['page=0','page=nope','limit=0','limit=501']:
            with self.subTest(query=query):self.assertEqual(self.client.get('/api/vocabulary/?'+query).status_code,400)
    def test_bootstrap_learning_stats_streak_and_goal(self):
        now=timezone.now()
        learning,_=save_entry(self.alice,{'word':'learning','meaning_vi':'đang học'})
        mastered,_=save_entry(self.alice,{'word':'mastered','meaning_vi':'đã thuộc'})
        forgotten,_=save_entry(self.alice,{'word':'forgotten','meaning_vi':'đã quên lại'})
        Vocabulary.objects.filter(pk=learning.pk).update(repetitions=2,interval_days=5,
            due_at=now-timedelta(days=2),last_reviewed=now)
        Vocabulary.objects.filter(pk=mastered.pk).update(repetitions=8,interval_days=21,
            due_at=now+timedelta(days=5),last_reviewed=now)
        Vocabulary.objects.filter(pk=forgotten.pk).update(repetitions=0,interval_days=10/1440,lapses=3,
            due_at=now+timedelta(minutes=10),last_reviewed=now)
        today_log=ReviewLog.objects.create(owner=self.alice,vocabulary=self.word,rating='good',next_due=now)
        yesterday_log=ReviewLog.objects.create(owner=self.alice,vocabulary=self.word,rating='good',next_due=now)
        ReviewLog.objects.filter(pk=yesterday_log.pk).update(created_at=now-timedelta(days=1))
        data=self.client.get('/api/bootstrap/').json()['stats']
        self.assertEqual((data['new'],data['learning'],data['mastered'],data['overdue']),(1,2,1,1))
        self.assertEqual(data['weak'],1)
        self.assertEqual((data['review_streak'],data['daily_goal'],data['daily_goal_progress'],data['daily_goal_percent']),(2,20,1,5))
