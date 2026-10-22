import uuid
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
import django.utils.timezone
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
      migrations.CreateModel(name='Reading',fields=[
        ('id',models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,serialize=False)),
        ('title',models.CharField(max_length=200)),('text',models.TextField()),
        ('source_name',models.CharField(max_length=200,blank=True)),('analysis',models.JSONField(default=dict,blank=True)),
        ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
        ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
      ],options={'ordering':['-updated_at']}),
      migrations.CreateModel(name='Vocabulary',fields=[
        ('id',models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,serialize=False)),
        ('fingerprint',models.CharField(max_length=64)),('word',models.CharField(max_length=160)),
        ('pos',models.CharField(max_length=40,blank=True)),('meaning_vi',models.TextField()),
        ('synonyms',models.JSONField(default=list,blank=True)),('paraphrases',models.JSONField(default=list,blank=True)),
        ('example',models.TextField(blank=True)),('example_vi',models.TextField(blank=True)),
        ('context',models.TextField(blank=True)),('note',models.TextField(blank=True)),
        ('tags',models.JSONField(default=list,blank=True)),('source_label',models.CharField(max_length=200,blank=True)),
        ('origin',models.CharField(max_length=20,default='manual')),('verified',models.BooleanField(default=False)),
        ('due_at',models.DateTimeField(default=django.utils.timezone.now)),('interval_days',models.FloatField(default=0)),
        ('ease',models.FloatField(default=2.5)),('repetitions',models.PositiveIntegerField(default=0)),
        ('lapses',models.PositiveIntegerField(default=0)),('last_reviewed',models.DateTimeField(null=True,blank=True)),
        ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
        ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ('reading',models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL,to='learning.reading',null=True,blank=True)),
      ],options={'ordering':['-created_at']}),
      migrations.CreateModel(name='ReviewLog',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('token',models.UUIDField(default=uuid.uuid4)),('rating',models.CharField(max_length=8)),
        ('mode',models.CharField(max_length=20,default='flashcard')),('correct',models.BooleanField(null=True)),
        ('next_due',models.DateTimeField()),('created_at',models.DateTimeField(auto_now_add=True)),
        ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ('vocabulary',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='learning.vocabulary',related_name='reviews')),
      ]),
      migrations.CreateModel(name='ExerciseAttempt',fields=[
        ('id',models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,serialize=False)),
        ('mode',models.CharField(max_length=20)),('question',models.JSONField(default=dict)),
        ('correct_answer',models.TextField()),('answered',models.BooleanField(default=False)),
        ('submitted_answer',models.TextField(blank=True)),('correct',models.BooleanField(null=True)),
        ('created_at',models.DateTimeField(auto_now_add=True)),
        ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ('vocabulary',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='learning.vocabulary')),
      ]),
      migrations.CreateModel(name='AICall',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('task',models.CharField(max_length=20)),('model',models.CharField(max_length=80)),
        ('status',models.CharField(max_length=20,default='started')),('created_at',models.DateTimeField(auto_now_add=True)),
        ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
      ]),
      migrations.CreateModel(name='LoginFailure',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('key',models.CharField(max_length=64,db_index=True)),('created_at',models.DateTimeField(auto_now_add=True)),
      ]),
      migrations.AddConstraint(model_name='vocabulary',constraint=models.UniqueConstraint(fields=('owner','fingerprint'),name='unique_owner_sense')),
      migrations.AddIndex(model_name='vocabulary',index=models.Index(fields=['owner','due_at'],name='vocab_owner_due')),
      migrations.AddConstraint(model_name='reviewlog',constraint=models.UniqueConstraint(fields=('owner','token'),name='unique_review_token')),
    ]
