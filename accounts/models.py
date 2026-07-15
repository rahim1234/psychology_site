from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class EmailVerification(models.Model):
    """Stores the (hashed) one-time code used to verify a user's email at signup."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification',
    )
    code_hash = models.CharField(max_length=128)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'تایید ایمیل'
        verbose_name_plural = 'تاییدهای ایمیل'

    def set_code(self, raw_code: str, ttl_minutes: int) -> None:
        self.code_hash = make_password(raw_code)
        self.attempts = 0
        self.last_sent_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)

    def check_code(self, raw_code: str) -> bool:
        return check_password(raw_code, self.code_hash)

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def seconds_until_can_resend(self, cooldown_seconds: int) -> int:
        elapsed = (timezone.now() - self.last_sent_at).total_seconds()
        remaining = cooldown_seconds - elapsed
        return max(0, int(remaining))

    def __str__(self):
        return f'کد تایید {self.user.email}'
