from django import forms
from .models import Genre

class GenreForm(forms.Form):
    name = forms.CharField(label="Genre", max_length=200)