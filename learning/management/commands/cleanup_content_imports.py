from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from learning.models import ContentImport


class Command(BaseCommand):
    help='Xóa bản xem trước nhập file cũ hơn 7 ngày; không xóa bài hay nhật ký admin.'
    def handle(self,*args,**options):
        count,_=ContentImport.objects.filter(created_at__lt=timezone.now()-timedelta(days=7)).delete()
        self.stdout.write(f'Đã dọn {count} bản xem trước quá hạn.')
