from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import EmailUserChangeForm,EmailUserCreationForm
from .models import Reading,Vocabulary,ReviewLog,AICall,VocabularyOccurrence

User=get_user_model()
admin.site.unregister(User)
@admin.register(User)
class EmailUserAdmin(UserAdmin):
    add_form=EmailUserCreationForm
    form=EmailUserChangeForm
    add_fieldsets=UserAdmin.add_fieldsets+(("Email đăng nhập",{'fields':('email',)}),)
    list_display=('username','email','is_staff','is_active')
    search_fields=('username','email')
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

@admin.register(VocabularyOccurrence)
class VocabularyOccurrenceAdmin(admin.ModelAdmin):
    list_display=('vocabulary','source_label','reading','owner','created_at')
    search_fields=('vocabulary__word','source_label','context')
    readonly_fields=('owner','vocabulary','reading','source_label','context','fingerprint','created_at')
    def has_add_permission(self,request):return False

from .models import CuratedLesson, LessonAttempt, ReadingQuestion, ToeicAttempt, DailyVisit
from .models import ToeicPractice
from .models import DictionaryEntry, DictionaryRelease, VocabularyCollection
from .editorial.admin import LessonContentAdmin, ToeicContentAdmin
admin.site.register(CuratedLesson,LessonContentAdmin)
admin.site.register(ToeicPractice,ToeicContentAdmin)


@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    list_display = ('display_word', 'release')
    search_fields = ('=word', '^word')
    readonly_fields = ('word', 'display_word', 'definition', 'content', 'release')
    show_full_result_count = False
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(DictionaryRelease)
class DictionaryReleaseAdmin(admin.ModelAdmin):
    list_display = ('key', 'entry_count', 'ipa_count', 'imported_at')
    readonly_fields = ('key', 'checksum', 'entry_count', 'ipa_count', 'imported_at')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(VocabularyCollection)
class VocabularyCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'level')
    list_filter = ('topic', 'level')
    search_fields = ('title', 'topic')
    readonly_fields = ('slug', 'title', 'topic', 'level', 'order', 'content')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(LessonAttempt)
class LessonAttemptAdmin(admin.ModelAdmin):
    list_display=('reading','created_at')
    readonly_fields=('reading','token','answers','result','created_at')
    def has_add_permission(self,request):return False

@admin.register(ToeicAttempt)
class ToeicAttemptAdmin(admin.ModelAdmin):
    list_display=('owner','set_slug','duration_seconds','created_at')
    readonly_fields=('owner','set_slug','token','answers','result','snapshot','duration_seconds','created_at')
    def has_add_permission(self,request):return False

@admin.register(DailyVisit)
class DailyVisitAdmin(admin.ModelAdmin):
    list_display=('date','owner','views','first_seen','last_seen')
    list_filter=('date',)
    readonly_fields=('date','visitor_key','owner','views','page_counts','first_seen','last_seen')
    def has_add_permission(self,request):return False

@admin.register(ReadingQuestion)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display=('reading','origin','created_at')
    readonly_fields=('reading','question','selected_text','result','source_hash','origin','created_at')
    def has_add_permission(self,request):return False
