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
import random
import string

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
            user = form.save(commit=False)
            # Генерируем случайный пароль
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.set_password(random_password)
            user.save()
            login(request, user)
            # Отправка email с случайным паролем на email пользователя
            subject = 'Добро пожаловать в наш сервис!'
            message = f'Здравствуйте, {user.email}!\n\nВы успешно зарегистрированы на нашем сайте.\nВаши учетные данные:\nEmail: {user.email}\nВаш случайный пароль: {random_password}\n\nСохраните этот пароль или измените его в профиле.\nС уважением,\nКоманда сайта'
            from_email = settings.EMAIL_HOST_USER  # Отправляется от lachenil@yandex.ru
            recipient_list = [user.email]  # Отправка на email пользователя
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, f'Регистрация прошла успешно! Пароль отправлен на {user.email}.')
            except Exception as e:
                messages.error(request, f'Ошибка отправки email: {str(e)}. Пароль: {random_password}')
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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/reset_password.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            subject = 'Сброс пароля'
            message = f'Здравствуйте, {user.email}!\n\nВы запросили сброс пароля. Перейдите по ссылке для создания нового пароля:\n{self.request.build_absolute_uri(reverse_lazy("users:password_reset_confirm", kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": default_token_generator.make_token(user)}))}\n\nЕсли это были не вы, проигнорируйте это письмо.\nС уважением,\nКоманда сайта'
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                messages.success(self.request, f'Ссылка для сброса пароля отправлена на {email}.')
            except Exception as e:
                messages.error(self.request, f'Ошибка отправки email: {str(e)}.')
        else:
            messages.error(self.request, 'Пользователь с таким email не найден.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/reset_password_confirm.html'
    success_url = reverse_lazy('users:login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('blog:pet_list')


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 5


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
