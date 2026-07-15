from datetime import date

from django import forms

from .jalali import JALALI_MONTHS, gregorian_to_jalali, jalali_to_gregorian


class JalaliDateWidget(forms.MultiWidget):
    """Three plain HTML inputs (year / month / day) — no JS date-picker, no
    external CSS/JS, so it can never fail to load due to network issues."""

    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={
                'placeholder': 'سال (مثلاً ۱۴۰۵)', 'class': 'form-control jalali-year',
                'style': 'width:110px;display:inline-block;', 'min': 1300, 'max': 1500,
            }),
            forms.Select(choices=JALALI_MONTHS, attrs={
                'class': 'form-control jalali-month', 'style': 'width:130px;display:inline-block;',
            }),
            forms.NumberInput(attrs={
                'placeholder': 'روز', 'class': 'form-control jalali-day',
                'style': 'width:80px;display:inline-block;', 'min': 1, 'max': 31,
            }),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
            return [jy, jm, jd]
        return [None, None, None]


class JalaliDateFormField(forms.MultiValueField):
    widget = JalaliDateWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(min_value=1300, max_value=1500),
            forms.ChoiceField(choices=JALALI_MONTHS),
            forms.IntegerField(min_value=1, max_value=31),
        )
        kwargs.setdefault('require_all_fields', True)
        super().__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list or any(v in (None, '') for v in data_list):
            return None
        jy, jm, jd = int(data_list[0]), int(data_list[1]), int(data_list[2])
        try:
            gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
            return date(gy, gm, gd)
        except (ValueError, OverflowError):
            raise forms.ValidationError('تاریخ شمسی واردشده معتبر نیست.')
