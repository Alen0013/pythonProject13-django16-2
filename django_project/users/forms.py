from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        help_text="Введите ваш email (обязательное поле).",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    password1 = forms.CharField(
        label="Пароль",
        help_text="Пароль должен содержать минимум 8 символов, включая буквы и цифры.",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        help_text="Повторите пароль для подтверждения.",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'})
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        if password1 and len(password1) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов.")
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

    class Meta:
        model = User
        fields = ('email', 'password')


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        help_text="Введите новый email.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        required=False,
        help_text="Введите номер телефона (необязательно).",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'})
    )
    telegram = forms.CharField(
        label="Telegram",
        max_length=100,
        required=False,
        help_text="Введите имя пользователя Telegram (необязательно).",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'telegram')
