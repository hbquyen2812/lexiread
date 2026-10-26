"""Portable decks must not overwrite progress or cross account boundaries."""
import json
import uuid
from copy import deepcopy
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from .models import Vocabulary
from .services.storage import save_entry, review_entry
from .services.personal_decks import MAX_BYTES


class PersonalDeckTests(TestCase):
    def setUp(self):
        self.alice=get_user_model().objects.create_user(username='deck-alice')
        self.bob=get_user_model().objects.create_user(username='deck-bob')
        self.client.force_login(self.alice)
        self.deck={'format':'lexiread-vocabulary','version':1,'deck':{'name':'Email công việc'},
                   'vocabulary':[{'word':'confirm','meaning_vi':'xác nhận','example':'Please confirm the date.'},
                                 {'word':'reschedule','meaning_vi':'đổi lịch'}]}

    def post(self,deck=None,preview=False):
        return self.client.post('/api/vocabulary/deck/',json.dumps({'preview':preview,'deck':self.deck if deck is None else deck}),content_type='application/json')

    def test_preview_never_writes_and_deduplicates_normalized_senses(self):
        self.deck['vocabulary'].append({'word':' CONFIRM ','meaning_vi':'Xác nhận'})
        result=self.post(preview=True)
        self.assertEqual(result.status_code,200)
        self.assertEqual((result.json()['new'],result.json()['duplicates']),(2,1))
        self.assertFalse(Vocabulary.objects.exists())

    def test_reimport_preserves_personal_content_schedule_and_identity(self):
        old,_=save_entry(self.alice,{'word':'confirm','meaning_vi':'xác nhận','note':'Ghi chú của tôi','example':'My own example.','tags':['Đã học']})
        review_entry(self.alice,old.pk,'easy',uuid.uuid4());old.refresh_from_db()
        before=(old.due_at,old.last_reviewed,old.interval_days,old.repetitions,old.note,old.example)
        for _ in range(2):self.assertEqual(self.post().status_code,201)
        old.refresh_from_db()
        self.assertEqual((old.due_at,old.last_reviewed,old.interval_days,old.repetitions,old.note,old.example),before)
        self.assertEqual(set(old.tags),{'Đã học','Email công việc'})
        self.assertEqual(Vocabulary.objects.filter(owner=self.alice).count(),2)

    def test_same_word_different_sense_is_separate(self):
        self.deck['vocabulary'].append({'word':'confirm','meaning_vi':'củng cố'})
        self.assertEqual(self.post().json()['created'],3)

    def test_owner_and_schedule_fields_are_ignored(self):
        other,_=save_entry(self.bob,{'word':'confirm','meaning_vi':'xác nhận','tags':['Email công việc']})
        self.deck['vocabulary'][0].update(owner=self.bob.pk,id=str(other.pk),verified=True,origin='curated',
                                          due_at='2099-01-01',repetitions=100,tags=['Hidden'],reading_id=str(uuid.uuid4()))
        self.assertEqual(self.post(preview=True).json()['existing'],0)
        self.assertEqual(self.post().json()['created'],2)
        word=Vocabulary.objects.get(owner=self.alice,word='confirm')
        self.assertNotEqual(word.pk,other.pk);self.assertFalse(word.verified)
        self.assertEqual(word.origin,'import');self.assertEqual(word.repetitions,0)
        self.assertEqual(word.tags,['Email công việc']);self.assertIsNone(word.reading_id)
        self.assertEqual(Vocabulary.objects.filter(owner=self.bob).count(),1)

    def test_export_is_scoped_portable_and_can_be_reimported(self):
        self.post()
        save_entry(self.bob,{'word':'secret','meaning_vi':'bí mật','tags':['Email công việc']})
        save_entry(self.alice,{'word':'outside','meaning_vi':'bên ngoài','tags':['Khác']})
        response=self.client.get('/api/vocabulary/deck/',{'name':'Email công việc'})
        self.assertEqual(response.status_code,200);data=response.json()
        self.assertEqual(len(data['vocabulary']),2)
        for row in data['vocabulary']:
            for field in ('id','owner','due_at','repetitions','verified','reading_id','tags'):self.assertNotIn(field,row)
        self.assertEqual(self.post(data).json()['created'],0)
        with patch('learning.services.personal_decks.MAX_BYTES',1024):
            self.assertEqual(self.client.get('/api/vocabulary/deck/',{'name':'Email công việc'}).status_code,400)
        self.assertEqual(self.client.get('/api/vocabulary/deck/?name=missing').status_code,400)

    def test_invalid_last_row_rolls_back_entire_file(self):
        self.deck['vocabulary'].append({'word':'broken'})
        self.assertEqual(self.post().status_code,400)
        self.assertFalse(Vocabulary.objects.exists())

    def test_file_contract_and_limits(self):
        for field,value in [('version',True),('version',2),('format','backup'),('vocabulary',[]),('vocabulary',[{}]*501),('deck',{'name':'x'*101})]:
            with self.subTest(field=field,value=str(value)[:20]):
                data=deepcopy(self.deck);data[field]=value
                self.assertEqual(self.post(data).status_code,400)
        data=deepcopy(self.deck);data['vocabulary'][0]['note']='x'*4001
        self.assertEqual(self.post(data).status_code,400)
        self.assertEqual(self.client.post('/api/vocabulary/deck/',' '* (MAX_BYTES+1),content_type='application/json').status_code,400)
        self.assertFalse(Vocabulary.objects.exists())

    def test_tag_limit_rejects_all_rows_without_dropping_existing_sets(self):
        old,_=save_entry(self.alice,{'word':'reschedule','meaning_vi':'đổi lịch','tags':[str(n) for n in range(20)]})
        self.assertEqual(self.post().status_code,400);old.refresh_from_db()
        self.assertEqual(len(old.tags),20);self.assertEqual(Vocabulary.objects.count(),1)

    def test_login_csrf_and_explicit_preview_required(self):
        self.assertEqual(self.client.post('/api/vocabulary/deck/',json.dumps({'deck':self.deck}),content_type='application/json').status_code,400)
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.alice)
        self.assertEqual(strict.post('/api/vocabulary/deck/',json.dumps({'preview':False,'deck':self.deck}),content_type='application/json').status_code,403)
        self.client.logout()
        self.assertEqual(self.post().status_code,401)
        self.assertEqual(self.client.get('/api/vocabulary/deck/?name=x').status_code,401)
