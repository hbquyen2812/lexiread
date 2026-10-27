import copy
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connections
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature
from learning.models import VocabularyCollection, CuratedLesson, FoundationAttempt
from learning.services.foundation_content import get_unit, units, summary, unit_summaries, quiz_snapshot, grade
from learning.services.storage import save_entry, export_library, import_library


class LeanCatalogueTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='lean-reader')
        self.client.force_login(self.user)
        self.unit=copy.deepcopy(units('vocabulary')[0])
        self.unit.update(id='pre-starter',title='A first notebook',level='pre-A1')
        VocabularyCollection.objects.create(slug=self.unit['id'],title=self.unit['title'],
            topic=self.unit['topic'],level=self.unit['level'],content=self.unit)
        other=copy.deepcopy(self.unit);other.update(id='other-unit',title='Second unit',level='A2')
        VocabularyCollection.objects.create(slug=other['id'],title=other['title'],topic=other['topic'],
            level=other['level'],content=other)

    def test_detail_fetches_one_unit_and_summary_matches_without_answers(self):
        with self.assertNumQueries(1) as captured:
            unit=get_unit('vocabulary','pre-starter')
        self.assertEqual(unit,self.unit)
        self.assertIn('WHERE',captured.captured_queries[0]['sql'])
        expected=[summary(row,'vocabulary') for row in units('vocabulary')]
        with self.assertNumQueries(1) as captured:
            rows=unit_summaries('vocabulary')
        self.assertEqual(rows,expected)
        self.assertNotIn('"learning_vocabularycollection"."content",',captured.captured_queries[0]['sql'])
        self.assertTrue(all('words' not in r and 'questions' not in r for r in rows))
        self.assertIsNone(get_unit('vocabulary','missing-unit'))

    def test_pre_a1_filter_and_backup_round_trip(self):
        response=self.client.get('/api/learn/overview/?kind=vocabulary&level=pre-A1')
        self.assertEqual(response.status_code,200)
        self.assertEqual([r['id'] for r in response.json()['items']],['pre-starter'])
        snapshot=quiz_snapshot(self.unit,'vocabulary')
        answers={q['id']:q['answer'] for q in snapshot['questions']}
        FoundationAttempt.objects.create(owner=self.user,kind='vocabulary',unit_id='pre-starter',token=uuid.uuid4(),
            snapshot=snapshot,answers=answers,result=grade(snapshot,answers))
        other=get_user_model().objects.create_user(username='restored-reader')
        result=import_library(other,export_library(self.user))
        self.assertEqual(result['foundation_attempts_created'],1)
        self.assertEqual(FoundationAttempt.objects.get(owner=other).snapshot['level'],'pre-A1')

    def test_home_starters_keep_total_and_one_of_each_level(self):
        for level in ['A1','A2','B1','B2']:
            for i in range(2):
                CuratedLesson.objects.create(slug=f'{level.lower()}-{i}',title=f'{level} story {i}',level=level,
                    track='general',topic='Travel',published=True,content={'track':'general','text':'A short story.'})
        response=self.client.get('/api/catalog/?track=general&featured=1&limit=3')
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual(data['total'],8)
        self.assertEqual([row['level'] for row in data['items']],['A1','A2','B1'])


class ConcurrentWordSaveTests(TransactionTestCase):
    @skipUnlessDBFeature('has_select_for_update')
    def test_concurrent_imports_merge_tags_without_resetting_review(self):
        user=get_user_model().objects.create_user(username='concurrent-reader')
        word,_=save_entry(user,{'word':'notebook','meaning_vi':'vở','tags':['Original']})
        word.repetitions=5;word.save(update_fields=['repetitions'])
        barrier=threading.Barrier(2)
        def save(tag):
            close_old_connections()
            try:
                owner=get_user_model().objects.get(pk=user.pk)
                barrier.wait(timeout=10)
                return save_entry(owner,{'word':'notebook','meaning_vi':'vở','tags':[tag]})[1]
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(save,tag) for tag in ['Travel','School']]
            self.assertEqual([future.result(timeout=15) for future in futures],[False,False])
        word.refresh_from_db()
        self.assertEqual(set(word.tags),{'Original','Travel','School'})
        self.assertEqual(word.repetitions,5)
