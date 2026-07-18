from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    PHQ9Result, GAD7Result,
    BDIResult, BAIResult, MCMI4Result,
)


@admin.register(PHQ9Result)
class PHQ9ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'answers_summary', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('created_at', 'answers_formatted')
    fields = ('user', 'score', 'severity', 'answers_formatted', 'created_at')

    def answers_summary(self, obj):
        if not obj.answers:
            return '-'
        vals = [obj.answers.get(f'q{i}', '0') for i in range(1, 10)]
        return ' | '.join(vals)
    answers_summary.short_description = 'پاسخ‌ها'

    def answers_formatted(self, obj):
        if not obj.answers:
            return '-'
        labels = [
            '۱. علاقه/لذت به کارهای روزمره',
            '۲. احساس ناراحتی/افسردگی',
            '۳. مشکل خواب',
            '۴. خستگی/کمبود انرژی',
            '۵. تغییر اشتها',
            '۶. احساس بد نسبت به خود',
            '۷. مشکل تمرکز',
            '۸. کندی حرکت/صحبت',
            '۹. افکار آسیب رساندن به خود',
        ]
        answers_text = []
        for i, label in enumerate(labels, 1):
            val = obj.answers.get(f'q{i}', '?')
            answers_text.append(f'{label}: <strong>{val}</strong>')
        return mark_safe('<br>'.join(answers_text))
    answers_formatted.short_description = 'پاسخ‌ها (formatted)'


@admin.register(GAD7Result)
class GAD7ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'answers_summary', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('created_at', 'answers_formatted')
    fields = ('user', 'score', 'severity', 'answers_formatted', 'created_at')

    def answers_summary(self, obj):
        if not obj.answers:
            return '-'
        vals = [obj.answers.get(f'q{i}', '0') for i in range(1, 8)]
        return ' | '.join(vals)
    answers_summary.short_description = 'پاسخ‌ها'

    def answers_formatted(self, obj):
        if not obj.answers:
            return '-'
        labels = [
            '۱. احساس عصبی بودن/نگرانی',
            '۲. ناتوانی در کنترل نگرانی',
            '۳. نگرانی‌های زیاد',
            '۴. مشکل در آرام شدن',
            '۵. آشفتگی/بی‌قراری',
            '۶. بی‌صبری/تحریک‌پذیری',
            '۷. ترس از اتفاق وحشتناک',
        ]
        answers_text = []
        for i, label in enumerate(labels, 1):
            val = obj.answers.get(f'q{i}', '?')
            answers_text.append(f'{label}: <strong>{val}</strong>')
        return mark_safe('<br>'.join(answers_text))
    answers_formatted.short_description = 'پاسخ‌ها (formatted)'


@admin.register(BDIResult)
class BDIResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(BAIResult)
class BAIResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(MCMI4Result)
class MCMI4ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('created_at',)