from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .forms import CustomAuthenticationForm, CustomUserCreationForm, VerificationCodeForm
from .models import EmailVerification
from .utils import VerificationEmailError, create_and_send_verification

User = get_user_model()

PENDING_USER_SESSION_KEY = 'pending_verification_user_id'


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
            verification = EmailVerification.objects.create(user=user, expires_at=user.date_joined)
            try:
                create_and_send_verification(user, verification)
            except VerificationEmailError:
                messages.error(
                    request,
                    'ثبت نام انجام شد اما ارسال ایمیل تایید با خطا مواجه شد. '
                    'لطفاً از صفحه‌ی بعد دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.',
                )
            else:
                messages.success(request, 'کد تایید به ایمیل شما ارسال شد.')
            request.session[PENDING_USER_SESSION_KEY] = user.pk
            return redirect('verify_email')
        return render(request, 'accounts/register.html', {'form': form})


class VerifyEmailView(View):
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
        return render(request, 'accounts/verify_email.html', {'form': form, 'email': user.email})

    def post(self, request):
        user = self._get_pending_user(request)
        if not user:
            messages.info(request, 'لطفاً ابتدا ثبت نام کنید.')
            return redirect('register')

        form = VerificationCodeForm(request.POST)
        verification = getattr(user, 'email_verification', None)

        if form.is_valid() and verification:
            if verification.attempts >= settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
                messages.error(request, 'تعداد تلاش‌های مجاز به پایان رسید. لطفاً کد جدید درخواست کنید.')
            elif verification.is_expired():
                messages.error(request, 'کد تایید منقضی شده است. لطفاً کد جدید درخواست کنید.')
            elif verification.check_code(form.cleaned_data['code']):
                user.is_active = True
                user.save(update_fields=['is_active'])
                verification.delete()
                del request.session[PENDING_USER_SESSION_KEY]
                login(request, user, backend='accounts.backends.EmailBackend')
                messages.success(request, 'ایمیل شما با موفقیت تایید شد!')
                return redirect('profile_create')
            else:
                verification.attempts += 1
                verification.save(update_fields=['attempts'])
                messages.error(request, 'کد تایید نادرست است.')
        else:
            messages.error(request, 'کد تایید نامعتبر است.')

        return render(request, 'accounts/verify_email.html', {'form': form, 'email': user.email})


@method_decorator(require_POST, name='dispatch')
class ResendVerificationView(View):
    def post(self, request):
        user_id = request.session.get(PENDING_USER_SESSION_KEY)
        user = User.objects.filter(pk=user_id, is_active=False).first() if user_id else None
        if not user:
            messages.info(request, 'لطفاً ابتدا ثبت نام کنید.')
            return redirect('register')

        verification, _ = EmailVerification.objects.get_or_create(
            user=user, defaults={'expires_at': user.date_joined}
        )
        remaining = verification.seconds_until_can_resend(settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS)
        if remaining > 0:
            messages.warning(request, f'لطفاً {remaining} ثانیه دیگر دوباره تلاش کنید.')
        else:
            try:
                create_and_send_verification(user, verification)
            except VerificationEmailError:
                messages.error(request, 'ارسال ایمیل با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.')
            else:
                messages.success(request, 'کد تایید جدید ارسال شد.')
        return redirect('verify_email')


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
