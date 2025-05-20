from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm
from .models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_mail(
                'Добро пожаловать!',
                f'Привет, {user.email}! Твой аккаунт успешно создан.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Регистрация успешна! Письмо с подтверждением отправлено.')
            return redirect('blog:pet_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
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
            return redirect('blog:pet_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"Ошибка в поле '{form[field].label}': {error}")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/update_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'Неверный текущий пароль.')
            return render(request, 'users/change_password.html')

        if new_password1 != new_password2:
            messages.error(request, 'Новые пароли не совпадают.')
            return render(request, 'users/change_password.html')

        if len(new_password1) < 8:
            messages.error(request, 'Новый пароль должен содержать минимум 8 символов.')
            return render(request, 'users/change_password.html')

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Пароль успешно изменён! Войдите заново.')
        logout(request)
        return redirect('users:login')
    return render(request, 'users/change_password.html')


@login_required
def reset_password(request):
    # Генерация пароля: минимум 12 символов, включая буквы, цифры и спецсимволы
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = (
            random.choice(string.ascii_uppercase) +  # минимум 1 заглавная буква
            random.choice(string.ascii_lowercase) +  # минимум 1 строчная буква
            random.choice(string.digits) +  # минимум 1 цифра
            random.choice(string.punctuation) +  # минимум 1 спецсимвол
            ''.join(random.choice(characters) for _ in range(8))  # остальные символы
    )
    random_password = ''.join(random.sample(random_password, len(random_password)))  # перемешиваем
    request.user.set_password(random_password)
    request.user.save()
    send_mail(
        'Ваш новый пароль',
        f'Привет, {request.user.email}! Ваш новый пароль: {random_password}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )
    messages.success(request, 'Новый пароль отправлен на ваш email! Войдите с новым паролем.')
    logout(request)
    return redirect('users:login')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли!')
    return redirect('blog:pet_list')
