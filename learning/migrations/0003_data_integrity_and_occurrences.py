import hashlib
import unicodedata
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion


def occurrence_key(reading_id,source_label,context):
    def normalise(value):
        return ' '.join(unicodedata.normalize('NFKC',str(value or '')).split()).casefold()
    raw=f'{reading_id or ""}\x1f{normalise(source_label)}\x1f{normalise(context)}'
    return hashlib.sha256(raw.encode()).hexdigest()


def copy_existing_occurrences(apps,schema_editor):
    Vocabulary=apps.get_model('learning','Vocabulary')
    Occurrence=apps.get_model('learning','VocabularyOccurrence')
    rows=[]
    for vocab in Vocabulary.objects.exclude(reading_id=None).iterator():
        rows.append(Occurrence(owner_id=vocab.owner_id,vocabulary_id=vocab.id,reading_id=vocab.reading_id,
            source_label=vocab.source_label,context=vocab.context,
            fingerprint=occurrence_key(vocab.reading_id,vocab.source_label,vocab.context)))
        if len(rows)>=1000:
            Occurrence.objects.bulk_create(rows,ignore_conflicts=True);rows=[]
    if rows:Occurrence.objects.bulk_create(rows,ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies=[('learning','0002_reading_platform')]
    operations=[
        migrations.AddField(model_name='reading',name='import_key',field=models.UUIDField(blank=True,editable=False,null=True)),
        migrations.AddIndex(model_name='reading',index=models.Index(fields=['owner','updated_at'],name='reading_owner_updated')),
        migrations.AddConstraint(model_name='reading',constraint=models.UniqueConstraint(condition=models.Q(import_key__isnull=False),fields=('owner','import_key'),name='unique_owner_import_key')),
        migrations.AlterField(model_name='reviewlog',name='rating',field=models.CharField(choices=[('again','Again'),('hard','Hard'),('good','Good'),('easy','Easy')],max_length=8)),
        migrations.AddConstraint(model_name='reviewlog',constraint=models.CheckConstraint(condition=models.Q(rating__in=['again','hard','good','easy']),name='valid_review_rating')),
        migrations.AddIndex(model_name='reviewlog',index=models.Index(fields=['owner','created_at'],name='review_owner_created')),
        migrations.AddConstraint(model_name='vocabulary',constraint=models.CheckConstraint(condition=models.Q(interval_days__gte=0,interval_days__lte=365),name='valid_vocab_interval')),
        migrations.AddConstraint(model_name='vocabulary',constraint=models.CheckConstraint(condition=models.Q(ease__gte=1.3,ease__lte=3),name='valid_vocab_ease')),
        migrations.AddIndex(model_name='vocabulary',index=models.Index(fields=['owner','last_reviewed','interval_days'],name='vocab_owner_progress')),
        migrations.CreateModel(name='VocabularyOccurrence',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('source_label',models.CharField(blank=True,max_length=200)),('context',models.TextField(blank=True)),
            ('fingerprint',models.CharField(max_length=64)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
            ('reading',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='vocabulary_occurrences',to='learning.reading')),
            ('vocabulary',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='occurrences',to='learning.vocabulary')),
        ],options={'ordering':['created_at']}),
        migrations.AddConstraint(model_name='vocabularyoccurrence',constraint=models.UniqueConstraint(fields=('owner','vocabulary','fingerprint'),name='unique_vocab_occurrence')),
        migrations.AddIndex(model_name='vocabularyoccurrence',index=models.Index(fields=['owner','reading'],name='occurrence_owner_reading')),
        migrations.RunPython(copy_existing_occurrences,migrations.RunPython.noop),
    ]
