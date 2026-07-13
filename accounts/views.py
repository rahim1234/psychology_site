from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت نام با موفقیت انجام شد!')
            return redirect('profile_create')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomAuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'ورود با موفقیت انجام شد!')
            return redirect('dashboard')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'شما با موفقیت خارج شدید.')
        return redirect('home')
