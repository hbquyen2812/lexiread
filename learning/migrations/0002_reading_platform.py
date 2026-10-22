import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('learning','0001_initial')]
    operations=[
        migrations.AddField(model_name='reading',name='catalog_slug',field=models.SlugField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='reading',name='lesson_snapshot',field=models.JSONField(default=dict,blank=True)),
        migrations.AddField(model_name='reading',name='progress',field=models.JSONField(default=dict,blank=True)),
        migrations.AddConstraint(model_name='reading',constraint=models.UniqueConstraint(fields=['owner','catalog_slug'],condition=~models.Q(catalog_slug=''),name='one_lesson_per_owner')),
        migrations.CreateModel(name='CuratedLesson',fields=[
            ('slug',models.SlugField(primary_key=True,max_length=100,serialize=False)),
            ('title',models.CharField(max_length=200)),('level',models.CharField(max_length=2)),
            ('topic',models.CharField(max_length=120)),('revision',models.PositiveIntegerField(default=1)),
            ('order',models.PositiveIntegerField(default=0)),('published',models.BooleanField(default=True)),
            ('content',models.JSONField(default=dict)),('updated_at',models.DateTimeField(auto_now=True)),
        ],options={'ordering':['order','title']}),
        migrations.CreateModel(name='LessonAttempt',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('token',models.UUIDField(default=uuid.uuid4)),('answers',models.JSONField(default=dict)),
            ('result',models.JSONField(default=dict)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('reading',models.ForeignKey(to='learning.reading',on_delete=django.db.models.deletion.CASCADE,related_name='lesson_attempts')),
        ]),
        migrations.AddConstraint(model_name='lessonattempt',constraint=models.UniqueConstraint(fields=['reading','token'],name='unique_lesson_attempt')),
        migrations.CreateModel(name='ReadingQuestion',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('question',models.TextField()),('selected_text',models.TextField(blank=True)),
            ('result',models.JSONField(default=dict)),('source_hash',models.CharField(max_length=64)),
            ('origin',models.CharField(max_length=20,default='ai')),('created_at',models.DateTimeField(auto_now_add=True)),
            ('reading',models.ForeignKey(to='learning.reading',on_delete=django.db.models.deletion.CASCADE,related_name='questions')),
        ],options={'ordering':['-created_at']}),
    ]
