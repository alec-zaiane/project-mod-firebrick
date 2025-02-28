from typing import Callable, Any, Optional
import inspect

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from socialnetwork.models import LocalAuthor
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.request import Request
from rest_framework.response import Response

from warnings import deprecated

# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments, accessed 2025-02-15


@deprecated("use the `user_controller` decorator and `user_control` function instead")
def user_control_deprecated(must_be_logged_in: bool = False, must_be_author: bool = False, must_be_superuser: bool = False, redirect_url: Optional[str] = None) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
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
                    FAILURE_RESPONSE = Response(status=403)
                else:
                    FAILURE_RESPONSE = Response(status=401)
            else:
                if redirect_url is not None:
                    FAILURE_RESPONSE = HttpResponseRedirect(redirect_url)
                else:
                    # FAILURE_RESPONSE = HttpResponseRedirect(reverse("socialnetwork:unauthorized")) TODO implement this
                    FAILURE_RESPONSE = HttpResponseRedirect("/")

            # 1: check `must_be_logged_in`
            if must_be_logged_in and not request.user.is_authenticated:
                return HttpResponseRedirect(reverse("socialnetwork:not_logged_in")) if not IS_API else FAILURE_RESPONSE

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


class UserControlException(Exception):
    def __init__(self, response: HttpResponse | Response):
        super().__init__("User control custom exception, if you see this, you probably want to use the @user_controller decorator on the containing view")
        self.response = response


def user_control(request: HttpRequest | Request, must_be_logged_in: bool = False, must_be_author: bool = False, must_be_superuser: bool = False, fail_response: Optional[HttpResponse | Response] = None) -> None:
    """Control what kind of user can access a view
    **Important: use only inside a function wrapped with `@user_controller`**

    Args:
        request (HttpRequest | Request): the request object from the view/api view
        must_be_logged_in (bool, optional): Whether the user must be logged in to pass this check. Defaults to False.
        must_be_author (bool, optional): Whether the user must be an author to pass this check. Defaults to False.
        must_be_superuser (bool, optional): Whether the user must be a superuser to pass this check. Defaults to False.
        fail_response: The response to return if the user fails the check. Default behaviour is outlined below. Defaults to None.
    """
    # figure out if this is a DRF call or not
    IS_DRF = isinstance(request, Request)

    # Get the default failure response
    # If this is an API call, the default is 401 if not logged in, 403 if logged in
    # If this is a website call, the default is a redirect to the login page, or a redirect to the unauthorized page if the user is logged in
    if fail_response is None:
        if IS_DRF:
            fail_response = Response(status=401)
            if hasattr(request, "user") and request.user.is_authenticated:
                fail_response = Response(status=403)
        else:
            fail_response = HttpResponseRedirect(
                reverse("socialnetwork:not_logged_in"))
            if hasattr(request, "user") and request.user.is_authenticated:
                fail_response = HttpResponseRedirect(
                    reverse("socialnetwork:unauthorized"))

    if not hasattr(request, "user"):
        raise UserControlException(fail_response)

    # 1: check `must_be_logged_in`
    if must_be_logged_in and not request.user.is_authenticated:
        raise UserControlException(fail_response)

    # fetch author information for future checks
    viewer_query = LocalAuthor.objects.filter(
        user=request.user) if isinstance(request.user, User) else None
    viewer = viewer_query.first() if viewer_query is not None and viewer_query.exists() else None
    viewer_is_author = viewer is not None
    viewer_is_superuser = request.user.is_superuser

    # 2: check `must_be_author`
    if must_be_author and not viewer_is_author:
        raise UserControlException(fail_response)

    # 3: check `must_be_superuser`
    if must_be_superuser and not viewer_is_superuser:
        raise UserControlException(fail_response)

    # all done :) don't raise an exception


def user_controller(must_be_logged_in: bool = False, must_be_author: bool = False, must_be_superuser: bool = False, fail_response: Optional[HttpResponse | Response] = None) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Decorator for any views that require user control
    **Important: see user_control for argument information, they are the same**
    **Important: add a `viewer:Optional[LocalAuthor]=None` kwarg to your view if you want to access the viewer's `LocalAuthor` object if they have one**
    All restrictions on the decorator are applied before the view is called, but more specific checks can be done inside the view

    example:
    ```python
    @user_controller(must_be_logged_in=True)
    def foo_view(request:HttpRequest) -> HttpResponse:
        if some_condition:
            user_control(request, must_be_author=True)
            do_something()
        else:
            do_something_else()
    ```
    This works the same for DRF api views
    """
    def wrap(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        def wrapped_f(request: HttpRequest | Request, *args: list[Any], **kwargs: dict[str, Any]) -> HttpResponse | Response:
            found_viewer = None
            if hasattr(request, "user") and request.user.is_authenticated:
                viewer_query = LocalAuthor.objects.filter(
                    user=request.user)
                if viewer_query.exists():
                    found_viewer = viewer_query.first()

            signature = inspect.signature(func)
            expects_viewer = "viewer" in signature.parameters

            # run the control checks and the function
            try:
                user_control(request, must_be_logged_in=must_be_logged_in,
                             must_be_author=must_be_author, must_be_superuser=must_be_superuser, fail_response=fail_response)
                if expects_viewer:
                    return func(request, viewer=found_viewer, *args, **kwargs)
                else:
                    return func(request, *args, **kwargs)

            except UserControlException as e:
                return e.response

        return wrapped_f

    return wrap
