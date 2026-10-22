import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at']
        constraints = [models.UniqueConstraint(fields=['owner','catalog_slug'], condition=~models.Q(catalog_slug=''), name='one_lesson_per_owner')]
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
        constraints = [models.UniqueConstraint(fields=['owner','fingerprint'],name='unique_owner_sense')]
        indexes = [models.Index(fields=['owner','due_at'],name='vocab_owner_due')]
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
    rating = models.CharField(max_length=8)
    mode = models.CharField(max_length=20,default='flashcard')
    correct = models.BooleanField(null=True)
    next_due = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner','token'],name='unique_review_token')]
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


class CuratedLesson(models.Model):
    """Shared editorial content. Opening it creates an immutable per-user snapshot."""
    slug = models.SlugField(primary_key=True, max_length=100)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=2)
    topic = models.CharField(max_length=120)
    revision = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)
    content = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['order', 'title']
    def clean(self):
        from django.core.exceptions import ValidationError
        from .services.catalog import validate_lesson
        from .services.core import InputError
        try:
            c = validate_lesson({**self.content,'slug':self.slug,'title':self.title,
                'level':self.level,'topic':self.topic,'revision':self.revision,
                'order':self.order,'published':self.published})
        except (InputError, TypeError, KeyError, AttributeError) as exc:
            raise ValidationError({'content': str(exc)}) from exc
        self.content = c
    def __str__(self): return self.title

class LessonAttempt(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name='lesson_attempts')
    token = models.UUIDField(default=uuid.uuid4)
    answers = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['reading','token'], name='unique_lesson_attempt')]

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
