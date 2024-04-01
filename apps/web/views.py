from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserDeleteForm


def home_view(request):
    return render(request, "home/index.html")


@login_required
def account_profile_view(request):
    return render(request, "account/account_profile.html")


@login_required
def account_delete_view(request):
    if request.method == "POST":
        form = UserDeleteForm(request.POST, instance=request.user)

        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            messages.info(request, "Your account has been deleted.")
            return redirect("home")
    else:
        form = UserDeleteForm(instance=request.user)

    context = {"form": form}

    return render(request, "account/account_delete.html", context)
