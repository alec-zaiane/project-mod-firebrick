from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext_lazy as _
import requests
from requests.auth import HTTPBasicAuth

from user_management.models import Author, JoinRequest, Node, User


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


class NodeAdminForm(forms.ModelForm[Node]):
    class Meta:
        model = Node
        fields = ["name", "host_url", "host_site_url", "is_local_node", "is_disabled"]

    is_local_node = forms.BooleanField(
        required=False,
        label="Is Local Node",
        initial=False,
    )
    is_disabled = forms.BooleanField(
        required=False,
        label="Is Disabled",
        initial=False,
    )

    name = forms.CharField(error_messages={
        "required": "Please provide a name.",
    }, widget=TextInput(
        attrs={'autofocus': True}))
    host_url = forms.URLField(error_messages={
        "invalid": "Please provide a valid Host URL.",
        "required": "Please provide a host URL.",
    }, help_text="Link to the API endpoint of the remote node. Include http:// or https://. Do not have a trailing slash. Example: http://website.com/api",)
    host_site_url = forms.URLField(required=False)
    internal_username = forms.CharField(label="Remote Node Username")
    internal_password = forms.CharField(label="Remote Node Password")
    external_username = forms.CharField(required=False, label="Local Username")
    external_password = forms.CharField(required=False, label="Local Password")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """On initialization, append the username and password of existing users."""
        super().__init__(*args, **kwargs)

        if self.instance:
            internal_user = getattr(self.instance, "internal_user", None)
            if internal_user:
                self.fields["internal_username"].initial = internal_user.username
                self.fields["internal_password"].initial = internal_user.password_plain
            external_user = getattr(self.instance, "external_user", None)
            if external_user:
                self.fields["external_username"].initial = external_user.username
                self.fields["external_password"].initial = external_user.password_plain

    def clean(self) -> dict[str, Any] | None:
        """On clean, check if the username and password are already in use. If they are, update the user. If not, create a new user."""
        cleaned_data = super().clean()
        internal_username = self.cleaned_data.get("internal_username")
        internal_password = self.cleaned_data.get("internal_password")
        external_username = self.cleaned_data.get("external_username")
        external_password = self.cleaned_data.get("external_password")
        external_user = self.instance.external_user
        internal_user = self.instance.internal_user
        commit = False

        if self.instance.external_user and external_username and external_password and external_user:
            # If the node already has a user, update it
            external_user.username = external_username
            external_user.set_password(external_password)
            external_user.password_plain = external_password
            self.instance.external_user = external_user
            commit = True
        elif User.objects.filter(username=external_username).exists():
            # If this is pointing to a user that already exists, update that user
            external_user = User.objects.get(username=external_username)
            external_user.set_password(external_password)
            external_user.password_plain = external_password
            self.instance.external_user = external_user
            commit = True
        elif external_username and external_password:
            # Finally, if none of the above are true, create a user
            external_user = User.objects.create_user(
                username=external_username,
                password=external_password,
                password_plain=external_password,
                type=User.Types.NODE,
            )
            self.instance.external_user = external_user
            commit = True

        if self.instance.internal_user and internal_username and internal_password and internal_user:
            # If the node already has a user, update it
            internal_user.username = internal_username
            internal_user.set_password(internal_password)
            internal_user.password_plain = internal_password
            self.instance.internal_user = internal_user
            commit = True
        elif User.objects.filter(username=internal_username).exists():
            # If this is pointing to a user that already exists, update that user
            internal_user = User.objects.get(username=internal_username)
            internal_user.set_password(internal_password)
            internal_user.password_plain = internal_password
            self.instance.internal_user = internal_user
            commit = True
        elif internal_username and internal_password:
            # Finally, if none of the above are true, create a user
            internal_user = User.objects.create_user(
                username=internal_username,
                password=internal_password,
                password_plain=internal_password,
                type=User.Types.NODE,
            )
            self.instance.internal_user = internal_user
            commit = True
        else:
            # If no username or password is provided, raise an error
            raise forms.ValidationError(
                _("Please provide a valid username and password."))

        host_url = self.cleaned_data.get("host_url")

        if host_url and internal_username and internal_password:
            try:
                response = Node.external_nodes.verify_connection(
                    host_url, internal_username, internal_password)
            except requests.exceptions.RequestException as e:
                response = requests.Response()
                response.status_code = 500
                response.reason = str(e)
                response._content = b""
            if not response.ok:
                commit = False
                error = "The provided host URL is not reachable. " + \
                    str(response.status_code) + " " + response.reason + ": "
                try:
                    error_data = response.json()
                    error_messages = ""
                    for key, value in error_data.items():
                        message = ", ".join(value) if isinstance(value, list) else value
                        error_messages += f"{message} "
                    error_messages = error_messages.strip()
                    error += error_messages
                except ValueError:
                    pass  # If the response is not JSON, just use the status code and reason
                raise forms.ValidationError(
                    _(error))

        else:
            raise forms.ValidationError(
                _("Please provide a valid host URL and credentials."))

        # Only save the user and instance if the form is valid
        if commit:
            if external_user:
                external_user.save()
            if internal_user:
                internal_user.save()
            self.instance.save()

        return cleaned_data
