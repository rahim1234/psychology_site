from django.db import models
from django.conf import settings


class PHQ9Result(models.Model):
    SEVERITY_CHOICES = [
        ('Normal', 'طبیعی'),
        ('Mild', 'خفیف'),
        ('Moderate', 'متوسط'),
        ('Moderately Severe', 'نسبتاً شدید'),
        ('Severe', 'شدید'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='phq9_results')
    score = models.PositiveIntegerField(verbose_name='امتیاز')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='شدت')
    answers = models.JSONField(verbose_name='پاسخ‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نتیجه PHQ-9'
        verbose_name_plural = 'نتایج PHQ-9'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - PHQ-9: {self.score} ({self.get_severity_display()})'


class GAD7Result(models.Model):
    SEVERITY_CHOICES = [
        ('Normal', 'طبیعی'),
        ('Mild', 'خفیف'),
        ('Moderate', 'متوسط'),
        ('Severe', 'شدید'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gad7_results')
    score = models.PositiveIntegerField(verbose_name='امتیاز')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='شدت')
    answers = models.JSONField(verbose_name='پاسخ‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نتیجه GAD-7'
        verbose_name_plural = 'نتایج GAD-7'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - GAD-7: {self.score} ({self.get_severity_display()})'


class BDIResult(models.Model):
    """نتیجه آزمون افسردگی Beck (BDI-II)"""
    SEVERITY_CHOICES = [
        ('Minimal', 'حداقل افسردگی'),
        ('Mild', 'افسردگی خفیف'),
        ('Moderate', 'افسردگی متوسط'),
        ('Severe', 'افسردگی شدید'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bdi_results')
    score = models.PositiveIntegerField(verbose_name='امتیاز')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='شدت')
    answers = models.JSONField(verbose_name='پاسخ‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نتیجه BDI-II'
        verbose_name_plural = 'نتایج BDI-II'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - BDI: {self.score} ({self.get_severity_display()})'


class BAIResult(models.Model):
    """نتیجه آزمون اضطراب Beck (BAI)"""
    SEVERITY_CHOICES = [
        ('Minimal', 'حداقل اضطراب'),
        ('Mild', 'اضطراب خفیف'),
        ('Moderate', 'اضطراب متوسط'),
        ('Severe', 'اضطراب شدید'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bai_results')
    score = models.PositiveIntegerField(verbose_name='امتیاز')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='شدت')
    answers = models.JSONField(verbose_name='پاسخ‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نتیجه BAI'
        verbose_name_plural = 'نتایج BAI'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - BAI: {self.score} ({self.get_severity_display()})'


class MCMI4Result(models.Model):
    """نتیجه آزمون MCMI-4 (فقط برای نمایش - نیاز به تفسیر متخصص)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mcmi4_results')
    score = models.PositiveIntegerField(verbose_name='امتیاز خام')
    answers = models.JSONField(verbose_name='پاسخ‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نتیجه MCMI-4'
        verbose_name_plural = 'نتایج MCMI-4'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone_number} - MCMI-4: {self.score}'