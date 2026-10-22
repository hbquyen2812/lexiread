from django.db import migrations,models

class Migration(migrations.Migration):
    dependencies=[('learning','0004_toeic_attempt')]
    operations=[
        migrations.AddConstraint(model_name='toeicattempt',constraint=models.CheckConstraint(
            condition=models.Q(duration_seconds__lte=7200),name='valid_toeic_duration')),
    ]
