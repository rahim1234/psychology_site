import django.core.validators
import django.db.models.deletion
import profiles.storage
import profiles.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0003_session_note_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionnote',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                storage=profiles.storage.get_private_storage,
                upload_to='session_notes/images/%Y/%m/',
                validators=[profiles.validators.MaxFileSizeValidator(10)],
                verbose_name='تصویر پیوست',
            ),
        ),
        migrations.AlterField(
            model_name='sessionnote',
            name='audio',
            field=models.FileField(
                blank=True,
                null=True,
                storage=profiles.storage.get_private_storage,
                upload_to='session_notes/audio/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a', 'aac']),
                    profiles.validators.MaxFileSizeValidator(20),
                ],
                verbose_name='فایل صوتی پیوست',
            ),
        ),
        migrations.AlterField(
            model_name='sessionnote',
            name='video',
            field=models.FileField(
                blank=True,
                null=True,
                storage=profiles.storage.get_private_storage,
                upload_to='session_notes/video/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm', 'avi']),
                    profiles.validators.MaxFileSizeValidator(100),
                ],
                verbose_name='فایل تصویری (ویدیو) پیوست',
            ),
        ),
        migrations.CreateModel(
            name='ProfileAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(
                    storage=profiles.storage.get_private_storage,
                    upload_to='profile_attachments/%Y/%m/',
                    validators=[
                        django.core.validators.FileExtensionValidator(allowed_extensions=[
                            'jpg', 'jpeg', 'png', 'gif', 'webp',
                            'mp3', 'wav', 'ogg', 'm4a', 'aac',
                            'mp4', 'mov', 'webm', 'avi',
                            'pdf', 'doc', 'docx',
                        ]),
                        profiles.validators.MaxFileSizeValidator(50),
                    ],
                    verbose_name='فایل',
                )),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='توضیح فایل')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='profiles.profile')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='آپلود شده توسط')),
            ],
            options={
                'verbose_name': 'فایل پیوست پروفایل',
                'verbose_name_plural': 'فایل‌های پیوست پروفایل',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
