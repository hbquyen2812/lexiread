from django import forms
from learning.models import CuratedLesson, ToeicPractice
from learning.services.catalog import LEVELS
from learning.services.core import paragraphs


class ImportForm(forms.Form):
    file=forms.FileField(label='File JSON / TXT / MD / DOCX / PDF có chữ')
    allow_update=forms.BooleanField(required=False,label='Cho phép cập nhật bài nháp trùng slug (cần tăng revision)')
    slug=forms.SlugField(required=False,max_length=100,label='Mã bài (chỉ cần cho tài liệu không phải JSON)')
    title=forms.CharField(required=False,max_length=200,label='Tên bài')
    level=forms.ChoiceField(choices=[(level,level) for level in LEVELS],initial='A2',label='Trình độ ước lượng')
    track=forms.ChoiceField(choices=[('general','Đọc tổng quát'),('ielts','IELTS')],label='Nhánh học')
    topic=forms.CharField(required=False,max_length=120,label='Chủ đề')


class VersionedForm(forms.ModelForm):
    edit_version=forms.CharField(required=False,widget=forms.HiddenInput)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.existing=bool(self.instance and not self.instance._state.adding)
        if self.existing: self.fields['edit_version'].initial=self.instance.updated_at.isoformat()

    def clean(self):
        cleaned=super().clean()
        if self.existing:
            # Admin wraps POST change forms in a transaction; serialize editors.
            current=type(self.instance).objects.select_for_update().get(pk=self.instance.pk)
            if cleaned.get('edit_version')!=current.updated_at.isoformat():
                raise forms.ValidationError('Bài đã được người khác sửa. Tải lại trang trước khi chỉnh tiếp.')
            self.instance.revision=current.revision+1
        return cleaned


class LessonEditorForm(VersionedForm):
    level=forms.ChoiceField(choices=[(level,level) for level in LEVELS],label='Trình độ ước lượng')
    summary=forms.CharField(required=False,max_length=800,widget=forms.Textarea(attrs={'rows':3}),label='Giới thiệu ngắn')
    text=forms.CharField(required=False,max_length=60000,widget=forms.Textarea(attrs={'rows':14,'cols':100}),label='Bài đọc tiếng Anh',help_text='Mỗi đoạn cách nhau một dòng trống.')
    translation_status=forms.ChoiceField(required=False,choices=[('complete','Có đầy đủ bản dịch'),('not_provided','Chưa có bản dịch — công khai nhãn cho người học')],initial='complete',label='Trạng thái bản dịch')
    translations=forms.CharField(required=False,widget=forms.Textarea(attrs={'rows':12,'cols':100}),label='Bản dịch tiếng Việt',help_text='Mỗi đoạn cách nhau một dòng trống. Nếu chọn chưa có bản dịch, để trống toàn bộ; không dùng bản dịch giả.')
    questions=forms.JSONField(required=False,widget=forms.Textarea(attrs={'rows':12,'class':'editorial-questions'}),label='Câu hỏi',help_text='Chọn đáp án theo chỉ số từ 0. Trích dẫn phải khớp nguyên văn đoạn nguồn.')
    vocabulary=forms.JSONField(required=False,widget=forms.Textarea(attrs={'rows':8}),label='Từ vựng (JSON, không bắt buộc)')
    grammar=forms.JSONField(required=False,widget=forms.Textarea(attrs={'rows':6}),label='Ngữ pháp (JSON, không bắt buộc)')
    faqs=forms.JSONField(required=False,widget=forms.Textarea(attrs={'rows':6}),label='Giải đáp (JSON, không bắt buộc)')

    class Meta:
        model=CuratedLesson
        fields=['slug','title','level','track','topic','order','published']

    class Media:
        js=('editorial.js',)
        css={'all':('editorial.css',)}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        content=self.instance.content or {}
        self.fields['translation_status'].initial=content.get('translation_status','complete')
        for name in ('text','summary','questions','faqs'):
            self.fields[name].initial=content.get(name,[] if name in ('questions','faqs') else '')
        analysis=content.get('analysis',{})
        self.fields['translations'].initial='\n\n'.join(item.get('vi','') for item in analysis.get('translations',[]))
        for name in ('vocabulary','grammar'): self.fields[name].initial=analysis.get(name,[])

    def clean(self):
        values=super().clean()
        content={**(self.instance.content or {}),'text':values.get('text',''),'summary':values.get('summary',''),
                 'questions':values.get('questions') or [],'faqs':values.get('faqs') or [],
                 'translation_status':values.get('translation_status') or 'complete'}
        content['analysis']={'translations':[{'index':i,'vi':text} for i,text in enumerate(paragraphs(values['translations']))] if values.get('translations') else [],
                             'vocabulary':values.get('vocabulary') or [],'grammar':values.get('grammar') or []}
        self.instance.content=content
        return values


class ToeicEditorForm(VersionedForm):
    class Meta:
        model=ToeicPractice
        fields=['slug','title','published','content']
