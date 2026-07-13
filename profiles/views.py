from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Profile
from .forms import ProfileForm
from assessments.models import PHQ9Result, GAD7Result


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


from django.shortcuts import render


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        form = ProfileForm(instance=request.user.profile)
        return render(request, 'profiles/profile_form.html', {'form': form, 'title': 'ویرایش پروفایل'})

    def post(self, request):
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
        return context
