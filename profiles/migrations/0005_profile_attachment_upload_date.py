"""Add a manual `upload_date` DateField to ProfileAttachment.

The secretary uploads files along with a date (e.g. the date of the session
or the date the document belongs to). Previously the model only had an
auto-set `uploaded_at` timestamp; this migration adds a date the secretary
can specify explicitly when uploading. For existing rows we default to
today's date so the migration is reversible and never fails on existing data.
"""

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_profile_attachment_private_storage'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileattachment',
            name='upload_date',
            field=models.DateField(
                default=django.utils.timezone.localdate,
                help_text='تاریخی که این فایل به آن تعلق دارد (مثلاً تاریخ جلسه یا تاریخ سند) — به شمسی وارد شود.',
                verbose_name='تاریخ فایل',
            ),
        ),
        migrations.AlterModelOptions(
            name='profileattachment',
            options={
                'ordering': ['-upload_date', '-uploaded_at'],
                'verbose_name': 'فایل پیوست پروفایل',
                'verbose_name_plural': 'فایل\u200cهای پیوست پروفایل',
            },
        ),
    ]
