import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class DictionaryRelease(models.Model):
    key = models.CharField(max_length=80, primary_key=True)
    checksum = models.CharField(max_length=64)
    entry_count = models.PositiveIntegerField(default=0)
    ipa_count = models.PositiveIntegerField(default=0)
    imported_at = models.DateTimeField(auto_now=True)


class DictionaryEntry(models.Model):
    word = models.CharField(max_length=160, primary_key=True)
    display_word = models.CharField(max_length=160)
    definition = models.TextField(blank=True)
    content = models.JSONField(default=list)
    release = models.ForeignKey(DictionaryRelease, on_delete=models.PROTECT)

    class Meta:
        ordering = ['word']


class DictionaryForm(models.Model):
    form = models.CharField(max_length=160, db_index=True)
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='forms')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['form', 'entry'], name='unique_dictionary_form')]


class DictionaryAudio(models.Model):
    digest = models.CharField(max_length=64, primary_key=True)
    data = models.BinaryField()
    mime = models.CharField(max_length=40)
    attribution = models.JSONField(default=dict)


class DictionarySupplement(models.Model):
    word = models.CharField(max_length=160, primary_key=True)
    content = models.JSONField(default=list)


class VocabularyCollection(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100, db_index=True)
    level = models.CharField(max_length=2, db_index=True)
    order = models.PositiveIntegerField(default=0)
    content = models.JSONField(default=dict)

    class Meta:
        ordering = ['order', 'slug']

class Reading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    source_name = models.CharField(max_length=200,blank=True)
    catalog_slug = models.SlugField(max_length=100,blank=True,default='')
    lesson_snapshot = models.JSONField(default=dict,blank=True)
    progress = models.JSONField(default=dict,blank=True)
    analysis = models.JSONField(default=dict,blank=True)
    import_key = models.UUIDField(null=True,blank=True,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['owner','catalog_slug'], condition=~models.Q(catalog_slug=''), name='one_lesson_per_owner'),
            models.UniqueConstraint(fields=['owner','import_key'], condition=models.Q(import_key__isnull=False), name='unique_owner_import_key'),
        ]
        indexes = [models.Index(fields=['owner','updated_at'],name='reading_owner_updated')]
    def __str__(self): return self.title
class Vocabulary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    fingerprint = models.CharField(max_length=64)
    word = models.CharField(max_length=160)
    pos = models.CharField(max_length=40,blank=True)
    meaning_vi = models.TextField()
    synonyms = models.JSONField(default=list,blank=True)
    paraphrases = models.JSONField(default=list,blank=True)
    example = models.TextField(blank=True)
    example_vi = models.TextField(blank=True)
    usage_pattern = models.CharField(max_length=300, blank=True)
    context = models.TextField(blank=True)
    note = models.TextField(blank=True)
    tags = models.JSONField(default=list,blank=True)
    source_label = models.CharField(max_length=200,blank=True)
    reading = models.ForeignKey(Reading,on_delete=models.SET_NULL,null=True,blank=True)
    origin = models.CharField(max_length=20,default='manual')
    verified = models.BooleanField(default=False)
    due_at = models.DateTimeField(default=timezone.now)
    interval_days = models.FloatField(default=0)
    ease = models.FloatField(default=2.5)
    repetitions = models.PositiveIntegerField(default=0)
    lapses = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['owner','fingerprint'],name='unique_owner_sense'),
            models.CheckConstraint(condition=models.Q(interval_days__gte=0,interval_days__lte=365),name='valid_vocab_interval'),
            models.CheckConstraint(condition=models.Q(ease__gte=1.3,ease__lte=3),name='valid_vocab_ease'),
        ]
        indexes = [
            models.Index(fields=['owner','due_at'],name='vocab_owner_due'),
            models.Index(fields=['owner','last_reviewed','interval_days'],name='vocab_owner_progress'),
        ]
    def save(self, *args, **kwargs):
        from .services.core import fingerprint
        self.fingerprint = fingerprint(self.word, self.meaning_vi)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'fingerprint'}
        super().save(*args, **kwargs)
    def __str__(self): return self.word
class ReviewLog(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(Vocabulary,on_delete=models.CASCADE,related_name='reviews')
    token = models.UUIDField(default=uuid.uuid4)
    rating = models.CharField(max_length=8,choices=[('again','Again'),('hard','Hard'),('good','Good'),('easy','Easy')])
    mode = models.CharField(max_length=20,default='flashcard')
    correct = models.BooleanField(null=True)
    next_due = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner','token'],name='unique_review_token'),
            models.CheckConstraint(condition=models.Q(rating__in=['again','hard','good','easy']),name='valid_review_rating'),
        ]
        indexes = [models.Index(fields=['owner','created_at'],name='review_owner_created')]

class VocabularyOccurrence(models.Model):
    """A saved sense may be encountered in several readings without duplicating its schedule."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(Vocabulary,on_delete=models.CASCADE,related_name='occurrences')
    reading = models.ForeignKey(Reading,on_delete=models.SET_NULL,null=True,blank=True,related_name='vocabulary_occurrences')
    source_label = models.CharField(max_length=200,blank=True)
    context = models.TextField(blank=True)
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
        constraints = [models.UniqueConstraint(fields=['owner','vocabulary','fingerprint'],name='unique_vocab_occurrence')]
        indexes = [models.Index(fields=['owner','reading'],name='occurrence_owner_reading')]
    def save(self,*args,**kwargs):
        from .services.core import occurrence_fingerprint
        self.fingerprint=occurrence_fingerprint(self.reading_id,self.source_label,self.context)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields']=set(kwargs['update_fields'])|{'fingerprint'}
        super().save(*args,**kwargs)
    def __str__(self): return f'{self.vocabulary} · {self.source_label or "nguồn riêng"}'
class ExerciseAttempt(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(Vocabulary,on_delete=models.CASCADE)
    mode = models.CharField(max_length=20)
    question = models.JSONField(default=dict)
    correct_answer = models.TextField()
    answered = models.BooleanField(default=False)
    submitted_answer = models.TextField(blank=True)
    correct = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
class AICall(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    task = models.CharField(max_length=20)
    model = models.CharField(max_length=80)
    status = models.CharField(max_length=20,default='started')
    created_at = models.DateTimeField(auto_now_add=True)
class LoginFailure(models.Model):
    # Hash avoids storing the raw IP address / entered username in this log.
    key = models.CharField(max_length=64,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuthRateLimit(models.Model):
    """Persistent, atomic budgets; keys contain hashes, never raw email/IP."""
    key = models.CharField(max_length=64, primary_key=True)
    started_at = models.DateTimeField(default=timezone.now)
    last_at = models.DateTimeField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)


class CuratedLesson(models.Model):
    """Shared editorial content. Opening it creates an immutable per-user snapshot."""
    slug = models.SlugField(primary_key=True, max_length=100)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=6)
    topic = models.CharField(max_length=120)
    track = models.CharField(max_length=12, default='general', choices=[('general','General'),('ielts','IELTS')], db_index=True)
    revision = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)
    content = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['order', 'title']
    def clean(self):
        from django.core.exceptions import ValidationError
        from .services.catalog import validate_lesson
        from .services.core import InputError
        try:
            raw = {**self.content,'slug':self.slug,'title':self.title,
                'level':self.level,'topic':self.topic,'revision':self.revision,
                'track':self.track,'order':self.order,'published':self.published}
            if self.published:
                c = validate_lesson(raw)
            else:
                from .editorial.services import validate_draft
                c = validate_draft(raw)
        except (InputError, TypeError, KeyError, AttributeError) as exc:
            raise ValidationError(str(exc)) from exc
        self.content = c
    def __str__(self): return self.title


class ToeicPractice(models.Model):
    """Shared TOEIC content; bundled files are bootstrap data, not the live source."""
    slug = models.SlugField(primary_key=True, max_length=100)
    title = models.CharField(max_length=200)
    revision = models.PositiveIntegerField(default=1)
    published = models.BooleanField(default=False)
    content = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def clean(self):
        from django.core.exceptions import ValidationError
        from .services.toeic import validate_toeic_set
        try:
            self.content = validate_toeic_set({**self.content, 'slug':self.slug, 'title':self.title, 'revision':self.revision})
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ValidationError({'content':str(exc)}) from exc

    def __str__(self): return self.title


class ContentImport(models.Model):
    """Owner-scoped, short-lived preview. Applied batches cannot be replayed."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField(max_length=12)
    payload = models.JSONField(default=list)
    expected = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    applied_at = models.DateTimeField(null=True, blank=True)

class LessonAttempt(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name='lesson_attempts')
    token = models.UUIDField(default=uuid.uuid4)
    answers = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['reading','token'], name='unique_lesson_attempt')]

class ToeicAttempt(models.Model):
    """A personal result for an original TOEIC-style practice set."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    set_slug = models.SlugField(max_length=100)
    token = models.UUIDField(default=uuid.uuid4)
    answers = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    snapshot = models.JSONField(default=dict, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['owner','token'],name='unique_toeic_attempt_token'),
            models.CheckConstraint(condition=models.Q(duration_seconds__lte=7200),name='valid_toeic_duration'),
        ]
        indexes = [models.Index(fields=['owner','set_slug','created_at'],name='toeic_owner_set_date')]

class LearningDay(models.Model):
    """One real learning day, independent of traffic and deletable source content."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['date']
        constraints = [models.UniqueConstraint(fields=['owner', 'date'], name='unique_learning_day')]


class LearningProfile(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.CharField(max_length=2, default='A1')
    goal = models.CharField(max_length=12, default='general')
    daily_minutes = models.PositiveSmallIntegerField(default=15)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(level__in=['A1','A2','B1','B2','C1','C2']), name='valid_learning_level'),
            models.CheckConstraint(condition=models.Q(goal__in=['general','ielts','toeic']), name='valid_learning_goal'),
            models.CheckConstraint(condition=models.Q(daily_minutes__in=[15,30,45,60]), name='valid_learning_minutes'),
        ]


class FoundationAttempt(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField(max_length=12)
    unit_id = models.SlugField(max_length=100)
    token = models.UUIDField(default=uuid.uuid4)
    answers = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['owner','token'], name='unique_foundation_attempt'),
            models.CheckConstraint(condition=models.Q(kind__in=['grammar','vocabulary']), name='valid_foundation_kind'),
        ]
        indexes = [models.Index(fields=['owner','kind','unit_id'], name='foundation_owner_unit')]


class DailyVisit(models.Model):
    """Privacy-preserving daily traffic row; stores a salted session hash, never an IP."""
    date = models.DateField(default=timezone.localdate)
    visitor_key = models.CharField(max_length=64)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    views = models.PositiveIntegerField(default=1)
    page_counts = models.JSONField(default=dict,blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-date','-last_seen']
        constraints = [models.UniqueConstraint(fields=['date','visitor_key'],name='unique_daily_visitor')]
        indexes = [
            models.Index(fields=['date'],name='visit_date'),
            models.Index(fields=['owner','date'],name='visit_owner_date'),
        ]

class ReadingQuestion(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    selected_text = models.TextField(blank=True)
    result = models.JSONField(default=dict)
    source_hash = models.CharField(max_length=64)
    origin = models.CharField(max_length=20, default='ai')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
