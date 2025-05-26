from django.core.management.base import BaseCommand
from blog.models import Pet
from users.models import User


class Command(BaseCommand):
    help = 'Adds test pets to the database'

    def handle(self, *args, **options):
        owner = User.objects.first()
        if not owner:
            self.stdout.write(self.style.ERROR('No users found. Create a superuser first.'))
            return

        pets_data = [
            {'name': 'Рекс', 'species': 'dog', 'age': 3, 'description': 'Добрый и игривый пес', 'is_active': True},
            {'name': 'Мурка', 'species': 'cat', 'age': 2, 'description': 'Спокойная кошка', 'is_active': True},
            {'name': 'Буцефал', 'species': 'bird', 'age': 1, 'description': 'Говорящий попугай', 'is_active': True},
        ]

        for pet_data in pets_data:
            Pet.objects.get_or_create(
                name=pet_data['name'],
                species=pet_data['species'],
                age=pet_data['age'],
                description=pet_data['description'],
                owner=owner,
                is_active=pet_data['is_active']
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added pet: {pet_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully added test pets'))
