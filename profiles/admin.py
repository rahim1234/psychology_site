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
    if not user.is_authenticated or user.is_superuser:
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
        'created_by', 'created_at_display',
    )
    readonly_fields = ('created_by', 'created_at_display')
    verbose_name = 'یادداشت جلسه'
    verbose_name_plural = 'یادداشت‌های جلسات (فقط قابل مشاهده توسط درمانگر)'

    def created_at_display(self, obj):
        if obj and obj.pk:
            return date_to_jalali_str(obj.created_at)
        return '—'
    created_at_display.short_description = 'تاریخ ثبت (شمسی)'


class ProfileAttachmentForm(forms.ModelForm):
    """Uses the Jalali (Shamsi) date widget for `upload_date`, so the
    secretary enters the file's date the same way the therapist enters
    session-note dates — three plain inputs for year/month/day, no JS
    date-picker, no external dependency."""

    upload_date = JalaliDateFormField(label='تاریخ فایل (شمسی)')

    class Meta:
        model = ProfileAttachment
        fields = ('file', 'upload_date', 'description')




class ProfileAttachmentInline(admin.TabularInline):
    model = ProfileAttachment
    form = ProfileAttachmentForm
    fields = ('file', 'upload_date', 'description', 'file_link', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('file_link', 'uploaded_by', 'uploaded_at')
    verbose_name = 'فایل پیوست'
    verbose_name_plural = 'فایل‌های پیوست پروفایل'

    def get_extra(self, request, obj=None, **kwargs):
        """
        برای منشی: همیشه یک فرم خالی نمایش بده (چون کار اصلی‌اش آپلود فایل است)
        برای درمانگر: هیچ فرم خالی نمایش نده (چون معمولاً فقط یادداشت ثبت می‌کند)
        درمانگر در صورت نیاز می‌تواند روی "Add another" کلیک کند.
        """
        if is_secretary(request.user):
            return 1
        return 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_secretary(request.user):
            return qs.none()
        return qs

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

    # ---- Secretary-specific overrides ---------------------------------

    def get_list_display(self, request):
        """Secretary only sees the user's full name in the list — no test
        counts, no age/gender, no creation date. They click the name to
        open the profile, then upload a file."""
        if is_secretary(request.user):
            return ('full_name',)
        return super().get_list_display(request)

    def get_list_filter(self, request):
        """Hide filters from secretary (they would leak e.g. gender
        distribution of clients)."""
        if is_secretary(request.user):
            return ()
        return super().get_list_filter(request)

    def get_fieldsets(self, request, obj=None):
        """Secretary only sees the client's name (read-only) — no age,
        gender, problem_description, or creation date. Just enough to
        confirm they're on the right profile before uploading a file."""
        if is_secretary(request.user):
            return (
                ('مشاهده کاربر', {
                    'fields': ('full_name',),
                    'description': 'شما به‌عنوان منشی فقط می‌توانید فایل برای این کاربر آپلود کنید. '
                                   'سایر اطلاعات پروفایل برای شما مخفی است.',
                }),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if is_secretary(request.user):
            # Secretary sees only `full_name` (per get_fieldsets above) and
            # cannot change anything on the profile itself — only upload
            # files via the inline below.
            readonly += ['full_name']
        return readonly

    def get_inline_instances(self, request, obj=None):
        if is_secretary(request.user):
            inline_classes = [ProfileAttachmentInline]
        else:
            inline_classes = [SessionNoteInline, ProfileAttachmentInline]
        return [inline_class(self.model, self.admin_site) for inline_class in inline_classes]

    def has_delete_permission(self, request, obj=None):
        if is_secretary(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        # Profiles are created by the users themselves on the site; the
        # secretary must never create profiles, only attach files to
        # existing ones.
        if is_secretary(request.user):
            return False
        return super().has_add_permission(request)

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
                # آزمون‌های قبلی
                extra_context['phq9_results'] = profile.user.phq9_results.all()
                extra_context['gad7_results'] = profile.user.gad7_results.all()
                
                # آزمون‌های جدید
                extra_context['bdi_results'] = profile.user.bdi_results.all()
                extra_context['bai_results'] = profile.user.bai_results.all()
                extra_context['mcmi4_results'] = profile.user.mcmi4_results.all()
        except Exception:
            extra_context['phq9_results'] = []
            extra_context['gad7_results'] = []
            extra_context['bdi_results'] = []
            extra_context['bai_results'] = []
            extra_context['mcmi4_results'] = []
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # ---- Therapist-only helpers ---------------------------------------

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