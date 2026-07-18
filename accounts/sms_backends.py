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

    To wire up a real provider, replace the body of `send()` with an HTTP
    call to that provider's API, something like:

        import requests

        def send(self, phone_number, message):
            response = requests.post(
                settings.SMS_API_URL,
                json={
                    'apikey': settings.SMS_API_KEY,
                    'sender': settings.SMS_SENDER_NUMBER,
                    'receptor': phone_number,
                    'message': message,
                },
                timeout=10,
            )
            response.raise_for_status()

    Then point SMS_BACKEND at this class in your production .env/settings.
    """

    def send(self, phone_number: str, message: str) -> None:
        raise NotImplementedError(
            'PlaceholderSMSBackend پیاده‌سازی نشده است. یک درگاه پیامکی واقعی '
            '(مثل کاوه‌نگار، ملی‌پیامک یا sms.ir) را در accounts/sms_backends.py '
            'پیاده‌سازی کرده و تنظیمات SMS_BACKEND / SMS_API_KEY / SMS_API_URL / '
            'SMS_SENDER_NUMBER را در فایل .env تکمیل کنید.'
        )


def get_sms_backend() -> BaseSMSBackend:
    """Instantiate the SMS backend configured in settings.SMS_BACKEND."""
    backend_path = getattr(settings, 'SMS_BACKEND', 'accounts.sms_backends.ConsoleSMSBackend')
    backend_class = import_string(backend_path)
    return backend_class()
