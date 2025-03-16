from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext_lazy as _

from user_management.models import JoinRequest


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
    username = forms.CharField(widget=TextInput(
        attrs={'autofocus': True, 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password'}))

    def save(self, commit: bool = True) -> JoinRequest:
        join_request = JoinRequest.objects.create_join_request(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"])

        return join_request
