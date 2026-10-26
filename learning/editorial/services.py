"""Import validation and atomic publishing, independent of HTTP/UI."""
import json
import re
from datetime import timedelta

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from learning.models import ContentImport, CuratedLesson, ToeicPractice
from learning.services.catalog import validate_lesson, integer, LEVELS
from learning.services.core import InputError, clean_text, MAX_READING_CHARS
from learning.services.importers import extract_reading, MAX_FILE_BYTES
from learning.services.toeic import validate_toeic_set

MODELS = {'lesson': CuratedLesson, 'toeic': ToeicPractice}


def require_editor(user, kind):
    model = MODELS.get(kind)
    if not model or not user.is_active or not user.is_staff:
        raise PermissionDenied
    label = model._meta.model_name
    if not all(user.has_perm(f'learning.{action}_{label}') for action in ('add','change')):
        raise PermissionDenied
    return model


def validate_draft(raw):
    """Incomplete translations/questions are allowed only while unpublished."""
    if not isinstance(raw, dict): raise InputError('Nội dung phải là JSON object.')
    slug = clean_text(raw.get('slug',''),100,True)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug): raise InputError('Slug chỉ gồm chữ thường, số và dấu gạch nối.')
    if raw.get('level') not in LEVELS: raise InputError('Chọn trình độ A1–C2.')
    if raw.get('track','general') not in ('general','ielts'): raise InputError('Loại bài không hợp lệ.')
    analysis = raw.get('analysis',{})
    if not isinstance(analysis,dict): raise InputError('analysis phải là object.')
    for key in ('translations','vocabulary','grammar'):
        if not isinstance(analysis.get(key,[]),list): raise InputError(f'{key} phải là danh sách.')
    for key in ('questions','faqs'):
        if not isinstance(raw.get(key,[]),list): raise InputError(f'{key} phải là danh sách.')
    return {**raw,'slug':slug,'title':clean_text(raw.get('title',''),200,True),
            'topic':clean_text(raw.get('topic',''),120,True),'text':clean_text(raw.get('text',''),MAX_READING_CHARS),
            'summary':clean_text(raw.get('summary',''),800),'published':False,
            'track':raw.get('track','general'),
            'revision':integer(raw.get('revision',1),1,10000,'Phiên bản'),
            'order':integer(raw.get('order',0),0,100000,'Thứ tự')}


def read_package(upload, kind, metadata):
    if upload.size > MAX_FILE_BYTES: raise InputError('File tối đa 8 MB.')
    if upload.name.lower().endswith('.json'):
        try:
            raw = upload.read(MAX_FILE_BYTES+1)
            if len(raw)>MAX_FILE_BYTES: raise InputError('File tối đa 8 MB.')
            data = json.loads(raw.decode('utf-8-sig'))
        except (UnicodeError, ValueError, RecursionError) as exc:
            raise InputError('File JSON UTF-8 không hợp lệ.') from exc
        if isinstance(data,dict) and 'metadata' in data and 'lessons' in data:
            from .dataset import adapt_dataset
            data=adapt_dataset(data,kind)
        if isinstance(data,dict) and data.get('format')=='lexiread-content':
            if data.get('version')!=1 or data.get('kind')!=kind:
                raise InputError('Loại hoặc phiên bản gói nhập không khớp.')
            data = data.get('items')
        if isinstance(data,dict): data=[data]
        if not isinstance(data,list) or not 1<=len(data)<=100:
            raise InputError('Mỗi lần nhập cần 1–100 bài.')
        result=[]
        for index, row in enumerate(data,1):
            try:
                if kind=='toeic': item=validate_toeic_set(row)
                else:
                    item=validate_draft(row) if isinstance(row,dict) and row.get('published') is False else validate_lesson(row)
            except (ValueError,TypeError,KeyError,AttributeError) as exc:
                raise InputError(f'Bài {index}: {exc}') from exc
            # Import never silently publishes or replaces public content.
            item['published']=False
            result.append(item)
    else:
        if kind!='lesson': raise InputError('Bộ TOEIC cần file JSON theo mẫu.')
        result=[validate_draft({**metadata,'text':extract_reading(upload),'published':False,
                               'questions':[],'faqs':[],'analysis':{}})]
    if len({row['slug'] for row in result})!=len(result): raise InputError('Slug bị trùng trong cùng file.')
    return result


def version_of(obj):
    return {'revision':obj.revision,'updated_at':obj.updated_at.isoformat()} if obj else None


def preview_import(user, kind, payload, allow_update=False):
    model = require_editor(user,kind)
    existing = model.objects.in_bulk([row['slug'] for row in payload])
    expected={}
    for row in payload:
        obj=existing.get(row['slug'])
        if obj:
            if not allow_update: raise InputError(f"{obj.slug}: đã tồn tại. Bật cho phép cập nhật nếu muốn thay nội dung.")
            if obj.published: raise InputError(f'{obj.slug}: hãy bỏ xuất bản trước khi thay nội dung; bản học cá nhân vẫn được giữ.')
            if row['revision']<=obj.revision: raise InputError(f'{obj.slug}: phiên bản mới phải lớn hơn {obj.revision}.')
        expected[row['slug']]=version_of(obj)
    return ContentImport.objects.create(owner=user,kind=kind,payload=payload,expected=expected)


def audit(user,obj,new,message):
    LogEntry.objects.log_actions(user_id=user.pk,queryset=[obj],
        action_flag=ADDITION if new else CHANGE,change_message=message,single_object=True)


@transaction.atomic
def publish_batch(user,kind,expected):
    """Publish reviewed selections atomically, rejecting stale confirmations."""
    model=require_editor(user,kind)
    if not isinstance(expected,dict) or not 1<=len(expected)<=100:
        raise InputError('Chọn 1–100 bài để xuất bản.')
    objects=list(model.objects.select_for_update().filter(pk__in=expected).order_by('pk'))
    if len(objects)!=len(expected): raise InputError('Danh sách bài đã thay đổi. Hãy chọn lại.')
    count=0
    for obj in objects:
        if version_of(obj)!=expected[obj.pk]:
            raise InputError(f'{obj.pk}: đã được sửa sau khi xem trước. Hãy chọn lại.')
        if obj.published: continue
        obj.published=True
        obj.revision+=1
        obj.full_clean()
        obj.save()
        audit(user,obj,False,'Xuất bản sau xác nhận của biên tập viên; kiểm tra cấu trúc tự động thành công.')
        count+=1
    return count


@transaction.atomic
def apply_import(user, batch_id):
    batch=ContentImport.objects.select_for_update().get(pk=batch_id,owner=user)
    model=require_editor(user,batch.kind)
    if batch.applied_at: return batch,0
    if batch.created_at < timezone.now()-timedelta(minutes=30):
        raise InputError('Bản xem trước hết hạn sau 30 phút. Hãy nhập lại file.')
    existing={obj.pk:obj for obj in model.objects.select_for_update().filter(pk__in=batch.expected).order_by('pk')}
    for row in batch.payload:
        obj=existing.get(row['slug'])
        if version_of(obj)!=batch.expected[row['slug']]:
            raise InputError(f"{row['slug']}: nội dung đã thay đổi sau khi xem trước. Hãy nhập lại file.")
        new=obj is None
        if new: obj=model(slug=row['slug'])
        fields=('title','revision') if batch.kind=='toeic' else ('title','revision','level','track','topic','order')
        for field in fields: setattr(obj,field,row[field])
        obj.published=False
        obj.content=row
        obj.full_clean()
        obj.save(force_insert=new)
        audit(user,obj,new,'Nhập file qua bản xem trước; lưu nháp.')
    batch.applied_at=timezone.now()
    count=len(batch.payload)
    batch.payload=[]  # do not retain duplicate lesson bodies after applying
    batch.save(update_fields=['applied_at','payload'])
    return batch,count
