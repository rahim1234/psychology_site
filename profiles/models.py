from django.db import models
from django.conf import settings


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
        ('O', 'دیگر'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, verbose_name='نام کامل')
    age = models.PositiveIntegerField(verbose_name='سن')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='جنسیت')
    problem_description = models.TextField(blank=True, verbose_name='توضیح مشکل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل‌ها'

    def __str__(self):
        return f'{self.full_name} - {self.user.email}'
