"""Pluggable SMS backends for the phone-verification flow.

Mirrors Django's own EMAIL_BACKEND pattern: ``settings.SMS_BACKEND`` holds
the dotted path to the class that should be instantiated to send a text
message. Swap providers in production by changing that one setting —
nothing in accounts/views.py or accounts/utils.py needs to change.
"""
import logging

from django.conf import settings
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


class BaseSMSBackend:
    """Subclass this and implement `send()` to plug in a real SMS gateway."""

    def send(self, phone_number: str, message: str) -> None:
        raise NotImplementedError


class ConsoleSMSBackend(BaseSMSBackend):
    """Prints the SMS to the console/log instead of actually sending it.

    This is the default while DEBUG=True, so local development needs no
    SMS-provider account — exactly like Django's own console email backend.
    The code is easy to spot in the runserver output.
    """

    def send(self, phone_number: str, message: str) -> None:
        banner = '=' * 50
        print(f'\n{banner}\nSMS to {phone_number}:\n{message}\n{banner}\n')
        logger.info('Console SMS backend: "sent" a message to %s', phone_number)


class PlaceholderSMSBackend(BaseSMSBackend):
    """Stand-in for a real provider (e.g. Kavenegar, MeliPayamak, sms.ir).

    This is intentionally left unimplemented so that, if it's ever selected
    in production without being filled in, it fails loudly (raises) instead
    of silently pretending a code was texted to the user.

    Two ready-to-use backends are implemented below: KavenegarSMSBackend and
    SmsIrSMSBackend. Point SMS_BACKEND at one of those in your .env instead
    of writing a new one, unless you're using a different provider.
    """

    def send(self, phone_number: str, message: str) -> None:
        raise NotImplementedError(
            'PlaceholderSMSBackend پیاده‌سازی نشده است. یک درگاه پیامکی واقعی '
            '(مثل کاوه‌نگار، ملی‌پیامک یا sms.ir) را در accounts/sms_backends.py '
            'پیاده‌سازی کرده و تنظیمات SMS_BACKEND / SMS_API_KEY / SMS_API_URL / '
            'SMS_SENDER_NUMBER را در فایل .env تکمیل کنید.'
        )


class KavenegarSMSBackend(BaseSMSBackend):
    """Sends SMS via Kavenegar's REST API (https://kavenegar.com).

    Settings used:
      - SMS_API_KEY: your Kavenegar "API-Key" (Panel > تنظیمات > API Key).
      - SMS_SENDER_NUMBER: optional. One of your purchased/assigned line
        numbers (Panel > خطوط من). Leave empty in .env to let Kavenegar pick
        its own default line for you (fine for testing; get a real line for
        production so messages aren't filtered as generic/shared traffic).
    """

    def send(self, phone_number: str, message: str) -> None:
        import requests

        api_key = settings.SMS_API_KEY
        if not api_key:
            raise RuntimeError('SMS_API_KEY در .env تنظیم نشده است.')

        url = "https://api.kavenegar.com/v1/" + api_key + "/sms/send.json"
        params = {'receptor': phone_number, 'message': message}
        if settings.SMS_SENDER_NUMBER:
            params['sender'] = settings.SMS_SENDER_NUMBER

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        status = (data.get('return') or {}).get('status')
        if status != 200:
            status_message = (data.get('return') or {}).get('message', 'خطای نامشخص')
            raise RuntimeError(f'Kavenegar error {status}: {status_message}')


class SmsIrSMSBackend(BaseSMSBackend):
    """Sends SMS via sms.ir's REST API v1 (https://sms.ir).

    Settings used:
      - SMS_API_KEY: the "API Key" from your sms.ir panel (Panel > وب سرویس).
      - SMS_SENDER_NUMBER: one of your panel's line numbers (Panel > خطوط
        من). Unlike Kavenegar, sms.ir *requires* a line number on every
        request — there's no default shared line.
    """

    def send(self, phone_number: str, message: str) -> None:
        import requests

        api_key = settings.SMS_API_KEY
        line_number = settings.SMS_SENDER_NUMBER
        if not api_key or not line_number:
            raise RuntimeError('SMS_API_KEY یا SMS_SENDER_NUMBER در .env تنظیم نشده است.')

        url = 'https://api.sms.ir/v1/send/bulk'
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload = {
            'lineNumber': line_number,
            'messageText': message,
            'mobiles': [phone_number],
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('status') != 1:
            raise RuntimeError(f"sms.ir error: {data.get('message', 'خطای نامشخص')}")


def get_sms_backend() -> BaseSMSBackend:
    """Instantiate the SMS backend configured in settings.SMS_BACKEND."""
    backend_path = getattr(settings, 'SMS_BACKEND', 'accounts.sms_backends.ConsoleSMSBackend')
    backend_class = import_string(backend_path)
    return backend_class()
