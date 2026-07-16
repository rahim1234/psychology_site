from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BDIResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('severity', models.CharField(
                    choices=[
                        ('Minimal', 'حداقل افسردگی'),
                        ('Mild', 'افسردگی خفیف'),
                        ('Moderate', 'افسردگی متوسط'),
                        ('Severe', 'افسردگی شدید'),
                    ],
                    max_length=20,
                    verbose_name='شدت'
                )),
                ('answers', models.JSONField(verbose_name='پاسخ‌ها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bdi_results',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'نتیجه BDI-II',
                'verbose_name_plural': 'نتایج BDI-II',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BAIResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('severity', models.CharField(
                    choices=[
                        ('Minimal', 'حداقل اضطراب'),
                        ('Mild', 'اضطراب خفیف'),
                        ('Moderate', 'اضطراب متوسط'),
                        ('Severe', 'اضطراب شدید'),
                    ],
                    max_length=20,
                    verbose_name='شدت'
                )),
                ('answers', models.JSONField(verbose_name='پاسخ‌ها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bai_results',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'نتیجه BAI',
                'verbose_name_plural': 'نتایج BAI',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MCMI4Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز خام')),
                ('answers', models.JSONField(verbose_name='پاسخ‌ها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mcmi4_results',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'نتیجه MCMI-4',
                'verbose_name_plural': 'نتایج MCMI-4',
                'ordering': ['-created_at'],
            },
        ),
    ]