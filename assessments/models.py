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
        return f'{self.user.email} - PHQ-9: {self.score} ({self.get_severity_display()})'


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
        return f'{self.user.email} - GAD-7: {self.score} ({self.get_severity_display()})'
