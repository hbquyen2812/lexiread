"""Study history must survive content deletion and must not count browsing."""
import json
import uuid
from datetime import date, datetime, timedelta, timezone as datetime_timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from learning.models import LearningDay, Reading, ReviewLog
from learning.services.core import InputError
from learning.services.motivation import learning_dates, summarize_days, validate_study_days
from learning.services.storage import export_library, import_library, review_entry, save_entry


class StudyHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='study-reader')
        self.other = get_user_model().objects.create_user(username='other-reader')
        self.client.force_login(self.user)
        self.reading = Reading.objects.create(owner=self.user, title='A short reading', text='A new day.')

    def progress(self, values):
        return self.client.post(f'/api/readings/{self.reading.pk}/progress/',
                                json.dumps(values), content_type='application/json')

    def test_completion_records_one_study_day_without_counting_open_or_favorite(self):
        self.assertEqual(self.client.get(f'/api/readings/{self.reading.pk}/').status_code, 200)
        self.assertEqual(self.progress({'favorite': True}).status_code, 200)
        self.assertFalse(LearningDay.objects.exists())
        self.assertEqual(self.progress({'completed': True}).status_code, 200)
        self.assertEqual(self.progress({'completed': True}).status_code, 200)
        self.assertEqual(list(LearningDay.objects.values_list('owner_id', 'date')),
                         [(self.user.pk, timezone.localdate())])

    def test_an_already_completed_reading_does_not_award_a_new_day(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        with patch('learning.services.motivation.timezone.localdate', return_value=yesterday):
            self.assertEqual(self.progress({'completed': True}).status_code, 200)
        self.assertEqual(self.progress({'completed': True}).status_code, 200)
        self.assertEqual(learning_dates(self.user), {yesterday})

    def test_other_users_cannot_mark_a_reading_as_completed(self):
        self.client.force_login(self.other)
        self.assertEqual(self.progress({'completed': True}).status_code, 404)
        self.assertFalse(LearningDay.objects.exists())

    def test_review_is_idempotent_and_history_survives_word_deletion(self):
        word, _ = save_entry(self.user, {'word': 'day', 'meaning_vi': 'ngày'})
        token = uuid.uuid4()
        review_entry(self.user, word.pk, 'good', token)
        self.assertTrue(review_entry(self.user, word.pk, 'good', token)['duplicate'])
        self.assertEqual(ReviewLog.objects.count(), 1)
        self.assertEqual(LearningDay.objects.count(), 1)
        word.delete()
        self.assertEqual(learning_dates(self.user), {timezone.localdate()})
        self.assertEqual(learning_dates(self.other), set())

    def test_legacy_review_history_uses_vietnam_day_at_utc_midnight_boundary(self):
        word, _ = save_entry(self.user, {'word': 'day', 'meaning_vi': 'ngày'})
        review = ReviewLog.objects.create(owner=self.user, vocabulary=word, rating='good',
                                         next_due=timezone.now())
        ReviewLog.objects.filter(pk=review.pk).update(
            created_at=datetime(2026, 1, 2, 18, 0, tzinfo=datetime_timezone.utc))
        with timezone.override('Asia/Ho_Chi_Minh'):
            self.assertEqual(learning_dates(self.user, date(2026, 1, 4)), {date(2026, 1, 3)})

    def test_backup_roundtrip_preserves_deleted_content_study_days_and_merges(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        LearningDay.objects.create(owner=self.user, date=yesterday)
        payload = export_library(self.user)
        self.assertEqual(payload['study_days'], [yesterday.isoformat()])
        import_library(self.other, payload)
        import_library(self.other, payload)
        self.assertEqual(learning_dates(self.other), {yesterday})
        self.assertEqual(LearningDay.objects.filter(owner=self.other).count(), 1)

    def test_backup_rejects_invalid_or_future_study_dates_atomically(self):
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        for invalid in (None, {}, [True], ['2026-13-01'], ['20260101'], [tomorrow]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(InputError):
                    validate_study_days(invalid)
        payload = export_library(self.user)
        payload['study_days'] = [tomorrow]
        with self.assertRaises(InputError):
            import_library(self.other, payload)
        self.assertFalse(Reading.objects.filter(owner=self.other).exists())
        self.assertFalse(LearningDay.objects.filter(owner=self.other).exists())

    def test_streak_grace_longest_rolling_window_and_future_dates(self):
        today = date(2026, 10, 26)
        days = {today - timedelta(days=n) for n in (1, 2, 3, 8, 9, 10, 11, 12, 29, 30)}
        days.add(today + timedelta(days=1))
        summary = summarize_days(days, today)
        self.assertEqual((summary['current'], summary['longest'], summary['active_days_30']), (3, 5, 9))
        self.assertFalse(summary['active_today'])
        self.assertEqual(summary['next_milestone'], 7)
        self.assertEqual(len(summary['week']), 7)
        self.assertEqual(summary['week'][-1], {'date': today.isoformat(), 'active': False, 'today': True})
        self.assertEqual(summarize_days(days, today + timedelta(days=3))['current'], 0)
