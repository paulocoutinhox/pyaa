from django.shortcuts import render
from django.urls import path


def home_index_view(request):
    return render(request, "pages/home/index.html")


urlpatterns = [
    path(
        "",
        home_index_view,
        name="home",
    ),
]
