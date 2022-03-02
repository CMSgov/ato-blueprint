from django import forms
from django.forms import ModelForm

from .models import Package


class PackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ["title", "acronym", "impact_level", "location"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'usa-input'}),
            'acronym': forms.TextInput(attrs={'class': 'usa-input'}),
            'location': forms.RadioSelect(attrs={'class': 'usa-radio__input usa-radio__input--tile'}),
            'impact_level': forms.RadioSelect(attrs={'class': 'usa-radio__input usa-radio__input--tile'})
        }
