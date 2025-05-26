from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import View, UpdateView, TemplateView, ListView, DetailView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

User = get_user_model()

class RegisterView(View):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('blog:pet_list')
        return render(request, self.template_name, {'form': form})

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

class ProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request):
        return render(request, self.template_name)

class UpdateProfileView(UpdateView):
    form_class = UserUpdateForm
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлён!')
        return super().form_valid(form)

class ChangePasswordView(View):
    template_name = 'users/change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'Старый пароль неверный.')
            return render(request, self.template_name)

        if new_password1 != new_password2:
            messages.error(request, 'Новые пароли не совпадают.')
            return render(request, self.template_name)

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Пароль успешно изменён!')
        login(request, request.user)
        return redirect('users:profile')

class ResetPasswordView(View):
    template_name = 'users/reset_password_confirm.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(new_password)
        user.save()

        send_mail(
            'Ваш новый пароль',
            f'Ваш новый пароль: {new_password}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, 'Новый пароль отправлен на ваш email.')
        return redirect('users:profile')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/reset_password.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:login')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/reset_password_confirm.html'
    success_url = reverse_lazy('users:login')

class LogoutView(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('blog:pet_list')

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.role in ['admin', 'moderator']

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для просмотра списка пользователей!')
        return redirect('blog:pet_list')

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

    def test_func(self):
        return self.request.user.role in ['admin', 'moderator'] or self.request.user == self.get_object()

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для просмотра этого профиля!')
        return redirect('blog:pet_list')