from .models import MenuItem


def extra_menu_items(request):
    """آیتم‌های منوی اضافه (قابل مدیریت توسط سوپریوزر) را در تمام صفحات در دسترس می‌گذارد.

    با try/except محافظت شده تا اگر migration هنوز اجرا نشده باشد، کل سایت خطا ندهد.
    """
    try:
        items = list(MenuItem.objects.filter(is_active=True).order_by('order', 'id'))
    except Exception:
        items = []
    return {'extra_menu_items': items}
