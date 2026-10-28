import copy
import hashlib
import io
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from learning.models import DictionaryEntry, DictionaryForm, DictionaryRelease, DictionaryAudio, VocabularyCollection
from learning.services import offline_dictionary as service
from learning.services.foundation_content import units


class OfflineDictionaryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='offline-dictionary')
        self.client.force_login(self.user)
        self.release = DictionaryRelease.objects.create(key='oewn-2025',checksum='a'*64,entry_count=1,ipa_count=1)
        self.entry = DictionaryEntry.objects.create(word='run',display_word='run',definition='Move quickly.',
            release=self.release,content=[{'word':'run','phonetics':[{'ipa':'/rʌn/','audio':''}],
                'meanings':[{'pos':'verb','definitions':[{'definition':'Move quickly.','example':'I run.'}]}],
                'sources':['https://en-word.net/'],'license':service.LICENSE,'source_label':'Open English WordNet 2025'}])
        DictionaryForm.objects.create(form='ran',entry=self.entry)

    def test_lookup_search_inflections_and_audio_never_use_network_or_ai(self):
        binary=b'OggS-test';digest=hashlib.sha256(binary).hexdigest()
        DictionaryAudio.objects.create(digest=digest,data=binary,mime='audio/ogg',attribution={})
        with patch('httpx.Client',side_effect=AssertionError('No network in learner requests')):
            lookup=self.client.get('/api/dictionary/',{'word':'ran'}).json()
            self.assertEqual(lookup['dictionary']['base_words'],['run'])
            self.assertEqual(lookup['dictionary']['storage'],'database')
            self.assertEqual(self.client.get('/api/dictionary/search/',{'q':'ran'}).json()['items'][0]['word'],'run')
            audio=self.client.get('/api/dictionary/audio/'+digest+'/')
            self.assertEqual(audio.content,binary)
            self.assertEqual(audio['Content-Type'],'audio/ogg')
            self.assertEqual(self.client.get('/api/dictionary/',{'word':'missing'}).json()['dictionary']['status'],'not_found')

    def test_batch_ipa_is_local_bounded_and_never_substitutes_inflected_words(self):
        with self.assertNumQueries(1):
            self.assertEqual(service.pronunciation_batch([' Run ', 'ran', 'missing']),
                             {'run': ['/rʌn/'], 'ran': [], 'missing': []})
        with patch('httpx.Client', side_effect=AssertionError('No network dictionary')):
            response = self.client.post('/api/dictionary/pronunciations/',
                data=json.dumps({'words': ['RUN', 'ran', 'missing']}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['items'], {'run': ['/rʌn/'], 'ran': [], 'missing': []})
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        for words in (None, 'run', ['run']*101, [None], [{}], [''], ['x'*161]):
            self.assertEqual(self.client.post('/api/dictionary/pronunciations/',
                data=json.dumps({'words': words}), content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/dictionary/pronunciations/',
            data=json.dumps({'words': [], 'extra': 'x'*24001}), content_type='application/json').status_code, 400)
        self.assertEqual(self.client.get('/api/dictionary/pronunciations/').status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post('/api/dictionary/pronunciations/',
            data=json.dumps({'words': ['run']}), content_type='application/json').status_code, 401)

    def test_ipa_batch_preserves_variants_and_requires_csrf(self):
        self.entry.content[0]['phonetics'] += [{'ipa':'/rʌn/'}, {'ipa':'/ɹʌn/'}]
        self.entry.save()
        self.assertEqual(service.pronunciation_batch(['run'])['run'], ['/rʌn/', '/ɹʌn/'])
        from django.test import Client
        secured = Client(enforce_csrf_checks=True)
        secured.force_login(self.user)
        self.assertEqual(secured.post('/api/dictionary/pronunciations/',
            data=json.dumps({'words': ['run']}), content_type='application/json').status_code, 403)

    def test_dictionary_pagination_is_bounded_and_empty_query_is_lightweight(self):
        DictionaryEntry.objects.bulk_create([DictionaryEntry(word=f'test{i:02}',display_word=f'test{i:02}',
            definition='Definition',release=self.release,content=[]) for i in range(25)])
        first=self.client.get('/api/dictionary/search/',{'q':'test'}).json()
        second=self.client.get('/api/dictionary/search/',{'q':'test','page':2}).json()
        self.assertEqual((first['total'],len(first['items']),first['has_next']),(25,20,True))
        self.assertEqual((len(second['items']),second['has_next']),(5,False))
        self.assertEqual(self.client.get('/api/dictionary/search/').json()['items'],[])
        self.assertEqual(self.client.get('/api/dictionary/search/',{'page':'bad'}).status_code,400)
        self.assertEqual(self.client.get('/api/dictionary/search/',{'q':"' OR 1=1 --"}).json()['total'],0)

    def test_authentication_covers_dictionary_search_and_binary_audio(self):
        self.client.logout()
        for url in ('/api/dictionary/search/','/api/dictionary/audio/'+'a'*64+'/'):
            self.assertEqual(self.client.get(url).status_code,401)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/dictionary/audio/invalid/').status_code,404)
        self.assertEqual(self.client.get('/api/dictionary/audio/'+'a'*64+'/').status_code,404)

    def test_database_collections_are_used_and_reseeding_preserves_edits(self):
        self.assertEqual(service.seed_collections(),30)
        first=VocabularyCollection.objects.first();first.title='Edited by staff';first.save()
        self.assertEqual(service.seed_collections(),0)
        self.assertEqual(units('vocabulary')[0]['title'],'Edited by staff')
        overview=self.client.get('/api/learn/overview/',{'kind':'vocabulary'}).json()
        self.assertEqual(len(overview['items']),30)
        self.assertTrue(all(r['topic'] for r in overview['items']))
        self.assertEqual(self.client.get('/api/learn/vocabulary/'+first.pk+'/').json()['title'],'Edited by staff')

    def test_archive_import_all_senses_forms_checksum_and_idempotence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);path=root/'sample.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('noun.test.json',json.dumps({'1-n':{'definition':['First sense.','Second sense.'],
                    'example':['A sample.'],'members':['sample','example']}}))
                z.writestr('entries-s.json',json.dumps({'sample':{'n':{'sense':[{'synset':'1-n'}],
                    'pronunciation':[{'value':'sæmpəl'}],'form':['samples']}}}))
            checksum=hashlib.sha256(path.read_bytes()).hexdigest()
            (root/'manifest.json').write_text(json.dumps({'sha256':checksum}))
            with patch.object(service,'DATA',root):
                release,changed=service.import_release(path)
                self.assertTrue(changed)
                entry=DictionaryEntry.objects.get(pk='sample')
                self.assertEqual(len(entry.content[0]['meanings'][0]['definitions']),2)
                self.assertEqual(entry.content[0]['phonetics'][0]['ipa'],'/sæmpəl/')
                self.assertTrue(DictionaryForm.objects.filter(form='samples',entry=entry).exists())
                # An import of the pinned release is a no-op after successful installation.
                DictionaryEntry.objects.exclude(pk='sample').delete()
                self.assertFalse(service.import_release(path)[1])
                (root/'manifest.json').write_text(json.dumps({'sha256':'wrong'}))
                with self.assertRaises(ValueError):service.import_release(path)

    def test_recording_pack_is_licensed_integral_and_imports_idempotently(self):
        result=service.import_recordings()
        self.assertGreater(result,0)
        self.assertEqual(service.import_recordings(),0)
        for sound in DictionaryAudio.objects.iterator():
            self.assertEqual(hashlib.sha256(sound.data).hexdigest(),sound.digest)
            self.assertTrue(sound.attribution['source'].startswith('https://commons.wikimedia.org/'))
            self.assertTrue(sound.attribution['license']['url'].startswith('https://creativecommons.org/licenses/'))

    def test_recordings_do_not_replace_oewn_ipa_with_unmatched_api_transcription(self):
        from learning.models import DictionarySupplement
        content=copy.deepcopy(self.entry.content)
        content[0]['phonetics']=[{'ipa':'/different-dialect/','audio':'/api/dictionary/audio/'+'b'*64+'/',
            'source':'https://commons.wikimedia.org/wiki/File:Example.ogg','license':service.LICENSE}]
        DictionarySupplement.objects.create(word='run',content=content)
        found=service.lookup_local('run')['entries'][0]['phonetics']
        self.assertEqual(found[0]['ipa'],'/rʌn/')
        self.assertEqual(found[1]['ipa'],'')
