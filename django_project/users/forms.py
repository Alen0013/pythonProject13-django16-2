from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')  # Используем email вместо username
        help_texts = {
            'email': 'Введите ваш email.',
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # Заменяем username на email

    class Meta:
        model = User
        fields = ('email', 'password')