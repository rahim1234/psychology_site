import accounts.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_email_verification'),
    ]

    operations = [
        # --- Rename the verification model to reflect the new SMS flow ----
        migrations.RenameModel(
            old_name='EmailVerification',
            new_name='PhoneVerification',
        ),
        migrations.AlterModelOptions(
            name='phoneverification',
            options={'verbose_name': 'تایید شماره موبایل', 'verbose_name_plural': 'تاییدهای شماره موبایل'},
        ),
        migrations.AlterField(
            model_name='phoneverification',
            name='user',
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                related_name='phone_verification',
                to='accounts.user',
            ),
        ),

        # --- Phone number becomes the required identity field -------------
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(
                default='',
                max_length=11,
                unique=True,
                validators=[accounts.models.phone_number_validator],
                verbose_name='شماره موبایل',
            ),
            preserve_default=False,
        ),

        # --- Email becomes optional -----------------------------------------
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='آدرس ایمیل'),
        ),
    ]
