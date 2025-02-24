from typing import Callable, Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import decorators
from socialnetwork.models import LocalAuthor
from django.urls import reverse
from django.contrib.auth.models import User




# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments, accessed 2025-02-15

def user_control(can_be_author:bool=True, can_be_logged_out:bool=False, can_be_superuser:bool=False, superuser_requires_author:bool=False) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Control what kind of user can access a view\n
    **Important: If can_be_author is True, the view will be passed an author object with `author=` as a keyword, make sure your view has this parameter**
    
    
    Raises: (none of these should ever happen)
        ValueError: If none of can_be_author, can_be_logged_out, or can_be_superuser are True
        ValueError: If the request object does not have a user attribute
        ValueError: If an unhandled user type was found
        AssertionError: If the user has an author attribute that is not an Author object
    

    Args:
        can_be_author (bool, optional): Whether authors can view this (otherwise they will be redirected to their stream). Defaults to True.
        can_be_logged_out (bool, optional): Whether logged out people can view this (otherwise they will be redirected to login page). Defaults to False.
        can_be_superuser (bool, optional): Whether superusers can view this (otherwise they will be redirected to admin panel). Defaults to False.
        superuser_requires_author (bool, optional): Whether superusers must also be authors to view this. Defaults to False.
    """     
    def wrap(func:Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        if (not can_be_author) and (not can_be_logged_out) and (not can_be_superuser):
            raise ValueError("At least one of can_be_author, can_be_logged_out, or can_be_superuser must be True")
        
        def wrapped_f(request:HttpRequest, *args:list[Any], **kwargs:dict[str,Any]) -> HttpResponse:
            if not hasattr(request, "user"):
                raise ValueError("The request object does not have a user attribute")
            if not request.user.is_authenticated:
                if can_be_logged_out:
                    return func(request, *args, **kwargs)
                return HttpResponseRedirect(reverse("socialnetwork:not_logged_in"))
            
            # try to get an author object for the next two checks
            author_query = LocalAuthor.objects.filter(user=request.user)
            author = author_query.first() if author_query.exists() else None
            
            if request.user.is_superuser:
                if can_be_superuser and not superuser_requires_author:
                    return func(request, *args, **kwargs)
                if can_be_superuser and superuser_requires_author:
                    if author is not None:
                        return func(request, author=author, *args, **kwargs)
                    return HttpResponseRedirect(reverse("socialnetwork:stream"))
                return HttpResponseRedirect(reverse("adminpanel:adminpanel"))
            if author is not None:
                if can_be_author:
                    return func(request, author=author, *args, **kwargs)
                return HttpResponseRedirect(reverse("socialnetwork:stream"))
            raise ValueError("An unhandled user type was found: "+str(type(request.user)))
        return wrapped_f

    return wrap