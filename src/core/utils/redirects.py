from typing import Optional
from django.http import HttpResponseRedirect, HttpRequest
from core.settings import LOGIN_URL
# useful redirects


def REDIRECT_TO_LOGIN(original_request: Optional[HttpRequest] = None) -> HttpResponseRedirect:
    query_params = ""
    if original_request is not None:
        query_params = "?next=" + original_request.path
    return HttpResponseRedirect(LOGIN_URL + query_params)
