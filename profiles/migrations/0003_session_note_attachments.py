import django.core.validators
import profiles.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_session_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionnote',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='session_notes/images/%Y/%m/',
                validators=[profiles.validators.MaxFileSizeValidator(10)],
                verbose_name='تصویر پیوست',
            ),
        ),
        migrations.AddField(
            model_name='sessionnote',
            name='audio',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='session_notes/audio/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a', 'aac']),
                    profiles.validators.MaxFileSizeValidator(20),
                ],
                verbose_name='فایل صوتی پیوست',
            ),
        ),
        migrations.AddField(
            model_name='sessionnote',
            name='video',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='session_notes/video/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm', 'avi']),
                    profiles.validators.MaxFileSizeValidator(100),
                ],
                verbose_name='فایل تصویری (ویدیو) پیوست',
            ),
        ),
    ]
