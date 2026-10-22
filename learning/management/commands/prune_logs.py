from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from learning.models import LoginFailure,ExerciseAttempt,AICall
class Command(BaseCommand):
    help='Remove expired transient attempts / throttle logs, but keep ReviewLog history.'
    def handle(self,*args,**options):
        now=timezone.now()
        LoginFailure.objects.filter(created_at__lt=now-timedelta(days=1)).delete()
        ExerciseAttempt.objects.filter(created_at__lt=now-timedelta(days=7)).delete()
        AICall.objects.filter(created_at__lt=now-timedelta(days=90)).delete()
        self.stdout.write('Pruned transient logs; saved review history unchanged.')
