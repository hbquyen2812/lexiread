from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies=[('learning','0005_toeic_duration_constraint')]
    operations=[
        migrations.CreateModel(name='DailyVisit',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('date',models.DateField(default=django.utils.timezone.localdate)),
            ('visitor_key',models.CharField(max_length=64)),('views',models.PositiveIntegerField(default=1)),
            ('page_counts',models.JSONField(blank=True,default=dict)),('first_seen',models.DateTimeField(auto_now_add=True)),
            ('last_seen',models.DateTimeField(auto_now=True)),
            ('owner',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-date','-last_seen']}),
        migrations.AddConstraint(model_name='dailyvisit',constraint=models.UniqueConstraint(fields=('date','visitor_key'),name='unique_daily_visitor')),
        migrations.AddIndex(model_name='dailyvisit',index=models.Index(fields=['date'],name='visit_date')),
        migrations.AddIndex(model_name='dailyvisit',index=models.Index(fields=['owner','date'],name='visit_owner_date')),
    ]
