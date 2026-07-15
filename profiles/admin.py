from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .jalali import date_to_jalali_str
from .models import Profile, ProfileAttachment, SessionNote
from .widgets import JalaliDateFormField

SECRETARY_GROUP_NAME = 'منشی'


def is_secretary(user):
    """True for staff who are in the 'منشی' (secretary) group and are not
    full admins. Superusers/therapists are never treated as secretary even
    if someone also adds them to the group by mistake."""
    if user.is_superuser:
        return False
    return user.groups.filter(name=SECRETARY_GROUP_NAME).exists()


class SessionNoteForm(forms.ModelForm):
    session_date = JalaliDateFormField(label='تاریخ جلسه (شمسی)')

    class Meta:
        model = SessionNote
        fields = '__all__'


class SessionNoteInline(admin.StackedInline):
    """Therapist-only. Never include this inline for the secretary role —
    see ProfileAdmin.get_inline_instances()."""

    model = SessionNote
    form = SessionNoteForm
    extra = 0
    fields = (
        'session_date',
        'content',
        'image', 'image_preview',
        'audio', 'audio_preview',
        'video', 'video_preview',
        'created_by', 'created_at_display',
    )
    readonly_fields = ('created_by', 'created_at_display', 'image_preview', 'audio_preview', 'video_preview')
    verbose_name = 'یادداشت جلسه'
    verbose_name_plural = 'یادداشت‌های جلسات (فقط قابل مشاهده توسط درمانگر)'

    def created_at_display(self, obj):
        if obj and obj.pk:
            return date_to_jalali_str(obj.created_at)
        return '—'
    created_at_display.short_description = 'تاریخ ثبت (شمسی)'

    def _protected_url(self, kind, obj):
        return reverse('protected_media', args=[kind, obj.pk])

    def image_preview(self, obj):
        if obj and obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:200px;border-radius:6px;object-fit:cover;">',
                self._protected_url('session-note-image', obj),
            )
        return '—'
    image_preview.short_description = 'پیش‌نمایش تصویر'

    def audio_preview(self, obj):
        if obj and obj.pk and obj.audio:
            return format_html(
                '<audio controls src="{}" style="max-width:260px;"></audio>',
                self._protected_url('session-note-audio', obj),
            )
        return '—'
    audio_preview.short_description = 'پخش فایل صوتی'

    def video_preview(self, obj):
        if obj and obj.pk and obj.video:
            return format_html(
                '<video controls src="{}" style="max-width:280px;max-height:200px;"></video>',
                self._protected_url('session-note-video', obj),
            )
        return '—'
    video_preview.short_description = 'پخش ویدیو'


class ProfileAttachmentInline(admin.TabularInline):
    """Where the secretary uploads files. Only 'add' + 'view' permission is
    granted to the secretary group (see README for the one-time setup) —
    no 'change'/'delete', so once a file is uploaded it can't be replaced
    or removed by the secretary, only by the therapist/superuser."""

    model = ProfileAttachment
    extra = 1
    fields = ('file', 'description', 'file_link', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('file_link', 'uploaded_by', 'uploaded_at')
    verbose_name = 'فایل پیوست'
    verbose_name_plural = 'فایل‌های پیوست پروفایل'

    def file_link(self, obj):
        if obj and obj.pk and obj.file:
            url = reverse('protected_media', args=['profile-attachment', obj.pk])
            return format_html('<a href="{}" target="_blank">دانلود / مشاهده فایل</a>', url)
        return '—'
    file_link.short_description = 'لینک فایل'


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

    def get_inline_instances(self, request, obj=None):
        if is_secretary(request.user):
            inline_classes = [ProfileAttachmentInline]
        else:
            inline_classes = [SessionNoteInline, ProfileAttachmentInline]
        return [inline_class(self.model, self.admin_site) for inline_class in inline_classes]

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if is_secretary(request.user):
            # Secretary can see client info to find the right profile, but
            # can't change it — only upload files via the inline above.
            readonly += ['user', 'full_name', 'age', 'gender', 'problem_description']
        return readonly

    def has_delete_permission(self, request, obj=None):
        if is_secretary(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, SessionNote) and not instance.created_by_id:
                instance.created_by = request.user
            if isinstance(instance, ProfileAttachment) and not instance.uploaded_by_id:
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_test_results'] = not is_secretary(request.user)
        try:
            profile = self.get_object(request, object_id)
            if profile and hasattr(profile.user, 'phq9_results') and not is_secretary(request.user):
                extra_context['phq9_results'] = profile.user.phq9_results.all()
                extra_context['gad7_results'] = profile.user.gad7_results.all()
        except Exception:
            extra_context['phq9_results'] = []
            extra_context['gad7_results'] = []
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
