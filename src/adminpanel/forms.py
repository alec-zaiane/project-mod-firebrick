from django import forms
from .models import HostedImage

class HostedImageForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = HostedImage
        fields = ['title', 'image']

