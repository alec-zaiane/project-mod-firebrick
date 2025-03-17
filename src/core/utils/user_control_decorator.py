from typing import Callable, Any, Optional
import inspect

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from user_management.models import Author
from django.urls import reverse

from rest_framework.request import Request
from rest_framework.response import Response


# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments, accessed 2025-02-15


# Useful fail responses:
REDIRECT_TO_LOGIN = HttpResponseRedirect(reverse("user_management:login"))


class UserControlException(Exception):
    def __init__(self, response: HttpResponse | Response):
        super().__init__("User control custom exception, if you see this, you probably want to use the @user_controller decorator on the containing view")
        self.response = response


def user_control(request: HttpRequest | Request, must_be_logged_in: bool = False, must_be_author: bool = False, must_be_superuser: bool = False, fail_response: Optional[HttpResponse | Response] = None, verify_true: bool = True) -> None:
    """Control what kind of user can access a view
    **Important: use only inside a function wrapped with `@user_controller`**


    Example usage:
    ```python
    @user_controller(must_be_logged_in=True)
    def my_view(request: HttpRequest):
        if some_condition:
            user_control(request, must_be_author=True)
            do_something()
        else:
            do_something_else()
    ```

    Example usage with verify_true:
    ```python
    @user_controller(must_be_logged_in=True, must_be_author=True)
    def my_view(request: HttpRequest, viewer: Optional[LocalAuthor] = None):
        post_in_question = get_post_in_question_somehow()
        viewer_is_author = viewer is not None and viewer == post_in_question.author
        # make sure the viewer is the author of the post
        user_control(request, verify_true=viewer_is_author)
        # rest of code here ...
        return xyz
    ```


    Args:
        request (HttpRequest | Request): the request object from the view/api view
        must_be_logged_in (bool, optional): Whether the user must be logged in to pass this check. Defaults to False.
        must_be_author (bool, optional): Whether the user must be an author to pass this check. Defaults to False.
        must_be_superuser (bool, optional): Whether the user must be a superuser to pass this check. Defaults to False.
        fail_response: The response to return if the user fails the check. Default behaviour is outlined below. Defaults to None.
        verify_true (bool, optional): Automatically fail if this is false. Defaults to True.
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

    # 0: check verify_true
    if not verify_true:
        raise UserControlException(fail_response)
    if not hasattr(request, "user"):
        raise UserControlException(fail_response)

    # 1: check `must_be_logged_in`
    if must_be_logged_in and not request.user.is_authenticated:
        raise UserControlException(fail_response)

    # fetch author information for future checks
    viewer = Author.local_authors.find_author_with_user(
        request.user) if request.user.is_authenticated else None
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
            found_viewer = Author.local_authors.find_author_with_user(
                request.user) if request.user.is_authenticated else None

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
