from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontent',
            name='about_tool1_title',
            field=models.CharField(max_length=150, blank=True, default='آزمون PHQ-9:', verbose_name='عنوان ابزار ۱'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_tool1_desc',
            field=models.TextField(blank=True, default='پرسشنامه افسردگی بیمار - یک ابزار استاندارد بین\u200cالمللی برای غربالگری افسردگی', verbose_name='توضیح ابزار ۱'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_tool2_title',
            field=models.CharField(max_length=150, blank=True, default='آزمون GAD-7:', verbose_name='عنوان ابزار ۲'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_tool2_desc',
            field=models.TextField(blank=True, default='پرسشنامه اضطراب عمومی - یک ابزار استاندارد بین\u200cالمللی برای غربالگری اضطراب', verbose_name='توضیح ابزار ۲'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_tools_note',
            field=models.TextField(blank=True, default='هر دو پرسشنامه توسط متخصصان بهداشت روان طراحی شده و در سراسر جهان مورد استفاده قرار می\u200cگیرند.', verbose_name='متن پایانی بخش ابزارها'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_warning_title',
            field=models.CharField(max_length=100, blank=True, default='توجه مهم:', verbose_name='عنوان بخش توجه مهم'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='about_warning_text',
            field=models.TextField(blank=True, default='نتایج آزمون\u200cهای ما جنبه غربالگری دارند و جایگزین تشخیص تخصصی پزشک نیستند. در صورت نیاز، حتماً با یک متخصص بهداشت روان مشورت کنید.', verbose_name='متن بخش توجه مهم'),
        ),
    ]
