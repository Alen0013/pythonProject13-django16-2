from django import forms
from .models import Pet


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ('name', 'species', 'age', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
