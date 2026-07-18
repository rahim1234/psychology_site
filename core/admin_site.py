from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


@method_decorator(
    ratelimit(key='ip', rate='10/h', method='POST', block=True),
    name='login',
)
class RateLimitedAdminSite(AdminSite):
    """Adds IP-based rate limiting to the Django admin login form.

    The rate limits in accounts/views.py only wrap the patient-facing
    register/login/verify views — the built-in admin login was otherwise
    completely unthrottled, so a brute-force attempt against a staff
    account's password would never be slowed down. `RatelimitMiddleware`
    (already in MIDDLEWARE) catches the resulting Ratelimited exception
    and shows the same 429 page used everywhere else on the site.

    The decorator is applied via `method_decorator(..., name='login')` on
    the class (exactly like `@method_decorator(ratelimit(...), name='dispatch')`
    elsewhere in this project) rather than directly on the method — putting
    it directly on `def login(self, request, ...)` makes django-ratelimit
    treat `self` as if it were the request object, since it always expects
    request to be the first positional argument it receives.
    """


class RateLimitedAdminConfig(AdminConfig):
    """Points django.contrib.admin at RateLimitedAdminSite above.

    Deliberately NOT in core/apps.py: that module is also what Django
    auto-loads as the 'core' app's own AppConfig (since 'core' is listed
    bare in INSTALLED_APPS) — importing another AppConfig subclass there
    makes Django unable to tell which one is core's default and it refuses
    to start ("declares more than one default AppConfig").
    """
    default_site = 'core.admin_site.RateLimitedAdminSite'
