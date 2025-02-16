from typing import Callable, Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import decorators
from socialnetwork.models import Author
from django.urls import reverse
from django.contrib.auth.models import User




# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments, accessed 2025-02-15

def user_control(can_be_author:bool=True, can_be_logged_out:bool=False, can_be_superuser:bool=False):
    """Control what kind of user can access a view
    If can_be_author is True, the view will be passed an author object with `author=` as a keyword
    
    One of the arguments must be True, otherwise the decorator will raise a ValueError
    If the user is logged in, but not a superuser or author, a ValueError will be raised (this should never happen)
    

    Args:
        can_be_author (bool, optional): Whether authors can view this (otherwise they will be redirected to their stream). Defaults to True.
        can_be_logged_out (bool, optional): Whether logged out people can view this (otherwise they will be redirected to login page). Defaults to False.
        can_be_superuser (bool, optional): Whether superusers can view this (otherwise they will be redirected to admin panel). Defaults to False.
    """     
    def wrap(func:Callable[..., HttpResponse]):
        if (not can_be_author) and (not can_be_logged_out) and (not can_be_superuser):
            raise ValueError("At least one of can_be_author, can_be_logged_out, or can_be_superuser must be True")
        
        def wrapped_f(request:HttpRequest, *args:list[Any], **kwargs:dict[str,Any]) -> HttpResponse:
            if not request.user.is_authenticated:
                if can_be_logged_out:
                    return func(request, *args, **kwargs)
                return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))
            if isinstance(request.user, User) and request.user.is_superuser:
                if can_be_superuser:
                    return func(request, *args, **kwargs)
                return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
            if isinstance(request.user, Author):
                if can_be_author:
                    return func(request, author=request.user, *args, **kwargs)
                return HttpResponseRedirect(reverse("socialnetwork:stream"))
            raise ValueError("An unhandled user type was found: "+str(type(request.user)))
        return wrapped_f

    return wrap