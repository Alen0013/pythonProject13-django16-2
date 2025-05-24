from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        help_text=_("Enter your email (required)."),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    password1 = forms.CharField(
        label=_("Password"),
        help_text=_("Password must be at least 8 characters, including letters and numbers."),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter password')})
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        help_text=_("Repeat the password for confirmation."),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm password')})
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords do not match."))
        if password1 and len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters."))
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.clear()
        self.fields['email'] = forms.EmailField(
            label=_("Email"),
            max_length=254,
            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
        )
        self.fields['password'] = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter password')})
        )
        self.username_field = User._meta.get_field('email')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _("Invalid email or password."),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        help_text=_("Enter new email."),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    phone = forms.CharField(
        label=_("Phone"),
        max_length=20,
        required=False,
        help_text=_("Enter phone number (optional)."),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'})
    )
    telegram = forms.CharField(
        label=_("Telegram"),
        max_length=100,
        required=False,
        help_text=_("Enter Telegram username (optional)."),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'telegram')
