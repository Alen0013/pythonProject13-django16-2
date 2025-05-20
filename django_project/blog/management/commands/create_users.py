from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates users with different roles'

    def handle(self, *args, **options):
        users_data = [
            {'email': 'admin@example.com', 'role': 'admin', 'password': 'admin123', 'is_staff': True,
             'is_superuser': True},
            {'email': 'moderator@example.com', 'role': 'moderator', 'password': 'mod123', 'is_staff': True,
             'is_superuser': False},
            {'email': 'user@example.com', 'role': 'user', 'password': 'user123', 'is_staff': False,
             'is_superuser': False},
        ]

        for data in users_data:
            try:
                user, created = User.objects.get_or_create(email=data['email'], defaults={
                    'role': data['role'],
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                })
                if created:
                    user.set_password(data['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Created user: {data["email"]} with role {user.role}, is_staff={user.is_staff}, is_superuser={user.is_superuser}'))
                else:
                    # Обновляем существующего пользователя
                    user.role = data['role']
                    user.is_staff = data['is_staff']
                    user.is_superuser = data['is_superuser']
                    user.set_password(data['password'])
                    user.save()
                    self.stdout.write(self.style.WARNING(
                        f'Updated user: {data["email"]} with role {user.role}, is_staff={user.is_staff}, is_superuser={user.is_superuser}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing user {data["email"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully processed users'))
