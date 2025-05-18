from django.db import models
from users.models import User


class Pet(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    species = models.CharField(max_length=100, verbose_name='Вид')
    age = models.PositiveIntegerField(verbose_name='Возраст')
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'
