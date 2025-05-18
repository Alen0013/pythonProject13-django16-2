from django.core.management.base import BaseCommand
from blog.models import Pet
from users.models import User  # Кастомная модель пользователя


class Command(BaseCommand):
    help = 'Adds test pets to the database'

    def handle(self, *args, **options):
        owner = User.objects.first()
        if not owner:
            self.stdout.write(self.style.ERROR('No users found. Create a superuser first.'))
            return

        pets_data = [
            {'name': 'Рекс', 'species': 'Собака', 'age': 3, 'description': 'Добрый и игривый пес'},
            {'name': 'Мурка', 'species': 'Кот', 'age': 2, 'description': 'Спокойная кошка'},
            {'name': 'Буцефал', 'species': 'Попугай', 'age': 1, 'description': 'Говорящий попугай'},
        ]

        for pet_data in pets_data:
            Pet.objects.get_or_create(
                name=pet_data['name'],
                species=pet_data['species'],
                age=pet_data['age'],
                description=pet_data['description'],
                owner=owner
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added pet: {pet_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully added test pets'))
