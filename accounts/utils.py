import logging
import re
import secrets

from django.conf import settings

from .sms_backends import get_sms_backend

logger = logging.getLogger(__name__)

# Persian and Arabic-Indic digits, so users can paste a number typed on a
# Persian/Arabic keyboard and still have it validate correctly.
_DIGIT_TRANSLATION = str.maketrans(
    '۰۱۲۳۴۵۶۷۸۹' '٠١٢٣٤٥٦٧٨٩',
    '01234567890123456789',
)


class SMSSendError(Exception):
    """Raised when the verification SMS could not be sent."""


def normalize_iranian_mobile(raw: str) -> str:
    """Normalize a user-entered Iranian mobile number to the '09XXXXXXXXX' form.

    Converts Persian/Arabic-Indic digits to ASCII, strips spaces/dashes, and
    rewrites the +98 / 0098 / 98 country-code prefixes people commonly paste
    in. If the input doesn't match a recognizable pattern it's returned
    translated-but-otherwise-unchanged, so the caller's own validator still
    produces the right error message instead of this function guessing.
    """
    value = raw.translate(_DIGIT_TRANSLATION)
    value = re.sub(r'[\s\-()]', '', value)
    if value.startswith('+98'):
        value = '0' + value[3:]
    elif value.startswith('0098'):
        value = '0' + value[4:]
    elif value.startswith('98') and len(value) == 12:
        value = '0' + value[2:]
    return value


def ratelimit_key_phone_number(group, request):
    """django-ratelimit key function: rate-limit by the *normalized* phone number.

    The built-in ``key='post:phone_number'`` shortcut keys on the raw,
    un-normalized POST value. That means the same phone number submitted in
    different but equivalent forms (e.g. ``+98912...``, ``0098912...``, with
    spaces/dashes, or Persian/Arabic-Indic digits) each get their own
    independent rate-limit bucket -- letting an attacker bypass the
    per-phone-number limit entirely while still hitting the same real
    account. Normalizing here closes that loophole so every equivalent
    representation of one phone number shares a single bucket.
    """
    raw = request.POST.get('phone_number', '')
    return normalize_iranian_mobile(raw.strip())


def generate_verification_code() -> str:
    """Return a cryptographically-random 6-digit numeric code."""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def _build_sms_body(code: str, ttl_minutes: int, purpose: str = 'signup') -> str:
    intro = 'کد بازیابی رمز عبور شما' if purpose == 'password_reset' else 'کد تایید ثبت‌نام شما'
    return (
        f'مرکز مشاوره روانشناسی\n'
        f'{intro}: {code}\n'
        f'اعتبار: {ttl_minutes} دقیقه\n'
        f'اگر این درخواست را شما نداده‌اید، این پیامک را نادیده بگیرید.'
    )


def create_and_send_verification(user, verification, purpose: str = 'signup') -> None:
    """Generate a fresh code, store its hash on `verification`, and text it.

    `purpose` only changes the wording of the SMS ('signup' or
    'password_reset'); the code/hash/expiry mechanics are identical either
    way. Raises SMSSendError if the SMS could not be sent, so the caller can
    show the user a friendly message instead of a 500 page.
    """
    code = generate_verification_code()
    verification.set_code(code, ttl_minutes=settings.PHONE_VERIFICATION_TTL_MINUTES)
    verification.save()

    ttl_minutes = settings.PHONE_VERIFICATION_TTL_MINUTES
    message = _build_sms_body(code, ttl_minutes, purpose=purpose)

    try:
        backend = get_sms_backend()
        backend.send(user.phone_number, message)
    except Exception:
        logger.exception('Failed to send verification SMS to %s', user.phone_number)
        raise SMSSendError('ارسال پیامک تایید با خطا مواجه شد.')
