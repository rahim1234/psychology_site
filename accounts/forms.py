import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.password_validation import password_validators_help_text_html
from captcha.fields import CaptchaField
from core.honeypot import HoneypotField
from .utils import normalize_iranian_mobile

User = get_user_model()

PHONE_NUMBER_RE = re.compile(r'^09\d{9}$')


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '۰۹xxxxxxxxx',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
        })
    )
    email = forms.EmailField(
        label='ایمیل (اختیاری)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید (اختیاری)'})
    )
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری خود را وارد کنید'})
    )
    password1 = forms.CharField(
        label='رمز عبور',
        help_text=password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تکرار رمز عبور'})
    )
    captcha = CaptchaField(
        label='کد امنیتی',
        error_messages={'invalid': 'کد امنیتی وارد شده صحیح نیست.'}
    )

    # ✅ Honeypot field - باید خالی بماند
    website_url = HoneypotField()

    class Meta:
        model = User
        fields = ('phone_number', 'email', 'username', 'password1', 'password2', 'captcha')

    def clean_phone_number(self):
        phone_number = normalize_iranian_mobile(self.cleaned_data['phone_number'].strip())
        if not PHONE_NUMBER_RE.match(phone_number):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود (مثال: ۰۹۱۲۳۴۵۶۷۸۹).')
        existing = User.objects.filter(phone_number=phone_number).first()
        if existing and existing.is_active:
            raise forms.ValidationError('این شماره موبایل قبلاً ثبت نام شده است.')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            return email
        existing = User.objects.filter(email__iexact=email).first()
        if existing and existing.is_active:
            raise forms.ValidationError('این ایمیل قبلاً توسط حساب دیگری ثبت شده است.')
        return email

    def save(self, commit=True):
        # Remove any stale, never-verified account tied to this phone number
        # so the person can re-register (e.g. they lost their verification code).
        User.objects.filter(phone_number=self.cleaned_data['phone_number'], is_active=False).delete()
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']
        user.email = self.cleaned_data.get('email') or None
        user.is_active = False
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره موبایل خود را وارد کنید',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )

    # ✅ Honeypot برای Login
    company_name = HoneypotField()

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': (
            'شماره موبایل یا رمز عبور اشتباه است، یا حساب شما هنوز تایید نشده است. '
            'اگر تازه ثبت نام کرده‌اید، پیامک حاوی کد تایید را بررسی کنید.'
        ),
    }

    def clean_username(self):
        return normalize_iranian_mobile(self.cleaned_data['username'].strip())


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        label='کد تایید',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '------',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
        })
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if not code.isdigit():
            raise forms.ValidationError('کد تایید باید فقط شامل عدد باشد.')
        return code


class PhoneNumberForm(forms.Form):
    """Step 1 of the forgot-password flow: identify the account by phone."""
    phone_number = forms.CharField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '۰۹xxxxxxxxx',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
        })
    )
    captcha = CaptchaField(
        label='کد امنیتی',
        error_messages={'invalid': 'کد امنیتی وارد شده صحیح نیست.'}
    )

    def clean_phone_number(self):
        return normalize_iranian_mobile(self.cleaned_data['phone_number'].strip())


class StyledPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm (logged-in user, from the dashboard) with matching widgets."""
    old_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'})
    )
    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        help_text=password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )


class StyledSetPasswordForm(SetPasswordForm):
    """SetPasswordForm (forgot-password flow, after the SMS code is verified)."""
    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        help_text=password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
