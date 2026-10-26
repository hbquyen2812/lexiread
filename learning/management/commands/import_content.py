from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from learning.editorial.services import read_package, preview_import, apply_import


class Command(BaseCommand):
    help='Kiểm tra gói JSON; thêm --apply --editor USERNAME để lưu nháp. Không tự xuất bản.'
    def add_arguments(self,parser):
        parser.add_argument('file')
        parser.add_argument('--kind',choices=['lesson','toeic'],default='lesson')
        parser.add_argument('--apply',action='store_true')
        parser.add_argument('--editor')
        parser.add_argument('--update',action='store_true')

    def handle(self,*args,**options):
        try:
            path=Path(options['file'])
            if path.stat().st_size>8*1024*1024: raise ValueError('File tối đa 8 MB.')
            payload=read_package(SimpleUploadedFile(path.name,path.read_bytes()),options['kind'],{})
            self.stdout.write(f"Hợp lệ để nhập nháp: {len(payload)} bài ({options['kind']}).")
            if not options['apply']:
                self.stdout.write('Chỉ kiểm tra, chưa ghi database. Dùng /admin/ để xem trước và xác nhận.')
                return
            if not options['editor']: raise ValueError('Cần --editor USERNAME có quyền thêm và sửa nội dung.')
            user=get_user_model().objects.get(username=options['editor'])
            batch=preview_import(user,options['kind'],payload,options['update'])
            _,count=apply_import(user,batch.pk)
            self.stdout.write(self.style.SUCCESS(f'Đã lưu {count} bài nháp. Chưa xuất bản.'))
        except (ValueError,OSError,get_user_model().DoesNotExist) as exc:
            raise CommandError(str(exc)) from exc
