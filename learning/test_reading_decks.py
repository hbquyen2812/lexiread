"""One-click decks: deterministic extraction, private ownership, and preserved review progress."""
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from .models import Reading, Vocabulary, VocabularyCollection, VocabularyOccurrence, DictionaryEntry, DictionaryForm, DictionaryRelease
from .services.reading_decks import candidates, occurrences, context_at, lexicon, CACHE_KEY
from .services.storage import save_entry, review_entry


class ReadingDeckTests(TestCase):
    def setUp(self):
        cache.delete(CACHE_KEY)
        self.addCleanup(cache.delete, CACHE_KEY)
        self.alice = get_user_model().objects.create_user(username='reader-alice')
        self.bob = get_user_model().objects.create_user(username='reader-bob')
        self.client.force_login(self.alice)
        self.bank = [
            {'word':'appointment','meaning_vi':'cuộc hẹn','example':'Confirm the appointment.'},
            {'word':'confirm','meaning_vi':'xác nhận','example':'Please confirm the meeting.'},
            {'word':'take part','meaning_vi':'tham gia'},
            {'word':'art','meaning_vi':'nghệ thuật'},
            {'word':'bank','meaning_vi':'ngân hàng','example':'Money in the account.'},
            {'word':'bank','meaning_vi':'bờ sông','example':'The river and water.'},
            {'word':'the','meaning_vi':'mạo từ'},
        ]
        VocabularyCollection.objects.create(slug='local-words',title='Local words',content={'words':self.bank})
        self.reading = Reading.objects.create(owner=self.alice,title='A small meeting',text='Please confirm the appointment. We take part today.')

    def url(self, reading=None):
        return f'/api/readings/{(reading or self.reading).pk}/vocabulary-deck/'

    def test_one_post_saves_bilingual_words_and_actual_context_without_ai(self):
        with patch('learning.services.ai.httpx.Client', side_effect=AssertionError('No network')):
            response=self.client.post(self.url())
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(response['Cache-Control'],'private, no-store')
        data=response.json()
        self.assertEqual(data['created'],3)
        self.assertEqual({w['word'] for w in data['items']},{'confirm','appointment','take part'})
        for word in data['items']:
            self.assertIn(word['context'],self.reading.text)
            self.assertEqual(word['example'],word['context'])
            self.assertEqual(word['example_vi'],'')
            self.assertEqual(word['origin'],'auto')
        self.assertEqual(VocabularyOccurrence.objects.count(),3)

    def test_get_never_creates_and_unknown_text_fails_without_writes(self):
        self.assertEqual(self.client.get(self.url()).json()['items'],[])
        self.assertEqual(Vocabulary.objects.count(),0)
        self.reading.text='Quasiparticles blorp xylometazoline.'
        self.reading.save()
        self.assertEqual(self.client.post(self.url()).status_code,400)
        self.assertEqual(Vocabulary.objects.count(),0)

    def test_auth_owner_and_csrf(self):
        other=Reading.objects.create(owner=self.bob,title='Private',text=self.reading.text)
        for method in ('get','post'):
            self.assertEqual(getattr(self.client,method)(self.url(other)).status_code,404)
            self.assertEqual(getattr(Client(),method)(self.url()).status_code,401)
        csrf=Client(enforce_csrf_checks=True);csrf.force_login(self.alice)
        self.assertEqual(csrf.post(self.url()).status_code,403)
        self.assertEqual(self.client.delete(self.url()).status_code,405)
        self.assertEqual(Vocabulary.objects.count(),0)

    def test_repeat_click_preserves_progress_and_second_article_context(self):
        first=self.client.post(self.url()).json()
        word=Vocabulary.objects.get(owner=self.alice,word='appointment')
        review_entry(self.alice,word.pk,'easy',uuid.uuid4());word.refresh_from_db()
        before=(word.due_at,word.last_reviewed,word.interval_days,word.example)
        second=Reading.objects.create(owner=self.alice,title=self.reading.title,text='Your appointment starts tomorrow.')
        data=self.client.post(self.url(second)).json()
        self.assertEqual(data['created'],0)
        self.assertEqual(data['items'][0]['context'],second.text)
        self.assertEqual(data['items'][0]['id'],str(word.pk))
        for _ in range(2):
            self.assertEqual(self.client.post(self.url()).json()['created'],0)
        word.refresh_from_db()
        self.assertEqual((word.due_at,word.last_reviewed,word.interval_days,word.example),before)
        self.assertEqual(Vocabulary.objects.count(),len(first['items']))
        self.assertEqual(VocabularyOccurrence.objects.count(),4)
        filtered=self.client.get('/api/vocabulary/',{'reading':str(second.pk)}).json()
        self.assertEqual([w['id'] for w in filtered['items']],[str(word.pk)])

    def test_boundary_matching_explicit_inflections_and_no_sentence_crossing(self):
        release=DictionaryRelease.objects.create(key='test',checksum='test')
        entry=DictionaryEntry.objects.create(word='confirm',display_word='confirm',release=release)
        DictionaryForm.objects.create(form='confirmed',entry=entry)
        text='Confirmed the apartment. Take. Part in art. Take part tomorrow.'
        found=occurrences(text,{'confirm','art','take part'})
        self.assertEqual(len(found['art']),1)
        self.assertEqual(len(found['take part']),1)
        self.assertEqual(text[slice(*found['confirm'][0])],'Confirmed')

    def test_ambiguous_senses_skipped_and_authored_sense_prioritised(self):
        self.reading.text='The bank is open.'
        self.assertEqual(candidates(self.reading),[])
        self.reading.text='The bank holds money in your account.'
        self.assertEqual(candidates(self.reading)[0]['meaning_vi'],'ngân hàng')
        self.reading.analysis={'vocabulary':[{'word':'bank','meaning_vi':'bờ sông'}]}
        self.reading.text='The bank is steep.'
        self.assertEqual(candidates(self.reading)[0]['meaning_vi'],'bờ sông')

    def test_bound_limit_and_keep_long_sentence_word(self):
        names=['word'+chr(97+i) for i in range(26)]
        self.reading.analysis={'vocabulary':[{'word':word,'meaning_vi':'nghĩa '+word} for word in names]}
        self.reading.text=' '.join(names)
        self.assertEqual(len(candidates(self.reading)),20)
        text='x '*2000+'appointment'+' y'*2000
        context=context_at(text,4000,4011)
        self.assertIn('appointment',context)
        self.assertLessEqual(len(context),1800)

    def test_public_cache_excludes_private_vocab_and_stale_example(self):
        private,_=save_entry(self.bob,{'word':'secret','meaning_vi':'riêng tư'})
        self.assertNotIn('secret',lexicon())
        self.client.post(self.url())
        self.reading.text='A completely rewritten text.';self.reading.save()
        data=self.client.get(self.url()).json()
        self.assertTrue(all(w['example']=='' for w in data['items']))
        self.assertFalse(any(w['id']==str(private.pk) for w in data['items']))
