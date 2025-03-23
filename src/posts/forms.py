from typing import Any
from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from posts.models import Post, PostTypes, VisibilityTypes


class CreatePostForm(forms.ModelForm[Post]):
    class Meta:
        model = Post
        fields = ["title", "description", "content", "post_type", "visibility_type", "image"]

    image = forms.ImageField(
        required=False,
        label="Upload Image",
        help_text="Upload an image file"
    )

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

    def clean(self) -> (dict[str, Any] | None):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            post_type = cleaned_data.get("post_type")
            if post_type == PostTypes.IMAGE or post_type == PostTypes.VIDEO:
                cleaned_data["content"] = ""
                if post_type == PostTypes.IMAGE:
                    self.fields["content"].required = False
                    self.fields["image"].required = True
            else:
                cleaned_data["image"] = None
                self.fields["content"].required = True
                self.fields["image"].required = False

        return cleaned_data
