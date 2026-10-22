from django.contrib import admin
from .models import Reading,Vocabulary,ReviewLog,AICall
@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display=('title','owner','updated_at')
    search_fields=('title',)
@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display=('word','pos','owner','verified','due_at')
    list_filter=('verified','origin')
    search_fields=('word','meaning_vi')
@admin.register(ReviewLog)
class ReviewAdmin(admin.ModelAdmin):
    list_display=('vocabulary','owner','rating','mode','created_at')
@admin.register(AICall)
class AIAdmin(admin.ModelAdmin):
    list_display=('owner','task','model','status','created_at')

from .models import CuratedLesson, LessonAttempt, ReadingQuestion
@admin.register(CuratedLesson)
class CuratedLessonAdmin(admin.ModelAdmin):
    list_display=('title','level','topic','revision','published','order')
    list_filter=('published','level','topic')
    search_fields=('title','slug','topic')
    fields=('slug','title','level','topic','revision','order','published','content')
    # Django ModelForm invokes clean(), validating every quotation before save.

@admin.register(LessonAttempt)
class LessonAttemptAdmin(admin.ModelAdmin):
    list_display=('reading','created_at')
    readonly_fields=('reading','token','answers','result','created_at')
    def has_add_permission(self,request):return False

@admin.register(ReadingQuestion)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display=('reading','origin','created_at')
    readonly_fields=('reading','question','selected_text','result','source_hash','origin','created_at')
    def has_add_permission(self,request):return False
