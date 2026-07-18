from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

phone_number_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود (مثال: ۰۹۱۲۳۴۵۶۷۸۹).',
)


class User(AbstractUser):
    phone_number = models.CharField(
        'شماره موبایل',
        max_length=11,
        unique=True,
        validators=[phone_number_validator],
    )
    # Email is now optional — phone number + SMS is the primary channel for
    # signup/verification/login. Left blank/null so multiple users can
    # leave it empty without violating a uniqueness constraint.
    email = models.EmailField('آدرس ایمیل', blank=True, null=True)

    # createsuperuser prompts for USERNAME_FIELD ('username') plus whatever
    # is listed here. phone_number is required+unique, so it must be asked
    # for explicitly — otherwise every superuser gets phone_number='' and
    # the second one collides with the first on the unique constraint.
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class PhoneVerification(models.Model):
    """Stores the (hashed) one-time code used to verify a user's phone number at signup."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_verification',
    )
    code_hash = models.CharField(max_length=128)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'تایید شماره موبایل'
        verbose_name_plural = 'تاییدهای شماره موبایل'

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
        return f'کد تایید {self.user.phone_number}'
