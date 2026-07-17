from django import forms
from django.core.exceptions import ValidationError


class HoneypotField(forms.CharField):
    """
    فیلد مخفی برای تشخیص ربات‌ها.
    کاربر واقعی این فیلد را نمی‌بیند و پر نمی‌کند.
    اگر پر شود → ربات است → فرم رد می‌شود.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('label', '')
        kwargs.setdefault('widget', forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
            'style': (
                'position: absolute !important; '
                'left: 0 !important; '
                'top: 0 !important; '
                'width: 1px !important; '
                'height: 1px !important; '
                'overflow: hidden !important; '
                'clip: rect(0, 0, 0, 0) !important; '
                'clip-path: inset(50%) !important; '
                'white-space: nowrap !important; '
                'border: 0 !important; '
                'margin: -1px !important; '
                'padding: 0 !important;'
            ),
        }))
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """اگر ربات این فیلد را پر کرده باشد، ValidationError برگردان."""
        if value:
            import logging
            logger = logging.getLogger('honeypot')
            logger.warning(f"Honeypot triggered! Bot detected. Value: {value[:50]}")
            raise ValidationError("لطفاً فیلدهای اضافی را پر نکنید.")
        return value