from typing import Optional

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from user_management.models import User

# Suggested by Copilot "@workspace how can I enable http basic auth for Users where user.type == User.Types.NODE?"
# Claude 3.7 Sonnet Thinking (Preview) on 2025-03-23


class NodeUserBasicAuthentication(authentication.BasicAuthentication):
    """
    Allow HTTP Basic Authentication for **Nodes only** (Users where user.type == User.Types.NODE)
    """

    def authenticate_credentials(self, userid: str, password: str, request: Optional[Request] = None) -> tuple[User, None]:
        user = User.objects.filter(username=userid).first()
        if not user:
            raise AuthenticationFailed('Invalid username/password.')
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid username/password.')
        if user.type != User.Types.NODE:
            raise AuthenticationFailed('Invalid username/password.')
        return (user, None)
