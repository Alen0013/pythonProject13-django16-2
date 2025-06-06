from django.db import models
from django.core.exceptions import ValidationError
from users.models import User
from datetime import date
import uuid

class Pet(models.Model):
    SPECIES_CHOICES = [
        ('dog', 'Собака'),
        ('cat', 'Кошка'),
        ('bird', 'Птица'),
        ('fish', 'Рыба'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=100, verbose_name='Имя')
    species = models.CharField(max_length=100, choices=SPECIES_CHOICES, verbose_name='Вид')
    age = models.PositiveIntegerField(verbose_name='Возраст')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    moderated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='moderated_pets', verbose_name='Модерирован'
    )
    view_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    def __str__(self):
        return self.name

    def clean(self):
        if self.birth_date:
            today = date.today()
            if self.birth_date > today:
                raise ValidationError('Дата рождения не может быть в будущем.')
            calculated_age = today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if calculated_age < 0:
                raise ValidationError('Дата рождения некорректна.')
            if self.age and abs(calculated_age - self.age) > 1:
                raise ValidationError('Возраст не соответствует дате рождения.')

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'

class Pedigree(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='pedigrees', verbose_name='Питомец')
    parent_type = models.CharField(
        max_length=10,
        choices=[('mother', 'Мать'), ('father', 'Отец')],
        verbose_name='Тип родителя'
    )
    parent_name = models.CharField(max_length=100, verbose_name='Имя родителя')
    breed = models.CharField(max_length=100, blank=True, verbose_name='Порода')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения родителя')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return f"{self.get_parent_type_display()} {self.parent_name} для {self.pet.name}"

    class Meta:
        verbose_name = 'Родословная'
        verbose_name_plural = 'Родословные'

class Review(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='reviews', verbose_name='Питомец')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Оценка',
        default=1
    )
    slug = models.SlugField(max_length=50, unique=True, blank=True, verbose_name='Slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:8]  # Генерируем случайный slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Отзыв от {self.author.email} на {self.pet.name}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'