from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config('DEBUG', default=False, cast=bool)

SECRET_KEY = config('SECRET_KEY', default='')
if not SECRET_KEY:
    if DEBUG:
        # Convenience fallback for local development only.
        SECRET_KEY = 'django-insecure-dev-only-key-do-not-use-in-production'
    else:
        raise RuntimeError(
            'SECRET_KEY environment variable is not set. '
            'Set it in your .env file before running with DEBUG=False.'
        )

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'profiles',
    'assessments',
    'blog',
    'core',
    'ckeditor',
    'ckeditor_uploader',
    'captcha',
    'django.contrib.sitemaps',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Files here (session-note attachments, profile attachments) are NEVER served
# directly by nginx/staticfiles — only through the login-protected view in
# profiles.views.protected_media. Kept outside MEDIA_ROOT on purpose.
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# --- Email (used for the signup verification-code flow) -------------------
# In development, codes are printed to the console by default so no real
# mail server is required. In production, set EMAIL_BACKEND and the SMTP
# variables below in your .env file.
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@psychology-center.ir')

# Email-verification code behaviour (accounts app)
EMAIL_VERIFICATION_TTL_MINUTES = config('EMAIL_VERIFICATION_TTL_MINUTES', default=10, cast=int)
EMAIL_VERIFICATION_MAX_ATTEMPTS = config('EMAIL_VERIFICATION_MAX_ATTEMPTS', default=5, cast=int)
EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS = config('EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS', default=60, cast=int)

# --- Production hardening (safe no-ops in DEBUG mode) -----------------------
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'



# 2. تنظیمات CKEditor
CKEDITOR_UPLOAD_PATH = "blog/uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

# 3. پیکربندی ویرایشگر برای پشتیبانی کامل از فارسی و امکانات پیشرفته
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'contentsLangDirection': 'rtl',  # راست‌چین برای فارسی
        'language': 'fa',
        'extraPlugins': ','.join([
            'uploadimage',
            'image2',
            'table',
            'tabletools',
            'codesnippet',
            'embed',
            'autogrow',
        ]),
        'toolbar_full': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'Preview', 'Print']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            '/',
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'CodeSnippet', 'Embed']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
        ],
    }
}

# ============================================================================
# 🔒 SECURITY SETTINGS - Session Management
# ============================================================================

# نشست کاربر بعد از 30 دقیقه عدم فعالیت منقضی می‌شود
SESSION_COOKIE_AGE = 1800  # 30 دقیقه (به ثانیه)

# با بستن مرورگر، نشست پاک می‌شود
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# هر درخواست، عمر نشست را تمدید می‌کند (sliding session)
SESSION_SAVE_EVERY_REQUEST = True

# cookie نشست فقط از طریق HTTPS ارسال شود (در production)
# SESSION_COOKIE_SECURE = True  # فقط در production فعال شود

# جلوگیری از دسترسی JavaScript به cookie نشست
SESSION_COOKIE_HTTPONLY = True

# cookie نشست فقط در همان سایت استفاده شود (جلوگیری از CSRF)
SESSION_COOKIE_SAMESITE = 'Lax'

# نام cookie نشست (غیرقابل حدس زدن)
SESSION_COOKIE_NAME = 'psych_session_id'

# ============================================================================
# 🔒 SECURITY SETTINGS - HTTP Security Headers
# ============================================================================

# جلوگیری از Clickjacking (سایت شما در iframe نمایش داده نشود)
X_FRAME_OPTIONS = 'DENY'

# فعال کردن XSS Filter در مرورگر
SECURE_BROWSER_XSS_FILTER = True

# جلوگیری از MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# جلوگیری از نمایش سایت در نتایج جستجو (اگر سایت خصوصی است)
# SECURE_REFERRER_POLICY = 'same-origin'

# ============================================================================
# 🌐 HTTPS Settings (فقط در Production فعال شود)
# ============================================================================
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# CSRF_COOKIE_SECURE = True

# ============================================================================
# 🔒 Rate Limiting Settings
# ============================================================================

# فعال‌سازی Rate Limiting
RATELIMIT_ENABLE = True

# روش بررسی: بر اساس IP (مناسب برای جلوگیری از حملات)
RATELIMIT_VIEW = 'accounts.views.ratelimited_error'

# استفاده از cache برای شمارش درخواست‌ها
# از cache حافظه (ساده‌ترین) استفاده می‌کنیم
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ratelimit-cache',
    }
}
# پشت پروکسی بودن (برای production با Nginx)
RATELIMIT_USE_X_FORWARDED_FOR = True
# پیام خطای سفارشی وقتی rate limit زده شد
RATELIMIT_ERROR_MESSAGE = 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # ✅ اضافه شده: Rate Limit Middleware (باید آخر باشد)
    'accounts.middleware.RatelimitMiddleware',
]