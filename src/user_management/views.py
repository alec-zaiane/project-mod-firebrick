from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View

from user_management.forms import JoinRequestForm


# Create your views here.

class JoinView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = JoinRequestForm()
        return render(request, "registration/join.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = JoinRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "registration/join_success.html")
        return render(request, "registration/join.html", {"form": form})
