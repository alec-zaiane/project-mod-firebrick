from typing import Optional
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse


from rest_framework.response import Response
from rest_framework.request import Request

from core.settings import LOGIN_URL
# useful redirects or canned responses


def REDIRECT_TO_LOGIN(original_request: Optional[HttpRequest] = None) -> HttpResponseRedirect:
    query_params = ""
    if original_request is not None:
        query_params = "?next=" + original_request.path
    return HttpResponseRedirect(LOGIN_URL + query_params)


def API_UNAUTHORIZED() -> Response:
    return Response({"error": "Authentication required."}, status=401)


def API_FORBIDDEN() -> Response:
    return Response({"error": "You do not have permission to perform this action."}, status=403)
