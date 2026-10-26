from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from learning.models import (DailyVisit, FoundationAttempt, LearningDay, LessonAttempt,
                             Reading, ReviewLog, ToeicAttempt, Vocabulary)
from learning.services.community import community_summary


class CommunitySummaryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = get_user_model().objects.create_user(username='learner')
        self.today = timezone.localdate()

    def events(self, owner):
        LearningDay.objects.create(owner=owner, date=self.today)
        reading = Reading.objects.create(owner=owner, title='Test', text='An example.')
        LessonAttempt.objects.create(reading=reading)
        ToeicAttempt.objects.create(owner=owner, set_slug='example')
        FoundationAttempt.objects.create(owner=owner, kind='grammar', unit_id='example')
        word = Vocabulary.objects.create(owner=owner, word='example', meaning_vi='ví dụ')
        ReviewLog.objects.create(owner=owner, vocabulary=word, rating='good', next_due=timezone.now())

    def test_public_empty_counts_are_zero_without_identity_or_traffic(self):
        DailyVisit.objects.create(owner=self.user, visitor_key='secret-session', views=999)
        result = self.client.get('/api/community/')
        self.assertEqual(result.status_code, 200)
        data = result.json()
        self.assertEqual(set(data), {'days','start_date','end_date','as_of','is_demo','active_learners','practice_attempts','word_reviews'})
        self.assertEqual([data[k] for k in ('active_learners','practice_attempts','word_reviews')], [0,0,0])
        self.assertNotIn('learner', result.content.decode().replace('active_learners',''))
        self.assertNotIn('secret-session', result.content.decode())
        self.assertEqual(self.client.post('/api/community/').status_code, 405)
        self.assertEqual(self.client.head('/api/community/').status_code, 200)

    def test_deduplicates_learners_and_combines_practice_types(self):
        self.events(self.user)
        LearningDay.objects.create(owner=self.user, date=self.today-timedelta(days=1))
        # Multiple devices and visits cannot inflate the learner count.
        for key in ('device-a','device-b'):
            DailyVisit.objects.create(owner=self.user, visitor_key=key, views=100)
        data = community_summary()
        self.assertEqual(data['active_learners'], 1)
        self.assertEqual(data['practice_attempts'], 3)
        self.assertEqual(data['word_reviews'], 1)

    @override_settings(PUBLIC_STATS_EXCLUDED_USERNAMES=('qa-reader','internal-check'))
    def test_excludes_staff_disabled_and_configured_test_accounts(self):
        self.events(self.user)
        for name, flags in [('admin',{'is_staff':True}),('root',{'is_superuser':True}),
                            ('disabled',{'is_active':False}),('qa-reader',{}),('internal-check',{})]:
            self.events(get_user_model().objects.create_user(username=name, **flags))
        data = community_summary()
        self.assertEqual([data[k] for k in ('active_learners','practice_attempts','word_reviews')], [1,3,1])

    def test_window_includes_first_day_and_excludes_old_and_future_events(self):
        self.events(self.user)
        LearningDay.objects.filter(owner=self.user).delete()
        first_day=self.today-timedelta(days=29)
        LearningDay.objects.create(owner=self.user, date=first_day)
        old=get_user_model().objects.create_user(username='old')
        future=get_user_model().objects.create_user(username='future')
        LearningDay.objects.create(owner=old, date=first_day-timedelta(days=1))
        LearningDay.objects.create(owner=future, date=self.today+timedelta(days=1))
        old_time=timezone.now()-timedelta(days=31)
        future_time=timezone.now()+timedelta(days=2)
        LessonAttempt.objects.all().update(created_at=old_time)
        ToeicAttempt.objects.all().update(created_at=future_time)
        ReviewLog.objects.all().update(created_at=old_time)
        data=community_summary()
        self.assertEqual(data['start_date'],first_day.isoformat())
        self.assertEqual([data[k] for k in ('active_learners','practice_attempts','word_reviews')],[1,1,0])

    @override_settings(QA_ONLY=True)
    def test_demo_is_labelled_and_landing_uses_the_same_snapshot(self):
        self.events(self.user)
        response=self.client.get('/')
        self.assertContains(response,'Hoạt động bản thử nghiệm')
        self.assertContains(response,'không phải số người dùng chính thức')
        self.assertEqual(response.context['community'],self.client.get('/api/community/').json())
        self.assertContains(response,'/guides/#guides/methods')

    def test_snapshot_is_reused_and_refreshes_after_cache_clear(self):
        first=community_summary()
        self.events(self.user)
        with self.assertNumQueries(0):
            self.assertEqual(community_summary(),first)
        cache.clear()
        self.assertEqual(community_summary()['active_learners'],1)
