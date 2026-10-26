"""Public guides and question-type filters must preserve the learning boundary."""
import json
import re
import uuid
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.management import call_command
from .models import CuratedLesson
from .services.catalog import validate_lesson

ROOT=Path(__file__).resolve().parents[1]


class LearningHubTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=get_user_model().objects.create_user(username='hub-reader',password='test-long-password')
        raw=json.loads((ROOT/'data/lessons/a-quiet-start.json').read_text(encoding='utf-8'))
        for slug,track,published in [('hub-ielts','ielts',True),('hub-general','general',True),('hub-draft','ielts',False)]:
            lesson=validate_lesson({**raw,'slug':slug,'track':track,'published':published})
            CuratedLesson.objects.create(slug=slug,title=lesson['title'],level=lesson['level'],topic=lesson['topic'],track=track,published=published,content=lesson)

    def test_guides_are_public_local_and_have_accessible_fallback(self):
        with patch('httpx.get',side_effect=AssertionError('No publisher network request')):
            response=self.client.get('/guides/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<noscript>')
        self.assertContains(response,'lang="vi"')
        match=re.search(r'<script id="strategy-guides-data" type="application/json">(.*?)</script>',response.content.decode(),re.S)
        self.assertIsNotNone(match)
        guides=json.loads(match.group(1))
        self.assertEqual(len(guides),18)
        self.assertEqual({g['exam'] for g in guides},{'ielts','toeic'})
        self.assertEqual(CuratedLesson.objects.count(),3)

    def test_guide_json_cannot_break_out_of_script(self):
        with patch('learning.services.strategy_guides.strategy_guides',return_value=[{'title':'</script><img src=x onerror=alert(1)>','summary_vi':'&'}]):
            response=self.client.get('/guides/')
        self.assertNotContains(response,'<img src=x')
        self.assertContains(response,'\\u003C/script\\u003E')

    def test_type_filter_is_paginated_and_does_not_expose_keys_or_drafts(self):
        self.client.force_login(self.user)
        response=self.client.get('/api/catalog/?track=ielts&kind=tfng&limit=1')
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual(data['total'],1)
        self.assertEqual(data['items'][0]['slug'],'hub-ielts')
        self.assertIn('tfng',data['items'][0]['question_types'])
        self.assertGreaterEqual(data['items'][0]['estimated_minutes'],5)
        for field in ('questions','answers','evidence','analysis'):
            self.assertNotIn(field,data['items'][0])
        self.assertEqual(self.client.get('/api/catalog/?kind=gap_fill').json()['total'],0)
        self.assertEqual(self.client.get('/api/catalog/?kind=bogus').status_code,400)

    def test_practice_still_requires_account_and_app_receives_guides(self):
        self.assertEqual(self.client.get('/api/catalog/?kind=tfng').status_code,401)
        self.client.force_login(self.user)
        response=self.client.get('/')
        self.assertContains(response,'strategy-guides-data')
        self.assertContains(response,'practice_tools.js')


class ExpandedPracticeIntegrationTests(TestCase):
    """Run the new content through real private API snapshots and server grading."""
    @classmethod
    def setUpTestData(cls):
        cls.user=get_user_model().objects.create_user(username='content-auditor')
        call_command('seed_lessons',stdout=StringIO())
        call_command('seed_toeic',stdout=StringIO())

    def post(self,path,data):
        return self.client.post(path,json.dumps(data),content_type='application/json')

    def test_every_expanded_ielts_lesson_opens_translates_and_grades(self):
        self.client.force_login(self.user)
        lessons=CuratedLesson.objects.filter(slug__startswith='ielts-').exclude(
            slug__in=['ielts-a-cooler-street','ielts-a-library-of-seeds','ielts-the-searchable-archive'])
        self.assertEqual(lessons.count(),10)
        for obj in lessons:
            with self.subTest(slug=obj.slug):
                response=self.post(f'/api/catalog/{obj.slug}/open/',{})
                self.assertEqual(response.status_code,201)
                opened=response.json()
                self.assertEqual(len(opened['analysis']['translations']),6)
                self.assertEqual(len(opened['analysis']['vocabulary']),7)
                for q in opened['lesson']['questions']:
                    for secret in ('answer','accepted_answers','evidence','explanation_vi'):
                        self.assertNotIn(secret,q)
                answers={q['id']:q['answer'] for q in obj.content['questions']}
                token=str(uuid.uuid4())
                result=self.post(f"/api/readings/{opened['id']}/quiz/",{'answers':answers,'token':token})
                self.assertEqual(result.status_code,200)
                self.assertEqual((result.json()['score'],result.json()['total']),(10,10))
                repeated=self.post(f"/api/readings/{opened['id']}/quiz/",{'answers':answers,'token':token})
                self.assertTrue(repeated.json()['duplicate'])

    def test_every_expanded_toeic_set_opens_and_grades(self):
        from .models import ToeicPractice,ToeicAttempt
        self.client.force_login(self.user)
        practices=ToeicPractice.objects.filter(slug__regex=r'^p[567]-')
        self.assertEqual(practices.count(),12)
        for obj in practices:
            with self.subTest(slug=obj.slug):
                response=self.client.get(f'/api/toeic/{obj.slug}/')
                self.assertEqual(response.status_code,200)
                public=response.json()
                for q in public['questions']:
                    self.assertFalse({'answer','evidence','explanation_vi'} & q.keys())
                answers={q['id']:q['answer'] for q in obj.content['questions']}
                result=self.post(f'/api/toeic/{obj.slug}/submit/',{
                    'answers':answers,'token':str(uuid.uuid4()),'duration_seconds':120,'revision':public['revision']})
                self.assertEqual(result.status_code,200)
                self.assertEqual(result.json()['score'],len(answers))
                self.assertEqual(sum(v['total'] for v in result.json()['by_part'].values()),len(answers))
        self.assertEqual(ToeicAttempt.objects.filter(owner=self.user).count(),12)
