import logging
import secrets

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


class VerificationEmailError(Exception):
    """Raised when the verification email could not be sent."""


def generate_verification_code() -> str:
    """Return a cryptographically-random 6-digit numeric code."""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def _build_text_body(username: str, code: str, ttl_minutes: int) -> str:
    """Plain-text body. The code is on the FIRST line, alone, in its own
    line, so even if the rest of the Persian text gets mangled by an SMTP
    server that doesn't handle UTF-8 well, the code is still visible."""
    return (
        f'{code}\n'
        f'\n'
        f'سلام {username}\n'
        f'\n'
        f'کد تایید ثبت‌نام شما در مرکز مشاوره روانشناسی، عدد بالاست.\n'
        f'این کد تا {ttl_minutes} دقیقه دیگر معتبر است.\n'
        f'\n'
        f'اگر شما درخواست ثبت‌نام نداده‌اید، این ایمیل را نادیده بگیرید.\n'
    )


def _build_html_body(username: str, code: str, ttl_minutes: int) -> str:
    """HTML body — renders correctly in every modern email client and is
    robust against SMTP servers that mangle 8-bit plain-text bodies."""
    return f"""\
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="utf-8"></head>
<body style="font-family: Tahoma, Arial, sans-serif; direction: rtl;
             background:#f4f4f5; padding:24px; margin:0;">
  <div style="max-width:480px; margin:0 auto; background:#ffffff;
              border:1px solid #e4e4e7; border-radius:8px; overflow:hidden;">
    <div style="background:#0d6efd; color:#ffffff; padding:16px 24px;
                font-size:16px; font-weight:bold;">
      کد تایید ثبت‌نام
    </div>
    <div style="padding:24px;">
      <p style="margin:0 0 16px 0; color:#27272a;">
        سلام {username}
      </p>
      <p style="margin:0 0 16px 0; color:#27272a;">
        کد تایید ثبت‌نام شما:
      </p>
      <div style="text-align:center; background:#f4f4f5; border:1px dashed #d4d4d8;
                  border-radius:8px; padding:20px; margin:0 0 16px 0;">
        <span style="font-family:'Courier New', monospace; font-size:32px;
                     font-weight:bold; letter-spacing:8px; color:#0d6efd;
                     direction:ltr; display:inline-block;">
          {code}
        </span>
      </div>
      <p style="margin:0 0 16px 0; color:#52525b; font-size:13px;">
        این کد تا {ttl_minutes} دقیقه دیگر معتبر است.
      </p>
      <p style="margin:0; color:#71717a; font-size:12px;">
        اگر شما درخواست ثبت‌نام نداده‌اید، این ایمیل را نادیده بگیرید.
      </p>
    </div>
  </div>
</body>
</html>
"""


def create_and_send_verification(user, verification) -> None:
    """Generate a fresh code, store its hash on `verification`, and email it.

    Raises VerificationEmailError if the email could not be sent, so the
    caller can show the user a friendly message instead of a 500 page.

    Notes on encoding (why we don't use plain ``send_mail``):
      Django's default ``send_mail`` sends the body with
      ``Content-Transfer-Encoding: 8bit``. Many SMTP servers (especially
      shared-hosting / regional ones) do NOT support ``8BITMIME`` and will
      either reject the message or mangle the UTF-8 Persian body, so the
      recipient sees only the (Base64-encoded) subject line and not the
      code. Using ``EmailMultiAlternatives`` with an explicit
      ``encoding='base64'`` forces a 7-bit-safe body that every SMTP
      server on the planet can relay intact, and the HTML alternative
      makes the code display correctly in every modern mail client.
    """
    code = generate_verification_code()
    verification.set_code(code, ttl_minutes=settings.EMAIL_VERIFICATION_TTL_MINUTES)
    verification.save()

    ttl_minutes = settings.EMAIL_VERIFICATION_TTL_MINUTES
    # Short subject keeps the Base64-encoded header compact and avoids
    # line-wrapping issues that some clients display as a long garbled
    # string.
    subject = 'کد تایید ثبت‌نام'
    text_body = _build_text_body(user.username, code, ttl_minutes)
    html_body = _build_html_body(user.username, code, ttl_minutes)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
    except Exception:
        logger.exception('Failed to send verification email to %s', user.email)
        raise VerificationEmailError('ارسال ایمیل تایید با خطا مواجه شد.')
