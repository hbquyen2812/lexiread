import io
import json
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from learning.models import CuratedLesson, ToeicPractice, VocabularyCollection, Reading
from learning.services.content_release import load_release, converted_release, RELEASE
from learning.services.catalog import grade_lesson, public_lesson
from learning.services.toeic import grade_toeic
from learning.services.foundation_content import grade, quiz_snapshot


class ReleaseValidationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pack, cls.manifest = load_release()
        cls.rows = list(converted_release(cls.pack, cls.manifest))

    def test_every_question_and_vocabulary_context_survives_and_grades(self):
        self.assertEqual(len(self.rows), 486)
        self.assertEqual(sum(len(row['questions']) for _,row,_ in self.rows),3240)
        self.assertEqual(sum(len(c['words']) for _,_,c in self.rows),3572)
        for kind,row,collection in self.rows:
            answers={q['id']:q['answer'] for q in row['questions']}
            result=(grade_toeic if kind=='toeic' else grade_lesson)(row,answers)
            self.assertEqual(result['score'],result['total'],row['slug'])
            if kind=='lesson':
                self.assertFalse(any('answer' in q or 'evidence' in q for q in public_lesson(row)['questions']))
            snapshot=quiz_snapshot(collection,'vocabulary')
            result=grade(snapshot,{q['id']:q['answer'] for q in snapshot['questions']})
            self.assertEqual(result['score'],len(collection['words']))

    def test_original_ids_and_nested_paragraph_evidence(self):
        self.assertEqual(sum(r['slug'].startswith('pack-v1-') for _,r,_ in self.rows),60)
        row=next(r for _,r,_ in self.rows if r['slug']=='pack-v3-day-003')
        cashier=next(v for v in row['analysis']['vocabulary'] if v['word']=='cashier')
        self.assertEqual(cashier['paragraph_index'],1)
        self.assertEqual(next(r for _,r,_ in self.rows if r['slug']=='pack-v3-igt3-001-s1')['track'],'ielts')
        self.assertEqual(len(next(r for _,r,_ in self.rows if r['slug']=='pack-v3-tor3-001-p7')['questions']),54)
        full=next(r for _,r,_ in self.rows if r['slug']=='pack-v3-tor3-001-p7')
        self.assertEqual(len({tuple(q['document_ids']) for q in full['questions']}),13)
        triple=next(q for q in full['questions'] if q['id']=='tor3_001_p7_q186')
        self.assertEqual(triple['document_ids'],['G11D1','G11D2','G11D3'])

    def test_practice_groups_reference_complete_question_sets(self):
        lessons={l['id']:l for l in self.pack['lessons']}
        groups=json.loads((RELEASE/'tests.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(t['test_kind']=='full_reading' for t in groups),12)
        self.assertEqual(sum(t['test_kind']=='practice_bundle' for t in groups),90)
        for t in groups:
            self.assertEqual(t['question_count'],sum(len(lessons[s['lesson_id']]['questions']) for s in t['sections']))


class ReleaseImportTests(TestCase):
    def test_additive_import_preserves_edits_accounts_and_reading_progress(self):
        pack,manifest=load_release()
        _,row,_=next(converted_release(pack,manifest))
        existing=CuratedLesson.objects.create(slug=row['slug'],title='Edited title',level=row['level'],
            track=row['track'],topic=row['topic'],published=False,content={'editor_note':'keep me'})
        user=get_user_model().objects.create_user(username='v3-reader',password='test-password-only')
        reading=Reading.objects.create(owner=user,title='My snapshot',text='My original text.',catalog_slug=existing.pk,
            lesson_snapshot={'revision':1},progress={'completed':True})
        out=io.StringIO()
        call_command('seed_content_v3',stdout=out)
        before=(CuratedLesson.objects.count(),ToeicPractice.objects.count(),VocabularyCollection.objects.count())
        self.assertEqual(before,(414,72,486))
        call_command('seed_content_v3',stdout=out)
        self.assertEqual(before,(CuratedLesson.objects.count(),ToeicPractice.objects.count(),VocabularyCollection.objects.count()))
        existing.refresh_from_db();reading.refresh_from_db();user.refresh_from_db()
        self.assertEqual(existing.title,'Edited title');self.assertFalse(existing.published)
        self.assertEqual(existing.content,{'editor_note':'keep me'})
        self.assertTrue(reading.progress['completed']);self.assertEqual(reading.text,'My original text.')
        self.assertTrue(user.check_password('test-password-only'))
        self.client.force_login(user)
        result=self.client.get('/api/learn/vocabulary/pack-v3-day-003/').json()
        self.assertEqual(len(result['words']),6)
        self.assertFalse(any('answer' in q or 'explanation_vi' in q for q in result['questions']))
        self.assertEqual(self.client.get('/api/learn/plan/').status_code,200)
        groups=self.client.get('/api/practice-groups/').json()['items']
        self.assertTrue(groups)
        self.assertFalse(any(s['href']=='#lesson/'+existing.pk for g in groups for s in g['sections']))
