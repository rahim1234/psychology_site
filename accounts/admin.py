from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from profiles.models import Profile
from assessments.models import PHQ9Result, GAD7Result


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'پروفایل'
    fields = ('full_name', 'age', 'gender', 'problem_description')


class PHQ9Inline(admin.TabularInline):
    model = PHQ9Result
    extra = 0
    readonly_fields = ('score', 'severity', 'answers_display', 'created_at')
    fields = ('score', 'severity', 'answers_display', 'created_at')
    can_delete = False
    max_num = 0

    def answers_display(self, obj):
        if not obj.answers:
            return '-'
        labels = [
            'عللاقه/لذت', 'ناراحتی', 'خواب', 'خستگی', 'اشتها',
            'احساس بد', 'تمرکز', 'کندی', 'افکار آزاردهنده'
        ]
        lines = []
        for i in range(1, 10):
            key = f'q{i}'
            val = obj.answers.get(key, '?')
            label = labels[i-1] if i <= len(labels) else f'Q{i}'
            lines.append(f'{label}: {val}')
        return '\n'.join(lines)
    answers_display.short_description = 'پاسخ‌ها'


class GAD7Inline(admin.TabularInline):
    model = GAD7Result
    extra = 0
    readonly_fields = ('score', 'severity', 'answers_display', 'created_at')
    fields = ('score', 'severity', 'answers_display', 'created_at')
    can_delete = False
    max_num = 0

    def answers_display(self, obj):
        if not obj.answers:
            return '-'
        labels = [
            'عصبی بودن', 'کنترل نگرانی', 'نگرانی‌های زیاد', 'آرام شدن',
            'آشفتگی', 'بی‌صبری', 'ترس'
        ]
        lines = []
        for i in range(1, 8):
            key = f'q{i}'
            val = obj.answers.get(key, '?')
            label = labels[i-1] if i <= len(labels) else f'Q{i}'
            lines.append(f'{label}: {val}')
        return '\n'.join(lines)
    answers_display.short_description = 'پاسخ‌ها'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'has_profile')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    inlines = [ProfileInline, PHQ9Inline, GAD7Inline]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('username', 'first_name', 'last_name')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    def has_profile(self, obj):
        return hasattr(obj, 'profile')
    has_profile.boolean = True
    has_profile.short_description = 'پروفایل'
