from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from learning.models import AICall, DailyVisit, ExerciseAttempt, LoginFailure


class Command(BaseCommand):
    help = "Remove expired transient logs and analytics; keep ReviewLog history."

    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()
        LoginFailure.objects.filter(created_at__lt=now - timedelta(days=1)).delete()
        ExerciseAttempt.objects.filter(created_at__lt=now - timedelta(days=7)).delete()
        AICall.objects.filter(created_at__lt=now - timedelta(days=90)).delete()
        DailyVisit.objects.filter(date__lt=today - timedelta(days=400)).delete()
        self.stdout.write(
            "Pruned transient logs and analytics older than 400 days; "
            "saved review history unchanged."
        )
