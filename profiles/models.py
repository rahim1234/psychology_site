from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

from .storage import get_private_storage
from .validators import MaxFileSizeValidator


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
        ('O', 'دیگر'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, verbose_name='نام کامل')
    age = models.PositiveIntegerField(
        verbose_name='سن',
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='جنسیت')
    problem_description = models.TextField(blank=True, verbose_name='توضیح مشکل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل‌ها'

    def __str__(self):
        return f'{self.full_name} - {self.user.email}'


class SessionNote(models.Model):
    """Therapist-only notes/summary for a client's session.

    These are only ever exposed through the Django admin (therapist area) —
    no user-facing view or template reads from this model, so clients never
    see this content. The "secretary" role (see admin.py) is deliberately
    never granted any permission on this model, so it never appears for them.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='session_notes')
    session_date = models.DateField(verbose_name='تاریخ جلسه')
    content = models.TextField(verbose_name='یادداشت / خلاصه جلسه')
    image = models.ImageField(
        storage=get_private_storage,
        upload_to='session_notes/images/%Y/%m/',
        blank=True,
        null=True,
        validators=[MaxFileSizeValidator(10)],
        verbose_name='تصویر پیوست',
        help_text='حداکثر حجم: ۱۰ مگابایت',
    )
    audio = models.FileField(
        storage=get_private_storage,
        upload_to='session_notes/audio/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a', 'aac']),
            MaxFileSizeValidator(20),
        ],
        verbose_name='فایل صوتی پیوست',
        help_text='فرمت‌های مجاز: mp3, wav, ogg, m4a, aac — حداکثر حجم: ۲۰ مگابایت',
    )
    video = models.FileField(
        storage=get_private_storage,
        upload_to='session_notes/video/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm', 'avi']),
            MaxFileSizeValidator(100),
        ],
        verbose_name='فایل تصویری (ویدیو) پیوست',
        help_text='فرمت‌های مجاز: mp4, mov, webm, avi — حداکثر حجم: ۱۰۰ مگابایت',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='ثبت شده توسط',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'یادداشت جلسه'
        verbose_name_plural = 'یادداشت‌های جلسات'
        ordering = ['-session_date', '-created_at']

    def __str__(self):
        return f'یادداشت {self.profile.full_name} - {self.session_date}'


class ProfileAttachment(models.Model):
    """A file uploaded onto a client's profile by the secretary (or therapist).

    Deliberately a separate model from SessionNote: the secretary role is
    granted permission on this model only, never on SessionNote, so they
    can upload files here without ever being able to see the therapist's
    session notes.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        storage=get_private_storage,
        upload_to='profile_attachments/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=[
                'jpg', 'jpeg', 'png', 'gif', 'webp',
                'mp3', 'wav', 'ogg', 'm4a', 'aac',
                'mp4', 'mov', 'webm', 'avi',
                'pdf', 'doc', 'docx',
            ]),
            MaxFileSizeValidator(50),
        ],
        verbose_name='فایل',
        help_text='عکس، صدا، ویدیو یا سند — حداکثر حجم: ۵۰ مگابایت',
    )
    description = models.CharField(max_length=255, blank=True, verbose_name='توضیح فایل')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='آپلود شده توسط',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        verbose_name = 'فایل پیوست پروفایل'
        verbose_name_plural = 'فایل‌های پیوست پروفایل'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'فایل پیوست {self.profile.full_name} - {self.uploaded_at:%Y-%m-%d}'
