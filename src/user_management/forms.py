from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext_lazy as _

from user_management.models import Author, JoinRequest


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'current-password',
                                                           'placeholder': 'Password'}))


class JoinRequestForm(forms.ModelForm[JoinRequest]):
    class Meta:
        model = JoinRequest
        fields = ["username", "password"]

    # Greater specification to fields, mostly for placeholder text
    username = forms.CharField(error_messages={
        "required": "Please provide a username.",
    }, widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Username'}))
    password = forms.CharField(error_messages={
        "required": "Please provide a password.",
    }, widget=PasswordInput(attrs={'placeholder': 'Password'}))

    def save(self, commit: bool = True) -> JoinRequest:
        join_request = JoinRequest.objects.create_join_request(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"])

        return join_request


class AuthorModifyForm(forms.ModelForm[Author]):
    class Meta:
        model = Author
        fields = ["username", "display_name", "profile_image", "bio"]

    username = forms.CharField(error_messages={
        "required": "Please provide a username.",
    }, widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Username'}))
    display_name = forms.CharField(error_messages={
        "required": "Please provide a display name.",
    }, widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Display Name'}))
    profile_image = forms.URLField(required=False, error_messages={
        "invalid": "Please provide a valid Profile Image URL.",
    }, widget=TextInput(
        attrs={'placeholder': 'Profile Image URL'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'placeholder': 'Author Bio'}))
