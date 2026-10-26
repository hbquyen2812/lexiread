import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from learning.models import CuratedLesson
from learning.services.catalog import validate_lesson
from learning.services.core import InputError

class Command(BaseCommand):
    help='Nạp thư viện cố định. Mặc định chỉ thêm, không ghi đè bài/tiến độ đã có.'
    def add_arguments(self, parser):
        parser.add_argument('--directory',default=str(settings.BASE_DIR/'data'/'lessons'))
        parser.add_argument('--update',action='store_true',help='Cập nhật bài chuẩn; không đổi snapshot đã mở của người học.')
    @transaction.atomic
    def handle(self,*args,**options):
        paths=sorted(Path(options['directory']).glob('*.json'))
        if not paths:raise CommandError('Không có file JSON bài đọc trong thư mục.')
        made=changed=0
        for path in paths:
            try:c=validate_lesson(json.loads(path.read_text(encoding='utf-8')))
            except (ValueError,TypeError,KeyError,AttributeError,InputError) as exc:raise CommandError(f'{path.name}: {exc}') from exc
            fields={k:c[k] for k in ('title','level','track','topic','revision','order','published')}
            fields['content']=c
            lesson,new=CuratedLesson.objects.get_or_create(slug=c['slug'],defaults=fields)
            made+=int(new)
            if not new and options['update']:
                if c['revision']<=lesson.revision:
                    continue
                for k,v in fields.items():setattr(lesson,k,v)
                lesson.full_clean();lesson.save();changed+=1
        self.stdout.write(self.style.SUCCESS(f'Thêm {made}; cập nhật {changed}; giữ {len(paths)-made-changed} bài chuẩn. Không thay đổi kho từ cá nhân.'))
