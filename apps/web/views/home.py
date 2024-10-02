from django.shortcuts import render
from django.urls import path


def index_view(request):
    return render(request, "pages/home/index.html")


urlpatterns = [
    path(
        "",
        index_view,
        name="home",
    ),
]
