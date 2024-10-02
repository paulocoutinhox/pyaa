from django.conf.urls import include
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.customer.forms import (
    CustomerDeleteForm,
    CustomerUpdateAvatarForm,
    CustomerUpdateProfileForm,
)
from apps.customer.models import Customer
from apps.shop import helpers as gh
from apps.shop.enums import PaymentGatewayCancelAction, SubscriptionStatus
from apps.shop.models import CreditLog, Subscription


@login_required
def account_profile_view(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect("home")

    return render(
        request,
        "account/profile.html",
        {
            "customer": customer,
        },
    )


@login_required
def account_update_profile_view(request):
    if request.method == "POST":
        form = CustomerUpdateProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, _("message.account-updated"))
            return redirect("account_profile")
    else:
        form = CustomerUpdateProfileForm(user=request.user)

    return render(
        request,
        "account/update_profile.html",
        {
            "form": form,
        },
    )


@login_required
def account_update_avatar_view(request):
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
def account_delete_view(request):
    customer = Customer.objects.get(user=request.user)

    # check if the customer has an active subscription
    active_subscriptions = Subscription.objects.filter(
        customer=customer, status=SubscriptionStatus.ACTIVE
    )

    if active_subscriptions.exists():
        # redirect to profile with an error message
        messages.error(request, _("message.error.account-has-subscriptions"))
        return redirect("account_profile")

    if request.method == "POST":
        form = CustomerDeleteForm(request.POST, instance=customer)

        if form.is_valid():
            user = request.user
            # log the user out and delete the account
            logout(request)
            user.delete()
            messages.info(request, _("message.account-deleted"))
            return redirect("home")
    else:
        form = CustomerDeleteForm(instance=customer)

    # render the account delete page with the delete form
    return render(
        request,
        "account/delete.html",
        {
            "form": form,
        },
    )


@login_required
def account_subscriptions_view(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect("home")

    subscriptions = Subscription.objects.filter(
        customer=request.user.customer,
    ).order_by("-id")

    return render(
        request,
        "account/subscriptions.html",
        {
            "customer": customer,
            "subscriptions": subscriptions,
        },
    )


@login_required
def account_subscription_cancel_view(request, token):
    try:
        subscription = Subscription.objects.get(token=token)
    except Subscription.DoesNotExist:
        return redirect("home")

    cancel_data = gh.process_cancel(request, subscription)
    action = cancel_data["action"]

    if action == PaymentGatewayCancelAction.REDIRECT:
        return redirect(cancel_data["url"])

    messages.error(request, _("message.shop-invalid-cancel-action"))
    return redirect("home")


@login_required
def account_credits_view(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect("home")

    credits = CreditLog.objects.filter(
        customer=request.user.customer,
    ).order_by("-id")

    return render(
        request,
        "account/credits.html",
        {
            "customer": customer,
            "credits": credits,
        },
    )


urlpatterns = [
    path(
        "accounts/",
        include("allauth.urls"),
    ),
    path(
        "account/profile/",
        account_profile_view,
        name="account_profile",
    ),
    path(
        "account/delete/",
        account_delete_view,
        name="account_delete",
    ),
    path(
        "account/profile/update/",
        account_update_profile_view,
        name="account_update_profile",
    ),
    path(
        "account/avatar/update/",
        account_update_avatar_view,
        name="account_update_avatar",
    ),
    path(
        "account/subscriptions/",
        account_subscriptions_view,
        name="account_subscriptions",
    ),
    path(
        "account/subscription/cancel/<str:token>/",
        account_subscription_cancel_view,
        name="account_subscription_cancel",
    ),
    path(
        "account/credits/",
        account_credits_view,
        name="account_credits",
    ),
]
