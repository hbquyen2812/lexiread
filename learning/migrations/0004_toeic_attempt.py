import uuid
from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('learning','0003_data_integrity_and_occurrences')]
    operations=[
        migrations.CreateModel(name='ToeicAttempt',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('set_slug',models.SlugField(max_length=100)),('token',models.UUIDField(default=uuid.uuid4)),
            ('answers',models.JSONField(default=dict)),('result',models.JSONField(default=dict)),
            ('duration_seconds',models.PositiveIntegerField(default=0)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-created_at']}),
        migrations.AddConstraint(model_name='toeicattempt',constraint=models.UniqueConstraint(fields=('owner','token'),name='unique_toeic_attempt_token')),
        migrations.AddIndex(model_name='toeicattempt',index=models.Index(fields=['owner','set_slug','created_at'],name='toeic_owner_set_date')),
    ]
