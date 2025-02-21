from django import forms
from .models import PostTextBased

class PostTextBasedForm(forms.ModelForm):
    class Meta:
        model = PostTextBased
        fields = ["content", "post_type", "visibility_type"]
