from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates users with different roles'

    def handle(self, *args, **options):
        users_data = [
            {'email': 'admin@example.com', 'role': 'admin', 'password': 'admin123', 'is_staff': True,
             'is_superuser': True, 'is_active': True},
            {'email': 'moderator@example.com', 'role': 'moderator', 'password': 'mod123', 'is_staff': True,
             'is_superuser': False, 'is_active': True},
            {'email': 'user@example.com', 'role': 'user', 'password': 'user123', 'is_staff': False,
             'is_superuser': False, 'is_active': True},
        ]

        for data in users_data:
            try:
                user, created = User.objects.get_or_create(email=data['email'], defaults={
                    'role': data['role'],
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                    'is_active': data['is_active'],
                })
                if created:
                    user.set_password(data['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Created user: {data["email"]} with role {user.role}, is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}'))
                else:
                    user.role = data['role']
                    user.is_staff = data['is_staff']
                    user.is_superuser = data['is_superuser']
                    user.is_active = data['is_active']
                    user.set_password(data['password'])
                    user.save()
                    self.stdout.write(self.style.WARNING(
                        f'Updated user: {data["email"]} with role {user.role}, is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing user {data["email"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully processed users'))
