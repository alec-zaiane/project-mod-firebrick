from typing import Optional
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse


# useful redirects


def REDIRECT_TO_LOGIN(original_request: Optional[HttpRequest] = None) -> HttpResponseRedirect:
    query_params = ""
    if original_request is not None:
        query_params = "?next=" + original_request.path
    return HttpResponseRedirect(reverse("user_management:login") + query_params)
