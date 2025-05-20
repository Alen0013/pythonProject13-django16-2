from django import forms
from .models import Pet
from datetime import date
import re


class PetForm(forms.ModelForm):
    species = forms.ChoiceField(
        choices=[('', '---------')] + Pet.SPECIES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Pet
        fields = ['name', 'species', 'age', 'birth_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите возраст'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите описание'}),
        }
        labels = {
            'name': 'Имя',
            'species': 'Вид',
            'age': 'Возраст',
            'birth_date': 'Дата рождения',
            'description': 'Описание',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Имя не может быть пустым.")
        if not re.match(r'^[a-zA-Zа-яА-Я\s-]+$', name):
            raise forms.ValidationError("Имя может содержать только буквы, пробелы и дефисы.")
        return name

    def clean_species(self):
        species = self.cleaned_data.get('species')
        if not species:
            raise forms.ValidationError("Вид не может быть пустым.")
        if species not in dict(Pet.SPECIES_CHOICES).keys():
            raise forms.ValidationError("Выберите вид из списка.")
        return species

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Возраст обязателен.")
        if age <= 0:
            raise forms.ValidationError("Возраст должен быть положительным числом.")
        if age > 100:
            raise forms.ValidationError("Возраст не может быть больше 100 лет.")
        return age

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise forms.ValidationError("Дата рождения не может быть в будущем.")
        return birth_date

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        age = cleaned_data.get('age')

        if birth_date and age:
            today = date.today()
            calculated_age = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day))
            if calculated_age != age:
                self.add_error(None,
                               f"Возраст ({age}) не соответствует дате рождения ({birth_date}). Рассчитанный возраст: {calculated_age}.")
        return cleaned_data
