import copy
import io
import json
import uuid
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase, Client
from learning.models import VocabularyCollection, LexicalReference, Vocabulary, FoundationAttempt
from learning.services.lexical_patterns import lessons, reference_rows, manifest
from learning.services.foundation_content import quiz_snapshot, revision
from scripts.build_lexical_lessons import build


class LexicalDataTests(SimpleTestCase):
    def test_reproducible_lessons_and_reference_provenance(self):
        self.assertEqual(build()['collections'], lessons())
        self.assertEqual(len(lessons()), 37)
        self.assertEqual(sum(len(u['words']) for u in lessons()), 240)
        families = {w['family'] for u in lessons() for w in u['words'] if 'family' in w}
        self.assertEqual(len(families), 24)
        for unit in lessons():
            self.assertEqual(len(unit['words']), len(unit['questions']))
            for q in unit['questions']:
                self.assertIn('____', q['prompt'])
                self.assertTrue(q['hint_vi'])
                self.assertEqual(q['prompt'].count('____'), 1)
        rows = list(reference_rows())
        self.assertEqual(len(rows), 24719)
        self.assertEqual(len({r['key'] for r in rows}), len(rows))
        self.assertEqual(sum(r['kind']=='family' for r in rows), manifest()['counts']['family'])
        corpus = [r for r in rows if r['kind']=='corpus']
        self.assertEqual(len(corpus),1887)
        self.assertTrue(all(r['detail']['count'] >= 2 for r in corpus))
        self.assertTrue(all(len(r['detail']['evidence'])==2 for r in corpus))
        self.assertTrue(all(r['detail']['license']=='CC BY-SA 4.0' for r in corpus))
        create = [r for r in rows if r['headword']=='create' and r['related']=='creative']
        self.assertTrue(create)
        self.assertTrue(create[0]['detail']['senses'][0]['related_id'])
        collocation = next(r for r in rows if r['headword']=='access' and r['related']=='gain')
        self.assertIn('gain access', collocation['detail']['pattern'])
        self.assertTrue(collocation['detail']['examples'])


class LexicalAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='pattern-learner')
        cls.other = get_user_model().objects.create_user(username='pattern-other')
        cls.unit = copy.deepcopy(lessons()[0])
        VocabularyCollection.objects.create(slug=cls.unit['id'], title=cls.unit['title'], topic=cls.unit['topic'],
            level=cls.unit['level'], content=cls.unit)
        samples = [r for r in reference_rows() if r['headword'] in ('create','access')]
        LexicalReference.objects.bulk_create([LexicalReference(**r) for r in samples])

    def setUp(self):
        self.client.force_login(self.user)

    def test_private_catalogue_no_answers_and_reference_pagination(self):
        anonymous = Client()
        self.assertEqual(anonymous.get('/api/lexical/lessons/').status_code, 401)
        self.assertEqual(anonymous.get('/api/lexical/reference/?q=create&kind=family').status_code, 401)
        response = self.client.get('/api/lexical/lessons/')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        catalog = response.json()
        self.assertEqual(len(catalog['items']), 1)
        self.assertNotIn('questions', catalog['items'][0])
        detail = self.client.get('/api/learn/vocabulary/'+self.unit['id']+'/').json()
        self.assertIn('hint_vi', detail['questions'][0])
        self.assertNotIn('answer', detail['questions'][0])
        self.assertNotIn('explanation_vi', detail['questions'][0])
        result = self.client.get('/api/lexical/reference/?q=ACCESS&kind=collocation').json()
        self.assertLessEqual(len(result['items']), 12)
        self.assertTrue(result['has_next'])
        next_page = self.client.get('/api/lexical/reference/?q=access&kind=collocation&page=2').json()
        self.assertNotEqual(result['items'][0], next_page['items'][0])
        for query in ['q=a','q=create&kind=wrong','q=create&page=0','q=create&page=101','q=create&page=abc','q=<script>']:
            self.assertEqual(self.client.get('/api/lexical/reference/?'+query).status_code, 400)

    def test_direct_relations_only_and_both_ends_searchable(self):
        result = self.client.get('/api/lexical/reference/?q=creative&kind=family').json()
        self.assertTrue(any(r['headword']=='create' for r in result['items']))
        self.assertTrue(all(r['headword']=='creative' or r['related']=='creative' for r in result['items']))
        self.assertEqual(self.client.get('/api/lexical/reference/?q=unlistedword&kind=family').json()['items'], [])
        corpus=self.client.get('/api/lexical/reference/?q=create&kind=corpus').json()
        self.assertTrue(corpus['items'])
        self.assertTrue(all(r['source']=='ewt-2.18' for r in corpus['items']))
        self.assertTrue(all(r['detail']['evidence'][0]['sentence_id'] for r in corpus['items']))

    def test_quiz_progress_and_whole_phrase_flashcards_are_owner_scoped(self):
        snapshot = quiz_snapshot(self.unit, 'vocabulary')
        payload = dict(answers={q['id']:q['answer'] for q in self.unit['questions']}, token=str(uuid.uuid4()), version=revision(snapshot))
        url = '/api/learn/vocabulary/'+self.unit['id']
        result = self.client.post(url+'/submit/', json.dumps(payload), content_type='application/json')
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()['score'],6)
        self.client.post(url+'/submit/', json.dumps(payload), content_type='application/json')
        self.assertEqual(FoundationAttempt.objects.count(),1)
        save = self.client.post(url+'/save/', json.dumps({'indices':[0,1]}), content_type='application/json')
        self.assertEqual(save.status_code,201)
        self.assertEqual(Vocabulary.objects.get(word='make progress').owner, self.user)
        self.assertEqual(Vocabulary.objects.count(),2)
        cards_url='/api/lexical/lessons/'+self.unit['id']+'/cards/'
        cards=self.client.get(cards_url)
        self.assertEqual([v['word'] for v in cards.json()['items']], ['make progress','take a break'])
        self.assertEqual(cards['Cache-Control'],'private, no-store')
        repeated = self.client.post(url+'/save/', json.dumps({'indices':[0,1]}), content_type='application/json')
        self.assertEqual(repeated.json()['created'],0)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(cards_url).json()['items'],[])
        self.assertIsNone(self.client.get('/api/lexical/lessons/').json()['items'][0]['progress'])
        self.assertFalse(any(w['saved'] for w in self.client.get(url+'/').json()['words']))
        csrf = Client(enforce_csrf_checks=True);csrf.force_login(self.user)
        self.assertEqual(csrf.post(url+'/save/', json.dumps({'indices':[0]}), content_type='application/json').status_code,403)

    def test_seed_is_additive_idempotent_and_does_not_reset_progress(self):
        row=VocabularyCollection.objects.get(pk=self.unit['id']);row.title='Edited lesson';row.save()
        sample = list(reference_rows())[:3]
        with patch('learning.management.commands.seed_lexical_patterns.reference_rows', return_value=iter(sample)), patch(
            'learning.management.commands.seed_lexical_patterns.manifest', return_value={'counts':{'family':3}}):
            call_command('seed_lexical_patterns', stdout=io.StringIO())
        count=LexicalReference.objects.count()
        with patch('learning.management.commands.seed_lexical_patterns.reference_rows', return_value=iter(sample)), patch(
            'learning.management.commands.seed_lexical_patterns.manifest', return_value={'counts':{'family':3}}):
            call_command('seed_lexical_patterns', stdout=io.StringIO())
        row.refresh_from_db();self.assertEqual(row.title,'Edited lesson')
        self.assertEqual(VocabularyCollection.objects.filter(content__track='lexical_patterns').count(),37)
        self.assertEqual(LexicalReference.objects.count(),count)
