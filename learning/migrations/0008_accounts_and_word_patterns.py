import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('learning','0007_editorial_workflow')]
    operations = [
        migrations.AddField(model_name='vocabulary',name='usage_pattern',
            field=models.CharField(blank=True,max_length=300)),
        migrations.CreateModel(name='AuthRateLimit',fields=[
            ('key',models.CharField(max_length=64,primary_key=True,serialize=False)),
            ('started_at',models.DateTimeField(default=django.utils.timezone.now)),
            ('last_at',models.DateTimeField(default=django.utils.timezone.now)),
            ('count',models.PositiveIntegerField(default=0)),
        ]),
    ]
