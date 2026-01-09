from django.shortcuts import render
from django.urls import path


def test_cheatsheet_view(request):
    return render(
        request,
        "pages/test/cheatsheet.html",
    )


urlpatterns = [
    path(
        "test/cheatsheet/",
        test_cheatsheet_view,
        name="test_cheatsheet",
    ),
]
