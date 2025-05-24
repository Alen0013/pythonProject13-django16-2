from django import forms
from .models import Pet
from datetime import date
import re
from django.utils.translation import gettext_lazy as _


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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter name')}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter age')}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter description')}),
        }
        labels = {
            'name': _('Name'),
            'species': _('Species'),
            'age': _('Age'),
            'birth_date': _('Birth Date'),
            'description': _('Description'),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError(_('Name cannot be empty.'))
        if not re.match(r'^[a-zA-Zа-яА-Я\s-]+$', name):
            raise forms.ValidationError(_('Name can only contain letters, spaces, and hyphens.'))
        return name

    def clean_species(self):
        species = self.cleaned_data.get('species')
        if not species:
            raise forms.ValidationError(_('Species cannot be empty.'))
        if species not in dict(Pet.SPECIES_CHOICES).keys():
            raise forms.ValidationError(_('Choose a species from the list.'))
        return species

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError(_('Age is required.'))
        if age <= 0:
            raise forms.ValidationError(_('Age must be a positive number.'))
        if age > 100:
            raise forms.ValidationError(_('Age cannot be more than 100 years.'))
        return age

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise forms.ValidationError(_('Birth date cannot be in the future.'))
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
                               _(f"Age ({age}) does not match birth date ({birth_date}). Calculated age: {calculated_age}."))
        return cleaned_data
