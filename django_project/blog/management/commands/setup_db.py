from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Sets up the database by running migrations and creating initial users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database setup...'))

        # Шаг 1: Создание миграций
        self.stdout.write('Creating migrations...')
        try:
            call_command('makemigrations', interactive=False)
            self.stdout.write(self.style.SUCCESS('Migrations created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating migrations: {e}'))
            return

        # Шаг 2: Применение миграций
        self.stdout.write('Applying migrations...')
        try:
            call_command('migrate', interactive=False)
            self.stdout.write(self.style.SUCCESS('Migrations applied successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error applying migrations: {e}'))
            return

        # Шаг 3: Создание суперпользователя
        self.stdout.write('Creating superuser...')
        try:
            call_command('createsuperuser', interactive=True)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating superuser: {e}. Skipping...'))

        # Шаг 4: Создание пользователей с разными ролями
        self.stdout.write('Creating users with different roles...')
        try:
            call_command('create_users')
            self.stdout.write(self.style.SUCCESS('Users created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating users: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('Database setup completed successfully!'))
