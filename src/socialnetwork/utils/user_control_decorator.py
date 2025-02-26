from typing import Callable, Any, Optional
import inspect

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from socialnetwork.models import LocalAuthor
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.request import Request
from rest_framework.response import Response


# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments, accessed 2025-02-15

def user_control(must_be_logged_in: bool = False, must_be_author: bool = False, must_be_superuser: bool = False, redirect_url: Optional[str] = None) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Control what kind of user can access a view\n
    **Important: the viewer's `Author` object will be passed into the wrapped functions with the `viewer=` kwarg. Make sure your view has this parameter if you want it**
        - i.e: `def foo(bar, viewer:Optional[LocalAuthor]=None, baz) -> ...

    Default behaviour is to allow access from anyone


    Evaluation:
    - if the user is not logged in, `must_be_logged_in` is the only parameter that counts


    Raises: (none of these should ever happen)
        ValueError: If an unhandled user type was found
        AssertionError: If the user has an author attribute that is not an Author object

    Args:
        must_be_logged_in (bool, optional): whether the viewer must be logged in. Defaults to False
        must_be_author (bool, optional): whether the viewer must be an author. Defaults to False
        must_be_superuser (bool, optional): whether the viewer must be a superuser. Defaults to False
        redirect_url (Optional[str], optional): If not None, any *website requests* will serve a redirect to this URL, API requests are unaffected. Defaults to None.
    """
    def wrap(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        def wrapped_f(request: HttpRequest | Request, *args: list[Any], **kwargs: dict[str, Any]) -> HttpResponse | Response:
            IS_API = isinstance(request, Request)

            if not hasattr(request, "user"):
                if IS_API:
                    return Response("Make sure to include a `user` with your request", 401)
                return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))

            FAILURE_RESPONSE: HttpResponse | Response
            if IS_API:
                if request.user.is_authenticated:
                    FAILURE_RESPONSE = Response(403)
                else:
                    FAILURE_RESPONSE = Response(401)
            else:
                if redirect_url is not None:
                    FAILURE_RESPONSE = HttpResponseRedirect(redirect_url)
                else:
                    # FAILURE_RESPONSE = HttpResponseRedirect(reverse("socialnetwork:unauthorized")) TODO implement this
                    FAILURE_RESPONSE = HttpResponseRedirect("/")

            # 1: check `must_be_logged_in`
            if must_be_logged_in and not request.user.is_authenticated:
                return FAILURE_RESPONSE

            # fetch author information for future checks

            viewer_query = LocalAuthor.objects.filter(
                user=request.user) if isinstance(request.user, User) else None
            viewer = viewer_query.first() if viewer_query is not None and viewer_query.exists() else None
            viewer_is_author = viewer is not None
            viewer_is_superuser = request.user.is_superuser

            # 2: check `must_be_author`
            if must_be_author and not viewer_is_author:
                return FAILURE_RESPONSE

            # 3: check `must_be_superuser`
            if must_be_superuser and not viewer_is_superuser:
                return FAILURE_RESPONSE

            # :) all done checks, now we can call the function, but first:
            # decide whether or not to pass in the viewer kwarg
            # https://stackoverflow.com/questions/15638706/listing-variables-expected-by-a-function-in-python, https://docs.python.org/3/library/inspect.html
            signature = inspect.signature(func)
            if "viewer" in signature.parameters:
                return func(request, viewer=viewer, *args, **kwargs)
            else:
                return func(request, *args, **kwargs)

        return wrapped_f

    return wrap
