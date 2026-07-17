from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited


class RatelimitMiddleware:
    """
    Middleware برای تبدیل exception Ratelimited به صفحه 429 سفارشی.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return render(request, 'accounts/ratelimited.html', status=429)
        return None