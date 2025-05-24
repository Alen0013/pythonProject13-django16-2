from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.generic import CreateView, FormView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm
from .models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('blog:pet_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        send_mail(
            _('Welcome!'),
            _(f'Hello, {user.email}! Your account has been successfully created.'),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(self.request, _('Registration successful! Confirmation email sent.'))
        return super().form_valid(form)


class UserLoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('blog:pet_list')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, _('You have successfully logged in!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, _(f"Error in field '{form[field].label}': {error}"))
        return self.render_to_response(self.get_context_data(form=form))


class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):
        return render(request, self.template_name, {'user': request.user})


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Profile successfully updated!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, _(f"Error in field '{form[field].label}': {error}"))
        return self.render_to_response(self.get_context_data(form=form))


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'users/change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, _('Invalid current password.'))
            return render(request, self.template_name)

        if new_password1 != new_password2:
            messages.error(request, _('New passwords do not match.'))
            return render(request, self.template_name)

        if len(new_password1) < 8:
            messages.error(request, _('New password must be at least 8 characters long.'))
            return render(request, self.template_name)

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, _('Password successfully changed! Please log in again.'))
        logout(request)
        return redirect('users:login')


class ResetPasswordView(LoginRequiredMixin, View):
    template_name = 'users/reset_password_confirm.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = (
                random.choice(string.ascii_uppercase) +
                random.choice(string.ascii_lowercase) +
                random.choice(string.digits) +
                random.choice(string.punctuation) +
                ''.join(random.choice(characters) for _ in range(8))
        )
        random_password = ''.join(random.sample(random_password, len(random_password)))
        request.user.set_password(random_password)
        request.user.save()
        send_mail(
            _('Your new password'),
            _(f'Hello, {request.user.email}! Your new password: {random_password}'),
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        messages.success(request, _('New password sent to your email! Log in with the new password.'))
        logout(request)
        return redirect('users:login')


class UserLogoutView(View):
    template_name = 'users/logout.html'

    def get(self, request):
        logout(request)
        messages.success(request, _('You have successfully logged out!'))
        return render(request, self.template_name)
