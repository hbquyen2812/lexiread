from django.core.management.base import BaseCommand
from django.db import transaction
from learning.models import ToeicPractice, ToeicAttempt
from learning.services.toeic import toeic_sets


class Command(BaseCommand):
    help='Bootstrap bộ TOEIC đi kèm, chỉ thêm mới; không ghi đè nội dung đã biên tập.'

    @transaction.atomic
    def handle(self,*args,**options):
        count=0
        for content in toeic_sets():
            obj,created=ToeicPractice.objects.get_or_create(slug=content['slug'],defaults={
                'title':content['title'],'revision':content['revision'],'published':True,'content':content})
            count+=int(created)
            # Pre-editorial attempts used only these bundled sets. Preserve that original.
            ToeicAttempt.objects.filter(set_slug=content['slug'],snapshot={}).update(snapshot=content)
        self.stdout.write(self.style.SUCCESS(f'Thêm {count} bộ TOEIC; giữ nguyên bộ đã có.'))
