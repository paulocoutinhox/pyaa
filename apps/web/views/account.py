from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.customers.forms import (
    CustomerDeleteForm,
    CustomerUpdateAvatarForm,
    CustomerUpdateProfileForm,
)
from apps.customers.models import Customer


@login_required
def profile_view(request):
    return render(request, "account/profile.html")


@login_required
def update_profile_view(request):
    if request.method == "POST":
        form = CustomerUpdateProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, _("message.account-updated"))
            return redirect("account_profile")
    else:
        form = CustomerUpdateProfileForm(user=request.user)

    return render(request, "account/update_profile.html", {"form": form})


@login_required
def update_avatar_view(request):
    if request.method == "POST":
        form = CustomerUpdateAvatarForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, _("message.account-updated"))
            return redirect("account_profile")
    else:
        form = CustomerUpdateAvatarForm(user=request.user)

    user = request.user
    customer = user.customer

    return render(
        request,
        "account/update_avatar.html",
        {
            "form": form,
            "customer": customer,
        },
    )


@login_required
def delete_view(request):
    customer = Customer.objects.get(user=request.user)

    if request.method == "POST":
        form = CustomerDeleteForm(request.POST, instance=customer)

        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            messages.info(request, _("message.account-deleted"))
            return redirect("home")
    else:
        form = CustomerDeleteForm(instance=customer)

    return render(request, "account/delete.html", {"form": form})
