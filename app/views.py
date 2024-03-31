from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render


def home_view(request):
    return render(request, "home/index.html")


def login_view(request):
    return render(request, "home/index.html")


def logout(request):
    auth_logout(request)
    return redirect("/")
