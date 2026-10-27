from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from .models import GrammarReadProgress, FoundationAttempt, AICall
from .services.foundation_content import units


class GrammarReadProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = get_user_model().objects.create_user('read-progress-alice')
        cls.bob = get_user_model().objects.create_user('read-progress-bob')
        cls.unit = units('grammar')[0]['id']
        cls.url = f'/api/learn/grammar/{cls.unit}/read/'

    def setUp(self):
        self.client.force_login(self.alice)

    def mark(self, value):
        return self.client.post(self.url, {'is_read': value}, content_type='application/json')

    def test_reading_is_explicit_idempotent_and_separate_from_practice(self):
        detail = f'/api/learn/grammar/{self.unit}/'
        self.assertFalse(self.client.get(detail).json()['is_read'])
        self.assertFalse(GrammarReadProgress.objects.exists())
        self.assertEqual(self.mark(True).json(), {'is_read': True})
        first = GrammarReadProgress.objects.get()
        self.mark(True)
        self.assertEqual(GrammarReadProgress.objects.count(), 1)
        self.assertEqual(GrammarReadProgress.objects.get().read_at, first.read_at)
        self.assertTrue(self.client.get(detail).json()['is_read'])
        row = next(r for r in self.client.get('/api/learn/overview/?kind=grammar').json()['items'] if r['id'] == self.unit)
        self.assertTrue(row['is_read'])
        self.assertIsNone(row['progress'])
        self.assertEqual(FoundationAttempt.objects.count(), 0)
        self.assertEqual(AICall.objects.count(), 0)

    def test_account_isolation_and_reversible_marker(self):
        self.mark(True)
        self.client.force_login(self.bob)
        self.assertFalse(self.client.get(f'/api/learn/grammar/{self.unit}/').json()['is_read'])
        self.mark(False)
        self.assertTrue(GrammarReadProgress.objects.filter(owner=self.alice).exists())
        self.mark(True)
        self.assertEqual(GrammarReadProgress.objects.count(), 2)
        self.client.force_login(self.alice)
        self.assertEqual(self.mark(False).json(), {'is_read': False})
        self.mark(False)
        self.assertEqual(list(GrammarReadProgress.objects.values_list('owner_id', flat=True)), [self.bob.pk])

    def test_rejects_unknown_units_and_non_boolean_flags(self):
        for value in (None, '', 'true', 1, [], {}):
            with self.subTest(value=value):
                self.assertEqual(self.mark(value).status_code, 400)
        self.assertEqual(self.client.post('/api/learn/grammar/missing-unit/read/', {'is_read': True}, content_type='application/json').status_code, 404)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertFalse(GrammarReadProgress.objects.exists())

    def test_authentication_and_csrf(self):
        self.assertEqual(Client().post(self.url, {'is_read': True}, content_type='application/json').status_code, 401)
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.alice)
        self.assertEqual(csrf.post(self.url, {'is_read': True}, content_type='application/json').status_code, 403)
