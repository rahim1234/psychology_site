from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    PhoneNumberForm,
    StyledPasswordChangeForm,
    StyledSetPasswordForm,
    VerificationCodeForm,
)
from .models import PhoneVerification
from .utils import SMSSendError, create_and_send_verification, ratelimit_key_phone_number

User = get_user_model()

PENDING_USER_SESSION_KEY = 'pending_verification_user_id'
PASSWORD_RESET_PHONE_SESSION_KEY = 'password_reset_phone_number'
PASSWORD_RESET_VERIFIED_KEY = 'password_reset_verified'


# ============================================================================
# 🔒 View سفارشی برای نمایش خطای Rate Limit (429)
# ============================================================================
def ratelimited_error(request, exception=None):
    """
    View سفارشی برای نمایش صفحه 429 Too Many Requests.
    """
    return render(request, 'accounts/ratelimited.html', status=429)


# ============================================================================
# ثبت نام با Rate Limit: 3 بار در ساعت
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='3/h', method='POST', block=True),
    name='dispatch'
)
@method_decorator(
    ratelimit(key=ratelimit_key_phone_number, rate='3/h', method='POST', block=True),
    name='dispatch'
)
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            verification = PhoneVerification.objects.create(user=user, expires_at=user.date_joined)
            try:
                create_and_send_verification(user, verification)
            except SMSSendError:
                messages.error(
                    request,
                    'ثبت نام انجام شد اما ارسال پیامک تایید با خطا مواجه شد. '
                    'لطفاً از صفحه‌ی بعد دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.',
                )
            else:
                messages.success(request, 'کد تایید به شماره موبایل شما پیامک شد.')
            request.session[PENDING_USER_SESSION_KEY] = user.pk
            return redirect('verify_phone')
        return render(request, 'accounts/register.html', {'form': form})


# ============================================================================
# تایید شماره موبایل با Rate Limit: 10 بار در دقیقه (جلوگیری از حدس کد)
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST', block=True),
    name='dispatch'
)
class VerifyPhoneView(View):
    def _get_pending_user(self, request):
        user_id = request.session.get(PENDING_USER_SESSION_KEY)
        if not user_id:
            return None
        return User.objects.filter(pk=user_id, is_active=False).first()

    def get(self, request):
        user = self._get_pending_user(request)
        if not user:
            messages.info(request, 'لطفاً ابتدا ثبت نام کنید.')
            return redirect('register')
        form = VerificationCodeForm()
        return render(request, 'accounts/verify_phone.html', {'form': form, 'phone_number': user.phone_number})

    def post(self, request):
        user = self._get_pending_user(request)
        if not user:
            messages.info(request, 'لطفاً ابتدا ثبت نام کنید.')
            return redirect('register')

        form = VerificationCodeForm(request.POST)
        verification = getattr(user, 'phone_verification', None)

        if form.is_valid() and verification:
            if verification.attempts >= settings.PHONE_VERIFICATION_MAX_ATTEMPTS:
                messages.error(request, 'تعداد تلاش‌های مجاز به پایان رسید. لطفاً کد جدید درخواست کنید.')
            elif verification.is_expired():
                messages.error(request, 'کد تایید منقضی شده است. لطفاً کد جدید درخواست کنید.')
            elif verification.check_code(form.cleaned_data['code']):
                user.is_active = True
                user.save(update_fields=['is_active'])
                verification.delete()
                del request.session[PENDING_USER_SESSION_KEY]
                login(request, user, backend='accounts.backends.PhoneNumberBackend')
                messages.success(request, 'شماره موبایل شما با موفقیت تایید شد!')
                return redirect('profile_create')
            else:
                verification.attempts += 1
                verification.save(update_fields=['attempts'])
                messages.error(request, 'کد تایید نادرست است.')
        else:
            messages.error(request, 'کد تایید نامعتبر است.')

        return render(request, 'accounts/verify_phone.html', {'form': form, 'phone_number': user.phone_number})


# ============================================================================
# ارسال مجدد کد تایید: 3 بار در ساعت (جلوگیری از spam پیامکی)
# ============================================================================
@method_decorator(require_POST, name='dispatch')
@method_decorator(
    ratelimit(key='ip', rate='3/h', method='POST', block=True),
    name='dispatch'
)
class ResendVerificationView(View):
    def post(self, request):
        user_id = request.session.get(PENDING_USER_SESSION_KEY)
        user = User.objects.filter(pk=user_id, is_active=False).first() if user_id else None
        if not user:
            messages.info(request, 'لطفاً ابتدا ثبت نام کنید.')
            return redirect('register')

        verification, created = PhoneVerification.objects.get_or_create(
            user=user, defaults={'expires_at': user.date_joined}
        )
        remaining = 0 if created else verification.seconds_until_can_resend(
            settings.PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS
        )
        if remaining > 0:
            messages.warning(request, f'لطفاً {remaining} ثانیه دیگر دوباره تلاش کنید.')
        else:
            try:
                create_and_send_verification(user, verification)
            except SMSSendError:
                messages.error(request, 'ارسال پیامک با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.')
            else:
                messages.success(request, 'کد تایید جدید پیامک شد.')
        return redirect('verify_phone')


# ============================================================================
# ورود با Rate Limit: 5 بار در دقیقه (جلوگیری از brute force)
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='5/m', method='POST', block=True),
    name='dispatch'
)
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomAuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'ورود با موفقیت انجام شد!')
            return redirect('dashboard')
        return render(request, 'accounts/login.html', {'form': form})


@method_decorator(require_POST, name='dispatch')
class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'شما با موفقیت خارج شدید.')
        return redirect('home')


# ============================================================================
# تغییر رمز عبور از داشبورد (کاربر لاگین است و رمز فعلی را می‌داند)
# ============================================================================
class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        form = StyledPasswordChangeForm(user=request.user)
        return render(request, 'accounts/password_change.html', {'form': form})

    def post(self, request):
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # جلوگیری از خروج خودکار کاربر بعد از تغییر رمز
            update_session_auth_hash(request, form.user)
            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد.')
            return redirect('dashboard')
        return render(request, 'accounts/password_change.html', {'form': form})


# ============================================================================
# فراموشی رمز عبور — از طریق پیامک، سه مرحله‌ای
# مرحله ۱: گرفتن شماره موبایل و ارسال کد
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='3/h', method='POST', block=True),
    name='dispatch'
)
@method_decorator(
    ratelimit(key=ratelimit_key_phone_number, rate='3/h', method='POST', block=True),
    name='dispatch'
)
class PasswordResetRequestView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = PhoneNumberForm()
        return render(request, 'accounts/password_reset_request.html', {'form': form})

    def post(self, request):
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            # عمداً برای شماره‌ی موجود و ناموجود، پیام یکسان نشان داده می‌شود
            # تا امکان حدس زدن اینکه چه کسی در سایت ثبت نام کرده وجود نداشته باشد.
            user = User.objects.filter(phone_number=phone_number, is_active=True).first()
            if user:
                verification, created = PhoneVerification.objects.get_or_create(
                    user=user, defaults={'expires_at': user.date_joined}
                )
                # A brand-new row's `last_sent_at` defaults to "now" even though
                # nothing has been sent yet, which would otherwise make
                # seconds_until_can_resend() think the cooldown already started
                # and silently skip the very first SMS. Only enforce the
                # cooldown for a row that already existed (i.e. a real resend).
                remaining = 0 if created else verification.seconds_until_can_resend(
                    settings.PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS
                )
                if remaining <= 0:
                    try:
                        create_and_send_verification(user, verification, purpose='password_reset')
                    except SMSSendError:
                        pass
            request.session[PASSWORD_RESET_PHONE_SESSION_KEY] = phone_number
            request.session.pop(PASSWORD_RESET_VERIFIED_KEY, None)
            messages.success(request, 'اگر این شماره در سیستم ثبت شده باشد، کد بازیابی برای آن پیامک شد.')
            return redirect('password_reset_verify')
        return render(request, 'accounts/password_reset_request.html', {'form': form})


# ============================================================================
# مرحله ۲: تایید کد پیامکی
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST', block=True),
    name='dispatch'
)
class PasswordResetVerifyView(View):
    def _get_phone(self, request):
        return request.session.get(PASSWORD_RESET_PHONE_SESSION_KEY)

    def get(self, request):
        phone_number = self._get_phone(request)
        if not phone_number:
            return redirect('password_reset_request')
        form = VerificationCodeForm()
        return render(request, 'accounts/password_reset_verify.html', {'form': form, 'phone_number': phone_number})

    def post(self, request):
        phone_number = self._get_phone(request)
        if not phone_number:
            return redirect('password_reset_request')

        form = VerificationCodeForm(request.POST)
        user = User.objects.filter(phone_number=phone_number, is_active=True).first()
        verification = getattr(user, 'phone_verification', None) if user else None
        generic_error = 'کد وارد شده صحیح نیست یا منقضی شده است.'

        if form.is_valid() and user and verification:
            if verification.attempts >= settings.PHONE_VERIFICATION_MAX_ATTEMPTS:
                messages.error(request, 'تعداد تلاش‌های مجاز به پایان رسید. لطفاً دوباره درخواست بازیابی رمز را بدهید.')
            elif verification.is_expired():
                messages.error(request, generic_error)
            elif verification.check_code(form.cleaned_data['code']):
                verification.delete()
                request.session[PASSWORD_RESET_VERIFIED_KEY] = True
                return redirect('password_reset_confirm')
            else:
                verification.attempts += 1
                verification.save(update_fields=['attempts'])
                messages.error(request, generic_error)
        else:
            # همان پیام عمومی؛ چه شماره موجود نباشد چه کد اشتباه باشد
            messages.error(request, generic_error)

        return render(request, 'accounts/password_reset_verify.html', {'form': form, 'phone_number': phone_number})


# ============================================================================
# مرحله ۳: تعیین رمز عبور جدید (فقط بعد از تایید موفق کد در مرحله ۲)
# ============================================================================
@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST', block=True),
    name='dispatch'
)
class PasswordResetConfirmView(View):
    def _get_user(self, request):
        if not request.session.get(PASSWORD_RESET_VERIFIED_KEY):
            return None
        phone_number = request.session.get(PASSWORD_RESET_PHONE_SESSION_KEY)
        if not phone_number:
            return None
        return User.objects.filter(phone_number=phone_number, is_active=True).first()

    def get(self, request):
        user = self._get_user(request)
        if not user:
            return redirect('password_reset_request')
        form = StyledSetPasswordForm(user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})

    def post(self, request):
        user = self._get_user(request)
        if not user:
            return redirect('password_reset_request')
        form = StyledSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            for key in (PASSWORD_RESET_PHONE_SESSION_KEY, PASSWORD_RESET_VERIFIED_KEY):
                request.session.pop(key, None)
            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.')
            return redirect('login')
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
