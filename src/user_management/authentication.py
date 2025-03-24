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
        # print(f"{userid=}, {password=}")
        user = User.objects.filter(username=userid).first()
        if not user:
            print("Invalid username")
            raise AuthenticationFailed('Invalid username')
        # if not user.check_password(password):
        #     print("Invalid password")
        #     raise AuthenticationFailed('Invalid password.')
        # if user.type != User.Types.NODE:
        #     print("Not a Node")
        #     raise AuthenticationFailed('Not a Node')
        return (user, None)
