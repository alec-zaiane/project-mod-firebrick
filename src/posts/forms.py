from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from posts.models import Post, PostTypes, VisibilityTypes
from user_management.models import Author


class CreatePostForm(forms.ModelForm[Post]):
    class Meta:
        model = Post
        fields = ["title", "description", "content", "post_type", "visibility_type"]

    title = forms.CharField(error_messages={
        "required": "Please provide a title.",
    }, widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Title'}))
    description = forms.CharField(required=False, widget=TextInput(
        attrs={'placeholder': 'Description'}))
    content = forms.CharField(error_messages={
        "required": "Please provide content.",
    }, widget=forms.Textarea(
        attrs={'placeholder': 'Content'}))

    post_type = forms.ChoiceField(error_messages={
        "required": "Please choose a post type.",
    }, choices=PostTypes.choices)

    visibility_type = forms.ChoiceField(error_messages={
        "required": "Please choose a visibility type.",
    }, choices=VisibilityTypes.choices)
