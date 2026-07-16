"""One-time setup command for the 'منشی' (secretary) role.

Creates the auth group named exactly `منشی` and assigns it the exact set
of permissions the secretary is allowed to have. Re-running the command
is safe — it will reset the group's permissions to the canonical set
defined here, so it can also be used to "repair" a group that was
mis-configured manually in the admin.

Usage:
    python manage.py setup_secretary_group
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from profiles.admin import SECRETARY_GROUP_NAME
from profiles.models import Profile, ProfileAttachment


# (Model, permission codename, human-readable label)
SECRETARY_PERMISSIONS = [
    (Profile, 'view_profile',          'مشاهده‌ی پروفایل کاربر'),
    (Profile, 'change_profile',        'ویرایش پروفایل (فقط برای ذخیره‌ی فرم آپلود فایل)'),
    (ProfileAttachment, 'view_profileattachment', 'مشاهده‌ی فایل‌های پیوست پروفایل'),
    (ProfileAttachment, 'add_profileattachment',  'افزودن فایل پیوست پروفایل'),
]


class Command(BaseCommand):
    help = (
        'گروه «منشی» را می‌سازد (اگر نباشد) و دقیقاً همان مجوزهای لازم را به '
        'آن می‌دهد. اجرای دوباره‌ی این دستور بی‌خطر است و مجوزها را به حالت '
        'استاندارد برمی‌گرداند.'
    )

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name=SECRETARY_GROUP_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'✓ گروه «{SECRETARY_GROUP_NAME}» ساخته شد.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'• گروه «{SECRETARY_GROUP_NAME}» از قبل وجود داشت — '
                f'مجوزها به حالت استاندارد بازنشانی می‌شود.'
            ))

        # Reset to the canonical permission set — important so re-running
        # the command also fixes a group that someone manually mis-granted
        # extra permissions to in the admin.
        group.permissions.clear()

        for model, codename, label in SECRETARY_PERMISSIONS:
            content_type = ContentType.objects.get_for_model(model)
            permission = Permission.objects.get(content_type=content_type, codename=codename)
            group.permissions.add(permission)
            self.stdout.write(f'  ✓ {label} — {model._meta.app_label}.{codename}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ {len(SECRETARY_PERMISSIONS)} مجوز به گروه «{SECRETARY_GROUP_NAME}» اختصاص داده شد.'
        ))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('مراحل بعدی (یک‌بار، توسط ادمین اصلی):')
        self.stdout.write('=' * 60)
        self.stdout.write(
            '  ۱. یک حساب کاربری برای منشی بسازید یا حساب موجود را ویرایش کنید:\n'
            '     /admin/accounts/user/add/\n'
            '     (یا /admin/accounts/user/<id>/change/)'
        )
        self.stdout.write(
            '  ۲. تیک «Staff status» را بزنید (لازم برای ورود به /admin/).\n'
            '     تیک «Superuser status» را نزنید!'
        )
        self.stdout.write(
            '  ۳. در بخش «Groups»، گروه «منشی» را به سمت راست منتقل کنید.'
        )
        self.stdout.write('  ۴. رمز عبور را تنظیم و ذخیره کنید.')
        self.stdout.write('')
        self.stdout.write(
            'از این پس، منشی با ورود به /admin/ فقط لیست نام کاربران را '
            'می‌بیند، با کلیک روی نام کاربر می‌تواند فایل به همراه تاریخ آپلود '
            'کند، و به هیچ‌یک از یادداشت‌های دکتر، نتایج آزمون‌ها، یا سایر '
            'اطلاعات پروفایل دسترسی ندارد.'
        )
