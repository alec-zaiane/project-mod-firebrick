from typing import Any
from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from posts.models import Post, PostTypes, VisibilityTypes


class CreatePostForm(forms.ModelForm[Post]):
    class Meta:
        model = Post
        fields = [
            "title",
            "description",
            "content",
            "post_type",
            "visibility_type",
            "image",
            "video",
        ]

    image = forms.ImageField(
        required=False,
        label="Upload Image",
        help_text="Upload an image file"
    )

    video = forms.FileField(
        required=False,
        label="Upload Video",
        help_text="Optional: Upload a video file (max 4 seconds)",
        widget=forms.FileInput(
            attrs={
                "accept": "video/*",
                "class": "form-control",
            }
        ),
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        post_type = self.data.get("post_type") if self.data else None
        if post_type:
            self.fields["content"].required = post_type == PostTypes.PLAINTEXT or post_type == PostTypes.MARKDOWN
            self.fields["image"].required = post_type == PostTypes.IMAGE
            self.fields["video"].required = post_type == PostTypes.VIDEO

    def clean(self) -> (dict[str, Any] | None):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            post_type = cleaned_data.get("post_type")
            if "content" in cleaned_data:
                cleaned_data["content"] = "" if post_type != PostTypes.PLAINTEXT and post_type != PostTypes.MARKDOWN else cleaned_data["content"]
            if "image" in cleaned_data:
                cleaned_data["image"] = None if post_type != PostTypes.IMAGE else cleaned_data["image"]
            if "video" in cleaned_data:
                cleaned_data["video"] = None if post_type != PostTypes.VIDEO else cleaned_data["video"]

        return cleaned_data
