from django.shortcuts import render
from django.urls import path


def index_view(request):
    return render(request, "pages/subscription/index.html")


urlpatterns = [
    path(
        "subscription/",
        index_view,
        name="subscription",
    ),
]
