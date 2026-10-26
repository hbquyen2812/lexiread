import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def backfill_tracks(apps,schema_editor):
    Lesson=apps.get_model('learning','CuratedLesson')
    for lesson in Lesson.objects.all().iterator():
        track=lesson.content.get('track','general')
        if track in ('general','ielts'): Lesson.objects.filter(pk=lesson.pk).update(track=track)


class Migration(migrations.Migration):
    dependencies=[('learning','0006_daily_visit'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.AlterField(model_name='curatedlesson',name='level',field=models.CharField(max_length=6)),
        migrations.AddField(model_name='curatedlesson',name='track',field=models.CharField(choices=[('general','General'),('ielts','IELTS')],db_index=True,default='general',max_length=12)),
        migrations.AlterField(model_name='curatedlesson',name='published',field=models.BooleanField(default=False)),
        migrations.RunPython(backfill_tracks,migrations.RunPython.noop),
        migrations.CreateModel(name='ToeicPractice',fields=[
            ('slug',models.SlugField(max_length=100,primary_key=True,serialize=False)),
            ('title',models.CharField(max_length=200)),('revision',models.PositiveIntegerField(default=1)),
            ('published',models.BooleanField(default=False)),('content',models.JSONField(default=dict)),
            ('updated_at',models.DateTimeField(auto_now=True)),
        ],options={'ordering':['title']}),
        migrations.AddField(model_name='toeicattempt',name='snapshot',field=models.JSONField(blank=True,default=dict)),
        migrations.CreateModel(name='ContentImport',fields=[
            ('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),
            ('kind',models.CharField(max_length=12)),('payload',models.JSONField(default=list)),
            ('expected',models.JSONField(default=dict)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('applied_at',models.DateTimeField(blank=True,null=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
    ]
