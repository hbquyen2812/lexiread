"""Learning, not page visits. Dates use the application's Vietnam time zone."""
from datetime import date, timedelta

from django.utils import timezone

from ..models import LearningDay, LessonAttempt, ReviewLog, ToeicAttempt
from .core import InputError, calculate_review_streak


def record_learning(user):
    # Unique DB constraint makes multiple tabs/activities safe; caller owns transaction.
    return LearningDay.objects.get_or_create(owner=user, date=timezone.localdate())


def learning_dates(user, today=None):
    today = today or timezone.localdate()
    days = set(LearningDay.objects.filter(owner=user, date__lte=today).values_list('date', flat=True))
    # Include existing history without guessing completion dates from updated_at.
    for qs in (ReviewLog.objects.filter(owner=user),
               LessonAttempt.objects.filter(reading__owner=user),
               ToeicAttempt.objects.filter(owner=user)):
        days.update(qs.filter(created_at__date__lte=today).order_by()
                    .values_list('created_at__date', flat=True).distinct())
    return days


def summarize_days(days, today):
    days = {day for day in days if day <= today}
    longest = run = 0
    previous = None
    for day in sorted(days):
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    current = calculate_review_streak(days, today)
    target = next((n for n in (3, 7, 14, 30, 60, 100, 180, 365) if n > current),
                  ((current // 100) + 1) * 100)
    return {
        'current': current, 'longest': longest, 'active_today': today in days,
        'active_days_30': sum(today - timedelta(days=29) <= day for day in days),
        'next_milestone': target, 'milestone_percent': min(100, round(current / target * 100)),
        'timezone': str(timezone.get_current_timezone()),
        'week': [{'date': (day := today - timedelta(days=offset)).isoformat(),
                  'active': day in days, 'today': day == today} for offset in range(6, -1, -1)],
    }


def study_summary(user):
    today = timezone.localdate()
    return summarize_days(learning_dates(user, today), today)


def validate_study_days(values):
    if not isinstance(values, list) or len(values) > 36600:
        raise InputError('Lịch sử ngày học trong backup không hợp lệ.')
    clean = set()
    for value in values:
        try:
            day = date.fromisoformat(value)
        except (TypeError, ValueError):
            raise InputError('Ngày học cần có dạng YYYY-MM-DD.') from None
        if day.isoformat() != value or not date(2000, 1, 1) <= day <= timezone.localdate():
            raise InputError('Ngày học trong backup không hợp lệ hoặc nằm trong tương lai.')
        clean.add(day)
    return clean
