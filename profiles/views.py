import os

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView
from assessments.models import GAD7Result, PHQ9Result, BDIResult, BAIResult, MCMI4Result
from .forms import ProfileForm
from .models import ProfileAttachment, SessionNote


class ProfileCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if hasattr(request.user, 'profile'):
            return redirect('profile_update')
        form = ProfileForm()
        return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'ایجاد پروفایل'})

    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'پروفایل با موفقیت ایجاد شد!')
            return redirect('dashboard')
        return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'ایجاد پروفایل'})


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        form = ProfileForm(instance=request.user.profile)
        return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'ویرایش پروفایل'})

    def post(self, request):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد!')
            return redirect('dashboard')
        return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'ویرایش پروفایل'})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = getattr(self.request.user, 'profile', None)
        context['phq9_results'] = PHQ9Result.objects.filter(user=self.request.user)[:5]
        context['gad7_results'] = GAD7Result.objects.filter(user=self.request.user)[:5]
        context['bdi_results'] = BDIResult.objects.filter(user=self.request.user)[:3]
        context['bai_results'] = BAIResult.objects.filter(user=self.request.user)[:3]
        context['mcmi4_results'] = MCMI4Result.objects.filter(user=self.request.user)[:3]
        return context


# kind -> (model, field name on that model holding the file)
_PROTECTED_FILE_KINDS = {
    'session-note-image': (SessionNote, 'image'),
    'session-note-audio': (SessionNote, 'audio'),
    'session-note-video': (SessionNote, 'video'),
    'profile-attachment': (ProfileAttachment, 'file'),
}


@staff_member_required
def protected_media(request, kind, pk):
    """Serve a session-note/profile attachment only to a logged-in staff
    user who also holds Django's `view_<model>` permission for it — so a
    secretary who only has permission on ProfileAttachment can never reach
    a SessionNote file even by guessing/reusing a URL, and no one who isn't
    logged in can reach any of these files at all.
    """
    if kind not in _PROTECTED_FILE_KINDS:
        raise Http404
    model, field_name = _PROTECTED_FILE_KINDS[kind]

    required_perm = f'{model._meta.app_label}.view_{model._meta.model_name}'
    if not request.user.has_perm(required_perm):
        raise PermissionDenied

    obj = get_object_or_404(model, pk=pk)
    file_field = getattr(obj, field_name)
    if not file_field:
        raise Http404

    file_field.open('rb')
    filename = os.path.basename(file_field.name)
    return FileResponse(file_field.file, filename=filename)
