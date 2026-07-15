import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(120)],
                verbose_name='سن',
            ),
        ),
        migrations.CreateModel(
            name='SessionNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField(verbose_name='تاریخ جلسه')),
                ('content', models.TextField(verbose_name='یادداشت / خلاصه جلسه')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ به\u200cروزرسانی')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='ثبت شده توسط')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_notes', to='profiles.profile')),
            ],
            options={
                'verbose_name': 'یادداشت جلسه',
                'verbose_name_plural': 'یادداشت\u200cهای جلسات',
                'ordering': ['-session_date', '-created_at'],
            },
        ),
    ]
