import json
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core import signing
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from learning.models import ContentImport
from learning.services.core import InputError
from .forms import ImportForm, LessonEditorForm, ToeicEditorForm
from .services import require_editor, read_package, preview_import, apply_import, publish_batch, version_of


class ContentAdmin(admin.ModelAdmin):
    change_list_template='admin/editorial/change_list.html'
    readonly_fields=('revision','updated_at','source_note')
    actions=('export_selected','publish_selected',)

    @admin.action(description='Duyệt và xuất bản các bài đã chọn', permissions=['change'])
    def publish_selected(self,request,queryset):
        require_editor(request.user,self.kind)
        if not 1<=queryset.count()<=100:
            self.message_user(request,'Chọn 1–100 bài mỗi lần.',messages.ERROR)
            return None
        if request.POST.get('confirm_publish')=='yes':
            try:
                data=signing.loads(request.POST.get('preview_token',''),salt='editorial-publish',max_age=1800)
                if (data['owner']!=request.user.pk or data['kind']!=self.kind or
                        set(data['expected'])!=set(queryset.values_list('pk',flat=True))):
                    raise InputError('Bản xác nhận không khớp danh sách bài.')
                count=publish_batch(request.user,self.kind,data['expected'])
                self.message_user(request,f'Đã xuất bản {count} bài.',messages.SUCCESS)
            except (InputError,ValidationError,signing.BadSignature,KeyError,TypeError,IntegrityError) as exc:
                self.message_user(request,'Không xuất bản bài nào. Hãy chọn lại và kiểm tra: '+str(exc),messages.ERROR)
            return None
        objects=list(queryset)
        token=signing.dumps({'owner':request.user.pk,'kind':self.kind,
                            'expected':{obj.pk:version_of(obj) for obj in objects}},salt='editorial-publish')
        return TemplateResponse(request,'admin/editorial/publish.html',{
            **self.admin_site.each_context(request),'title':'Xác nhận xuất bản','opts':self.model._meta,
            'objects':objects,'preview_token':token})

    @admin.display(description='Nguồn gốc & lưu ý biên tập')
    def source_note(self,obj):
        info=(obj.content or {}).get('editorial',{})
        if not isinstance(info,dict): return 'Kiểm tra nguồn và quyền sử dụng trước khi xuất bản.'
        original=info.get('original',{})
        return f"{info.get('note','Nội dung nhập/biên soạn trực tiếp.')} Nhóm gốc: {original.get('track','—')}. {obj.content.get('provenance','')}"

    def get_readonly_fields(self,request,obj=None):
        return self.readonly_fields+(('slug',) if obj else ())

    def get_urls(self):
        custom=[path('import/',self.admin_site.admin_view(self.import_view),name=f'learning_{self.model._meta.model_name}_import'),
                path('import/<uuid:batch_id>/',self.admin_site.admin_view(self.preview_view),name=f'learning_{self.model._meta.model_name}_preview')]
        return custom+super().get_urls()

    def changelist_view(self,request,extra_context=None):
        url=reverse(f'admin:learning_{self.model._meta.model_name}_import')
        return super().changelist_view(request,{**(extra_context or {}),'import_url':url})

    def import_view(self,request):
        require_editor(request.user,self.kind)
        form=ImportForm(request.POST or None,request.FILES or None)
        if request.method=='POST' and form.is_valid():
            try:
                payload=read_package(form.cleaned_data['file'],self.kind,form.cleaned_data)
                batch=preview_import(request.user,self.kind,payload,form.cleaned_data['allow_update'])
                return redirect(f'admin:learning_{self.model._meta.model_name}_preview',batch_id=batch.pk)
            except (InputError,ValidationError) as exc: form.add_error(None,str(exc))
        return TemplateResponse(request,'admin/editorial/import.html',{
            **self.admin_site.each_context(request),'title':'Nhập nội dung thư viện — lưu nháp','opts':self.model._meta,'form':form,'kind':self.kind})

    def preview_view(self,request,batch_id):
        require_editor(request.user,self.kind)
        batch=ContentImport.objects.filter(pk=batch_id,owner=request.user,kind=self.kind).first()
        if not batch: raise Http404
        error=''
        if request.method=='POST' and request.POST.get('confirm')=='yes':
            try:
                batch,count=apply_import(request.user,batch.pk)
                self.message_user(request,f'Đã nhập {count} bài nháp. Mở từng bài để duyệt và xuất bản.',messages.SUCCESS)
                return redirect(f'admin:learning_{self.model._meta.model_name}_changelist')
            except (InputError,ValidationError,IntegrityError) as exc:
                error='Dữ liệu đã thay đổi hoặc không hợp lệ. Nhập lại file để xem trước.' if isinstance(exc,IntegrityError) else str(exc)
        rows=[{'slug':row['slug'],'title':row['title'],'level':row.get('level',''),
               'questions':len(row.get('questions',[])),'revision':row['revision'],
               'action':'Cập nhật' if batch.expected[row['slug']] else 'Thêm mới',
               'text':row.get('text') or '\n\n'.join(d['body'] for d in row.get('documents',[])),
               'needs_translation':self.kind=='lesson' and not row.get('analysis',{}).get('translations')}
              for row in batch.payload]
        return TemplateResponse(request,'admin/editorial/preview.html',{
            **self.admin_site.each_context(request),'title':'Xem trước — chưa ghi vào thư viện','opts':self.model._meta,
            'batch':batch,'rows':rows,'error':error})

    @admin.action(description='Xuất các bài đã chọn thành gói JSON (có đáp án, chỉ quản trị)')
    def export_selected(self,request,queryset):
        if queryset.count()>100:
            self.message_user(request,'Chọn tối đa 100 bài mỗi lần xuất.',messages.ERROR)
            return None
        items=[]
        for obj in queryset:
            fields=('slug','title','revision','published') if self.kind=='toeic' else ('slug','title','revision','published','level','track','topic','order')
            items.append({**obj.content,**{key:getattr(obj,key) for key in fields}})
        response=HttpResponse(json.dumps({'format':'lexiread-content','version':1,'kind':self.kind,'items':items},ensure_ascii=False,indent=2),content_type='application/json; charset=utf-8')
        response['Content-Disposition']=f'attachment; filename="lexiread-{self.kind}-content.json"'
        return response


class LessonContentAdmin(ContentAdmin):
    kind='lesson'
    form=LessonEditorForm
    list_display=('title','level','track','topic','revision','published','order')
    list_filter=('published','track','level','topic')
    search_fields=('title','slug','topic')
    fieldsets=(('Thông tin',{'fields':('slug','title','level','track','topic','order','revision','updated_at','source_note','edit_version')}),
               ('Bài đọc & bản dịch',{'fields':('summary','text','translation_status','translations')}),
               ('Câu hỏi',{'fields':('questions',)}),
               ('Nội dung bổ sung (không bắt buộc)',{'fields':('vocabulary','grammar','faqs'),'classes':('collapse',)}),
               ('Xuất bản',{'fields':('published',),'description':'Chỉ xuất bản sau khi duyệt nội dung. Hệ thống kiểm tra bản dịch, câu hỏi và trích dẫn; không tự thẩm định kiến thức.'}))


class ToeicContentAdmin(ContentAdmin):
    kind='toeic'
    form=ToeicEditorForm
    list_display=('title','revision','published','updated_at')
    list_filter=('published',)
    search_fields=('title','slug')
