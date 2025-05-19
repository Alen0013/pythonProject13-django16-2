from django import forms
from .models import Pet


class PetForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Дата рождения',
        required=False,
        help_text='Введите дату рождения питомца (например, 2020-01-01).'
    )

    class Meta:
        model = Pet
        fields = ('name', 'species', 'age', 'birth_date', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'species': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
