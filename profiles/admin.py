from django.contrib import admin
from django.utils.html import format_html
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'age', 'gender', 'phq9_count', 'gad7_count', 'created_at')
    list_filter = ('gender',)
    search_fields = ('full_name', 'user__email')
    readonly_fields = ('created_at',)
    fields = ('user', 'full_name', 'age', 'gender', 'problem_description', 'created_at')
    change_form_template = 'admin/profiles/profile/change_form.html'

    def phq9_count(self, obj):
        count = obj.user.phq9_results.count()
        if count == 0:
            return '-'
        return format_html('{} نتیجه', count)
    phq9_count.short_description = 'PHQ-9'

    def gad7_count(self, obj):
        count = obj.user.gad7_results.count()
        if count == 0:
            return '-'
        return format_html('{} نتیجه', count)
    gad7_count.short_description = 'GAD-7'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            profile = self.get_object(request, object_id)
            if profile and hasattr(profile.user, 'phq9_results'):
                extra_context['phq9_results'] = profile.user.phq9_results.all()
                extra_context['gad7_results'] = profile.user.gad7_results.all()
        except Exception:
            extra_context['phq9_results'] = []
            extra_context['gad7_results'] = []
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
