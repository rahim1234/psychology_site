from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from captcha.fields import CaptchaField
from core.honeypot import HoneypotField

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'})
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
        fields = ('email', 'username', 'password1', 'password2', 'captcha')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        existing = User.objects.filter(email__iexact=email).first()
        if existing and existing.is_active:
            raise forms.ValidationError('این ایمیل قبلاً ثبت نام شده است.')
        return email

    def save(self, commit=True):
        # Remove any stale, never-verified account tied to this email so the
        # person can re-register (e.g. they lost their verification code).
        User.objects.filter(email__iexact=self.cleaned_data['email'], is_active=False).delete()
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'})
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
            'ایمیل یا رمز عبور اشتباه است، یا حساب شما هنوز تایید نشده است. '
            'اگر تازه ثبت نام کرده‌اید، ایمیل خود را برای کد تایید بررسی کنید.'
        ),
    }


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
