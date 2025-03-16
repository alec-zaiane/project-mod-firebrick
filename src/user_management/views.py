from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from user_management.forms import JoinRequestForm

# Create your views here.


def join_view(request: HttpRequest) -> HttpResponse:
    """A view for users who are not logged in, to make a join request"""
    if request.method == "POST":
        form = JoinRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "registration/join_success.html")
    else:
        form = JoinRequestForm()

    return render(request, "registration/join.html", {"form": form})
