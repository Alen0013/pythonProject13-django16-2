from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print(f"Created user: {email}, role={user.role}, is_staff={user.is_staff}, is_superuser={user.is_superuser}")
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'Обычный пользователь'),
            ('moderator', 'Модератор'),
            ('admin', 'Администратор'),
        ],
        default='user'
    )
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_role_display(self):
        return dict(self._meta.get_field('role').choices).get(self.role, 'Не определено')
