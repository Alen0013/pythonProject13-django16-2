from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('blog:pet_list')  # Исправлено с 'post_list' на 'pet_list'
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли!')
            return redirect('blog:pet_list')  # Исправлено с 'post_list' на 'pet_list'
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def profile(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    return render(request, 'users/profile.html', {'user': request.user})


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли!')
    return redirect('blog:pet_list')  # Исправлено с 'post_list' на 'pet_list'
