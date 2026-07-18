from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-phone/', views.VerifyPhoneView.as_view(), name='verify_phone'),
    path('verify-phone/resend/', views.ResendVerificationView.as_view(), name='resend_verification'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # تغییر رمز عبور از داخل داشبورد
    path('password-change/', views.ChangePasswordView.as_view(), name='password_change'),

    # فراموشی رمز عبور (از طریق پیامک)
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', views.PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
