"""Public aggregates only; never expose identities or equate page views with people."""
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from ..models import FoundationAttempt, LearningDay, LessonAttempt, ReviewLog, ToeicAttempt


def community_summary():
    today = timezone.localdate()
    start = today - timedelta(days=29)
    # A small shared snapshot bounds the cost of the anonymous endpoint and landing page.
    key = f'community-summary-v1:{today}'
    summary = cache.get(key)
    if summary is not None:
        return summary
    excluded = getattr(settings, 'PUBLIC_STATS_EXCLUDED_USERNAMES', ('qa-reader', 'qa-editor'))
    learners = get_user_model().objects.filter(is_active=True, is_staff=False, is_superuser=False).exclude(username__in=excluded)
    tz = timezone.get_current_timezone()
    beginning = timezone.make_aware(datetime.combine(start, time.min), tz)
    end = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min), tz)
    period = {'created_at__gte': beginning, 'created_at__lt': end}
    practice_count = sum(model.objects.filter(**period, **{owner: learners}).count()
                         for model, owner in ((LessonAttempt, 'reading__owner__in'),
                                              (ToeicAttempt, 'owner__in'),
                                              (FoundationAttempt, 'owner__in')))
    summary = {
        'days': 30, 'start_date': start.isoformat(), 'end_date': today.isoformat(),
        'as_of': timezone.now().isoformat(),
        'is_demo': bool(getattr(settings, 'QA_ONLY', False)),
        'active_learners': LearningDay.objects.filter(owner__in=learners, date__range=(start, today)).values('owner').distinct().count(),
        'practice_attempts': practice_count,
        'word_reviews': ReviewLog.objects.filter(owner__in=learners, **period).count(),
    }
    cache.set(key, summary, 60)
    return summary
