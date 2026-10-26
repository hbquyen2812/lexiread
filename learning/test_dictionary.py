import copy
import json
from unittest.mock import patch

import httpx
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from learning.models import Reading, Vocabulary
from learning.services import dictionary as service
from learning.services.foundation_content import units


ENTRY = [{'word': 'routine', 'phonetics': [
    {'text': '/ɹuːˈtiːn/', 'audio': 'https://api.dictionaryapi.dev/media/pronunciations/en/routine-us.mp3',
     'sourceUrl': 'https://commons.wikimedia.org/wiki/File:Example.ogg',
     'license': {'name': 'BY-SA 4.0', 'url': 'https://creativecommons.org/licenses/by-sa/4.0'}}],
    'meanings': [{'partOfSpeech': 'noun', 'definitions': [{'definition': 'A regular activity.', 'example': 'This is my routine.'}]}],
    'sourceUrls': ['https://en.wiktionary.org/wiki/routine'],
    'license': {'name': 'CC BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0'}}]


class DictionaryTests(TestCase):
    def setUp(self):
        cache.clear(); self.addCleanup(cache.clear)
        self.alice = get_user_model().objects.create_user(username='dictionary-alice')
        self.bob = get_user_model().objects.create_user(username='dictionary-bob')
        self.reading = Reading.objects.create(owner=self.alice, title='Private reading', text='Private context',
            analysis={'vocabulary': [{'word':'routine','meaning_vi':'thói quen trong bài','pos':'noun'}]})

    def test_auth_ownership_and_invalid_queries_never_call_provider(self):
        with patch.object(service, 'fetch_remote') as fetch:
            self.assertEqual(self.client.get('/api/dictionary/', {'word':'routine'}).status_code, 401)
            self.client.force_login(self.bob)
            self.assertEqual(self.client.get('/api/dictionary/', {'word':'routine','reading_id':self.reading.pk}).status_code, 404)
            for word in ('', 'http://localhost', 'hello@example.com', 'word\x00', 'a'*161, 'one two three four five six seven eight nine ten eleven twelve thirteen'):
                self.assertEqual(self.client.get('/api/dictionary/', {'word':word}).status_code, 400)
            self.assertEqual(self.client.get('/api/dictionary/', {'word':'routine','reading_id':'invalid'}).status_code, 400)
            fetch.assert_not_called()

    def test_context_meaning_and_provider_are_separate_and_no_context_is_sent(self):
        self.client.force_login(self.alice)
        with patch('learning.dictionary_views.lookup_local', return_value={'status':'ok','entries':service.sanitize_entries(ENTRY)}) as remote:
            response = self.client.get('/api/dictionary/', {'word':'Routine,','reading_id':self.reading.pk})
            remote.assert_called_once_with('routine')
        data=response.json()
        self.assertEqual(data['local_entries'][0]['meaning_vi'],'thói quen trong bài')
        self.assertEqual(data['local_entries'][0]['label'],'Trong bài đang đọc')
        self.assertEqual(data['dictionary']['entries'][0]['phonetics'][0]['accent'],'US')
        self.assertEqual(response['Cache-Control'],'private, no-store')
        self.assertEqual(data['links'][0]['title'],'Cambridge Dictionary')

    def test_personal_meanings_stay_private_without_network(self):
        Vocabulary.objects.create(owner=self.alice,word='routine',meaning_vi='private Alice',fingerprint='alice')
        Vocabulary.objects.create(owner=self.bob,word='routine',meaning_vi='private Bob',fingerprint='bob')
        with patch.object(service,'fetch_remote',side_effect=AssertionError('No runtime network')):
            self.client.force_login(self.alice);first=self.client.get('/api/dictionary/',{'word':'routine'}).json()
            self.client.force_login(self.bob);second=self.client.get('/api/dictionary/',{'word':'routine'}).json()
        self.assertIn('private Alice',json.dumps(first))
        self.assertNotIn('private Alice',json.dumps(second))
        self.assertNotIn('private Bob',json.dumps(first))

    def test_course_gloss_available_without_dictionary_seed(self):
        word=units('vocabulary')[0]['words'][0]
        self.client.force_login(self.alice)
        with patch.object(service,'fetch_remote',side_effect=AssertionError('No runtime network')):
            data=self.client.get('/api/dictionary/',{'word':word['word']}).json()
        self.assertEqual(data['dictionary']['status'],'not_ready')
        self.assertTrue(any(x['meaning_vi']==word['meaning_vi'] for x in data['local_entries']))

    def test_sanitizer_rejects_unsafe_audio_and_partial_ipa(self):
        raw=copy.deepcopy(ENTRY)
        raw[0]['phonetics'].insert(0,{'text':'/ˈkjɔː-/','audio':''})
        raw[0]['phonetics'][1]['audio']='https://api.dictionaryapi.dev.evil.test/media/pronunciations/en/test.mp3'
        raw[0]['sourceUrls'].append('javascript:alert(1)')
        clean=service.sanitize_entries(raw)
        self.assertEqual(clean[0]['phonetics'][0]['audio'],'')
        self.assertEqual(len(clean[0]['phonetics']),1)
        self.assertEqual(clean[0]['sources'],['https://en.wiktionary.org/wiki/routine'])
        raw[0]['license']['url']='https://attacker.test/license'
        self.assertEqual(service.sanitize_entries(raw),[])
        self.assertEqual(service.sanitize_entries([None,1,{}]),[])

    def test_http_policy_normal_response_and_no_redirects(self):
        real_client=httpx.Client
        seen=[]
        def handler(request):
            seen.append(str(request.url))
            if request.url.host == 'commons.wikimedia.org':
                return httpx.Response(200, json={'query': {'pages': {'1': {'ns': 6, 'pageid': 1,
                    'title': 'File:Example.ogg', 'imageinfo': [{'mime': 'audio/ogg',
                    'url': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.ogg?utm_source=test'}]}}}})
            return httpx.Response(200,json=ENTRY)
        with patch.object(service.httpx,'Client',side_effect=lambda **kwargs:real_client(transport=httpx.MockTransport(handler),**kwargs)):
            result = service.fetch_remote('routine')
            self.assertEqual(result['status'],'ok')
            self.assertEqual(result['entries'][0]['phonetics'][0]['audio'],
                             'https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.ogg')
        self.assertEqual(len(seen), 2)
        self.assertEqual(seen[0],service.ENDPOINT+'routine/')
        self.assertTrue(seen[1].startswith(service.COMMONS_API+'?'))
        for response in (httpx.Response(302,headers={'location':'http://127.0.0.1/'}),
                         httpx.Response(200,headers={'content-type':'text/html'},text='not JSON'),
                         httpx.Response(404,headers={'content-type':'text/html'},text='CDN error'),
                         httpx.Response(200,headers={'content-type':'application/json'},content=b' '*512001)):
            with patch.object(service.httpx,'Client',side_effect=lambda **kwargs:real_client(transport=httpx.MockTransport(lambda r:response),**kwargs)):
                self.assertEqual(service.fetch_remote('routine')['status'],'unavailable')

    def test_missing_word_is_cached_and_budget_blocks_only_new_requests(self):
        with patch.object(service,'fetch_remote',return_value={'status':'not_found','entries':[]}) as fetch:
            self.assertEqual(service.remote_lookup('missing',self.alice.pk)['status'],'not_found')
            service.remote_lookup('missing',self.bob.pk)
            self.assertEqual(fetch.call_count,1)
            cache.set('dictionary-budget:'+str(self.alice.pk),30,60)
            self.assertEqual(service.remote_lookup('another',self.alice.pk)['status'],'rate_limited')
            self.assertEqual(service.remote_lookup('missing',self.alice.pk)['status'],'not_found')
            self.assertEqual(fetch.call_count,1)

    def test_http_not_found_and_malformed_payloads(self):
        real_client=httpx.Client
        with patch.object(service.httpx,'Client',side_effect=lambda **kwargs:real_client(transport=httpx.MockTransport(lambda r:httpx.Response(404,json={'title':'No Definitions Found'})),**kwargs)):
            self.assertEqual(service.fetch_remote('nonesuch')['status'],'not_found')
        with patch.object(service,'fetch_remote',side_effect=ValueError('bad JSON')):
            self.assertEqual(service.remote_lookup('routine',self.alice.pk)['status'],'unavailable')

    def test_recordings_ignore_unsafe_files_and_metadata_failures(self):
        real_client = httpx.Client
        for response in (httpx.Response(403), httpx.Response(200, json=[]),
                         httpx.Response(200, json={'query': {'pages': {'1': {'ns': 6, 'pageid': 1,
                             'title': 'File:Example.ogg', 'imageinfo': [{'mime': 'audio/ogg',
                             'url': 'https://attacker.test/file.ogg'}]}}}}),
                         httpx.Response(200, json={'query': {'pages': {'1': {'ns': 6, 'pageid': 1,
                             'title': 'File:Example.ogg', 'imageinfo': [{'mime': 'text/html',
                             'url': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.ogg'}]}}}})):
            original = service.sanitize_entries(ENTRY)
            with patch.object(service.httpx, 'Client', side_effect=lambda **kwargs:real_client(
                    transport=httpx.MockTransport(lambda r:response), **kwargs)):
                self.assertEqual(service.resolve_recordings(copy.deepcopy(original)), original)

    def test_recording_pageids_are_batched_and_only_two_recordings_resolved(self):
        original = service.sanitize_entries(ENTRY)
        original[0]['phonetics'] = [dict(original[0]['phonetics'][0],
            source='https://commons.wikimedia.org/w/index.php?curid='+str(i)) for i in (1,2,3)]
        real_client = httpx.Client
        seen = []
        def handler(request):
            seen.append(request)
            return httpx.Response(200, json={'query': {'pages': {}}})
        with patch.object(service.httpx, 'Client', side_effect=lambda **kwargs:real_client(
                transport=httpx.MockTransport(handler), **kwargs)):
            service.resolve_recordings(original)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].url.params['pageids'], '1|2')
        self.assertIn('LexiRead', seen[0].headers['User-Agent'])
