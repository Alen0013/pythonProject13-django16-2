from django import forms
from .models import Pet
from datetime import date


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'age', 'birth_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            'species': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите вид'}),
            # Изменили на TextInput
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

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        age = cleaned_data.get('age')

        if birth_date and age:
            today = date.today()
            calculated_age = today.year - birth_date.year - (
                        (today.month, today.day) < (birth_date.month, birth_date.day))
            if calculated_age != age:
                self.add_error(None, "Возраст не соответствует дате рождения.")
        return cleaned_data
