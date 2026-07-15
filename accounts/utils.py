import logging
import secrets

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class VerificationEmailError(Exception):
    """Raised when the verification email could not be sent."""


def generate_verification_code() -> str:
    """Return a cryptographically-random 6-digit numeric code."""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def create_and_send_verification(user, verification) -> None:
    """Generate a fresh code, store its hash on `verification`, and email it.

    Raises VerificationEmailError if the email could not be sent, so the
    caller can show the user a friendly message instead of a 500 page.
    """
    code = generate_verification_code()
    verification.set_code(code, ttl_minutes=settings.EMAIL_VERIFICATION_TTL_MINUTES)
    verification.save()

    subject = 'کد تایید ثبت نام - مرکز مشاوره روانشناسی'
    message = (
        f'سلام {user.username},\n\n'
        f'کد تایید ثبت نام شما: {code}\n\n'
        f'این کد تا {settings.EMAIL_VERIFICATION_TTL_MINUTES} دقیقه دیگر معتبر است.\n'
        'اگر شما درخواست ثبت نام نداده‌اید، این ایمیل را نادیده بگیرید.'
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception('Failed to send verification email to %s', user.email)
        raise VerificationEmailError('ارسال ایمیل تایید با خطا مواجه شد.')
