from django.db import models
from django.core.exceptions import ValidationError
from users.models import User
from datetime import date


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

