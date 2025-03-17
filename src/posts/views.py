from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


from user_management.models import LocalAuthor
from core.utils.user_control_decorator import user_control, user_controller, REDIRECT_TO_LOGIN


# Create your views here.
@user_controller(must_be_logged_in=True, fail_response=REDIRECT_TO_LOGIN)
def stream_view(request: HttpRequest, viewer: LocalAuthor) -> HttpResponse:
    """Stream view for an author"""
    page = int(request.GET.get('page', '1'))
    size = int(request.GET.get('size', '10'))
    start = (page - 1) * size

    posts = viewer.get_stream(paginate_start=start, paginate_count=size)

    return render(request, "stream.html", {
        "user": request.user,
        "viewer": viewer,
        "posts": posts,
        "current_page": page,
    })
