import copy
import uuid
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.utils import timezone
from .models import LearningProfile, FoundationAttempt, Vocabulary, AICall, LearningDay, ToeicPractice, ToeicAttempt
from .services.foundation_content import units, quiz_snapshot, revision, grade
from .services.learning_path import progress_for, plan_for
from .services.storage import export_library, import_library


class FoundationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice=get_user_model().objects.create_user('foundation-alice')
        cls.bob=get_user_model().objects.create_user('foundation-bob')

    def setUp(self):
        self.client.force_login(self.alice)
        self.grammar=units('grammar')[0]
        self.vocab=units('vocabulary')[0]

    def submit(self,kind='grammar',unit=None,correct=True,token=None):
        unit=unit or self.grammar
        snapshot=quiz_snapshot(unit,kind)
        answers={q['id']:q['answer'] if correct else (q['answer']+1)%4 for q in snapshot['questions']}
        return self.client.post(f'/api/learn/{kind}/{unit["id"]}/submit/',{
            'token':str(token or uuid.uuid4()),'version':revision(snapshot),'answers':answers},content_type='application/json')

    def test_catalogue_and_private_answers(self):
        for kind in ('grammar','vocabulary'):
            response=self.client.get('/api/learn/overview/',{'kind':kind,'level':'B2'})
            self.assertEqual(response.status_code,200)
            self.assertEqual(len(response.json()['items']),5)
            self.assertTrue(all(r['level']=='B2' for r in response.json()['items']))
            unit=units(kind)[0]
            detail=self.client.get(f'/api/learn/{kind}/{unit["id"]}/').json()
            self.assertTrue(all(set(q)=={'id','prompt','options'} for q in detail['questions']))
        self.assertEqual(self.client.get('/api/learn/grammar/not-a-lesson/').status_code,404)
        self.assertEqual(self.client.get('/api/learn/overview/?kind=invalid').status_code,400)
        self.assertEqual(AICall.objects.count(),0)

    def test_grade_idempotency_and_account_isolation(self):
        token=uuid.uuid4()
        first=self.submit(token=token)
        self.assertEqual(first.status_code,201)
        self.assertEqual(first.json()['percent'],100)
        repeat=self.submit(correct=False,token=token)
        self.assertEqual(repeat.json()['percent'],100)
        self.assertTrue(repeat.json()['duplicate'])
        self.assertEqual(FoundationAttempt.objects.filter(owner=self.alice).count(),1)
        self.assertEqual(self.submit(unit=units('grammar')[1],token=token).status_code,400)
        self.assertTrue(LearningDay.objects.filter(owner=self.alice).exists())
        self.client.force_login(self.bob)
        self.assertFalse(self.client.get('/api/learn/plan/').json()['progress'])
        self.assertEqual(self.submit(token=token).status_code,201)
        self.assertEqual(FoundationAttempt.objects.filter(token=token).count(),2)

    def test_reject_incomplete_forged_and_stale_submissions(self):
        path=f'/api/learn/grammar/{self.grammar["id"]}/submit/'
        snapshot=quiz_snapshot(self.grammar,'grammar')
        data={'token':str(uuid.uuid4()),'version':revision(snapshot),'answers':{}}
        self.assertEqual(self.client.post(path,data,content_type='application/json').status_code,400)
        data['answers']={q['id']:True for q in snapshot['questions']}
        self.assertEqual(self.client.post(path,data,content_type='application/json').status_code,400)
        data['answers']={q['id']:q['answer'] for q in snapshot['questions']};data['version']='outdated'
        self.assertEqual(self.client.post(path,data,content_type='application/json').status_code,400)
        self.assertEqual(FoundationAttempt.objects.count(),0)

    def test_profile_validation_persistence_and_ownership(self):
        data={'level':'C1','goal':'ielts','daily_minutes':30}
        response=self.client.patch('/api/learn/plan/',data,content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['profile'],data|{'configured':True})
        self.assertEqual(len(response.json()['guidance']['steps']),3)
        self.assertEqual(self.client.patch('/api/learn/plan/',data|{'daily_minutes':True},content_type='application/json').status_code,400)
        self.assertEqual(LearningProfile.objects.get(owner=self.alice).daily_minutes,30)
        self.client.force_login(self.bob)
        self.assertFalse(self.client.get('/api/learn/plan/').json()['profile']['configured'])

    def test_vocabulary_save_merge_preserves_review_and_is_private(self):
        path=f'/api/learn/vocabulary/{self.vocab["id"]}/save/'
        self.assertEqual(self.client.post(path,{'indices':[0,1]},content_type='application/json').json()['created'],2)
        word=Vocabulary.objects.get(owner=self.alice,word=self.vocab['words'][0]['word'])
        word.interval_days=28;word.repetitions=6;word.due_at=timezone.now()+timedelta(days=28);word.save()
        due=word.due_at
        result=self.client.post(path,{'indices':[0,1]},content_type='application/json').json()
        self.assertEqual(result['created'],0);self.assertEqual(result['existing'],2)
        word.refresh_from_db();self.assertEqual(word.interval_days,28);self.assertEqual(word.due_at,due)
        self.assertEqual(Vocabulary.objects.filter(owner=self.bob).count(),0)
        self.assertEqual(self.client.post(path,{'indices':[-1]},content_type='application/json').status_code,400)
        self.assertEqual(self.submit('vocabulary',self.vocab).json()['total'],12)

    def test_dictionary_unicode_empty_and_url_encoding(self):
        self.assertEqual(self.client.get('/api/learn/dictionary/?q=a').json()['total'],0)
        word=self.vocab['words'][0]['word']
        data=self.client.get('/api/learn/dictionary/',{'q':word}).json()
        self.assertGreater(data['total'],0);self.assertEqual(data['items'][0]['word'],word)
        links=self.client.get('/api/learn/dictionary/',{'q':'<script>&evil=/'}).json()['links']
        self.assertTrue(all('<script>' not in link['url'] and link['url'].startswith('https://') for link in links))
        self.assertEqual(len(self.client.get('/api/learn/sources/').json()['items']),40)

    def test_three_attempt_weighting_and_due_review(self):
        for correct in (True,True,False):self.submit(correct=correct)
        key='grammar/'+self.grammar['id']
        self.assertEqual(progress_for(self.alice)[key]['mastery'],50)
        FoundationAttempt.objects.filter(owner=self.alice).update(created_at=timezone.now()-timedelta(days=2))
        self.assertTrue(progress_for(self.alice)[key]['due'])
        self.assertEqual(plan_for(self.alice)['tasks'][0]['href'],'#grammar/'+self.grammar['id'])

    def test_plan_budgets_and_due_words_first(self):
        self.client.post(f'/api/learn/vocabulary/{self.vocab["id"]}/save/',{'indices':[0]},content_type='application/json')
        for level in ('A1','B1','C2'):
            for minutes in (15,30,45,60):
                LearningProfile.objects.update_or_create(owner=self.alice,defaults={'level':level,'goal':'general','daily_minutes':minutes})
                plan=plan_for(self.alice)
                self.assertEqual(plan['tasks'][0]['kind'],'review')
                self.assertLessEqual(sum(t['minutes'] for t in plan['tasks']),minutes)
                self.assertEqual(len({t['href'] for t in plan['tasks']}),len(plan['tasks']))
                self.assertIsNone(plan['next_level'])

    def test_backup_roundtrip_regrades_and_merges(self):
        self.submit()
        LearningProfile.objects.create(owner=self.alice,level='B1',goal='toeic',daily_minutes=30)
        payload=export_library(self.alice)
        self.assertEqual(payload['version'],5)
        self.assertEqual(payload['counts']['foundation_attempts'],1)
        payload['foundation_attempts'][0]['result']={'score':-123} # Not trusted.
        result=import_library(self.bob,payload)
        self.assertEqual(result['foundation_attempts_created'],1)
        self.assertEqual(FoundationAttempt.objects.get(owner=self.bob).result['percent'],100)
        self.assertEqual(LearningProfile.objects.get(owner=self.bob).level,'B1')
        self.assertEqual(import_library(self.bob,payload)['foundation_attempts_created'],0)
        bad=copy.deepcopy(payload);bad['foundation_attempts'][0]['snapshot']['level']='XX'
        with self.assertRaises(ValueError):import_library(self.bob,bad)

    def test_goal_prioritizes_weak_exam_set_within_budget(self):
        LearningProfile.objects.create(owner=self.alice,level='B1',goal='toeic',daily_minutes=30)
        ToeicPractice.objects.create(slug='new-set',title='A new set',published=True,content={'parts':[5]})
        ToeicPractice.objects.create(slug='weak-set',title='Weak set',published=True,content={'parts':[7]})
        ToeicAttempt.objects.create(owner=self.alice,set_slug='weak-set',result={'score':1,'total':10})
        plan=plan_for(self.alice)
        self.assertIn('#toeic-set/weak-set',[t['href'] for t in plan['tasks']])
        self.assertLessEqual(plan['planned_minutes'],30)

    def test_authentication_methods_and_csrf(self):
        anon=Client()
        self.assertEqual(anon.get('/api/learn/plan/').status_code,401)
        self.assertEqual(self.client.post('/api/learn/dictionary/').status_code,405)
        csrf=Client(enforce_csrf_checks=True);csrf.force_login(self.alice)
        self.assertEqual(csrf.patch('/api/learn/plan/',{},content_type='application/json').status_code,403)
        for page in ('learn','grammar','collection'):
            self.assertEqual(self.client.post('/api/activity/visit/',{'page':page},content_type='application/json').status_code,200)
