from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render, resolve_url
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.banner.enums import BannerZone
from apps.banner.helpers import BannerHelper
from apps.customer.enums import CustomerAddressType
from apps.customer.forms import (
    CustomerChangePasswordForm,
    CustomerDeleteForm,
    CustomerLoginForm,
    CustomerPasswordRecoveryForm,
    CustomerResetPasswordForm,
    CustomerSignupForm,
    CustomerUpdateAddressForm,
    CustomerUpdateAvatarForm,
    CustomerUpdateProfileForm,
)
from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.shop.enums import PaymentGatewayCancelAction, SubscriptionStatus
from apps.shop.helpers import ShopHelper
from apps.shop.models import CreditLog, CreditPurchase, ProductPurchase, Subscription
from pyaa.decorators.customer import customer_required
from pyaa.helpers.request import RequestHelper
from pyaa.utils.cached_paginator import Paginator


def account_login_view(request):
    next_url = RequestHelper.get_next_url(request)
    banners = BannerHelper.get_banners(BannerZone.SIGNIN)

    if request.method == "POST":
        form = CustomerLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user:
                login(request, user)
                messages.success(request, _("message.login-success"))

                if next_url:
                    return redirect(next_url)
                else:
                    return redirect("account_profile")
            else:
                messages.error(request, _("error.invalid-login-data"))
    else:
        form = CustomerLoginForm()

    return render(
        request,
        "pages/account/login.html",
        {
            "form": form,
            "next_url": next_url,
            "banners": banners,
        },
    )


def account_signup_view(request):
    next_url = RequestHelper.get_next_url(request)
    banners = BannerHelper.get_banners(BannerZone.SIGNUP)

    if request.method == "POST":
        form = CustomerSignupForm(request.POST)

        if form.is_valid():
            customer = form.save()

            # check if activation is required
            if settings.CUSTOMER_ACTIVATION_REQUIRED:
                return redirect("account_activation_pending")
            else:
                # log the user in directly if activation not required
                login(request, customer.user)
                query_params = {"next": next_url} if next_url else {}

                return redirect(
                    f"{resolve_url('account_signup_success')}?{urlencode(query_params)}"
                )
    else:
        form = CustomerSignupForm()

    return render(
        request,
        "pages/account/signup.html",
        {
            "form": form,
            "next": next_url,
            "banners": banners,
        },
    )


@login_required
def account_logout_view(request):
    logout(request)
    return redirect("account_logout_success")


@customer_required
def account_profile_view(request):
    return render(
        request,
        "pages/account/profile.html",
        {
            "customer": request.customer,
        },
    )


@login_required
def account_update_profile_view(request):
    if request.method == "POST":
        form = CustomerUpdateProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            if form.save():
                messages.success(request, _("message.account-updated"))
                return redirect("account_profile")
    else:
        form = CustomerUpdateProfileForm(user=request.user)

    return render(
        request,
        "pages/account/update_profile.html",
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
        "pages/account/update_avatar.html",
        {
            "form": form,
            "customer": customer,
        },
    )


@login_required
def account_change_password_view(request):
    if request.method == "POST":
        form = CustomerChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            if form.save():
                messages.success(request, _("message.password-changed"))
                return redirect("account_profile")
    else:
        form = CustomerChangePasswordForm(user=request.user)

    return render(
        request,
        "pages/account/change_password.html",
        {
            "form": form,
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
        "pages/account/delete.html",
        {
            "form": form,
        },
    )


@customer_required
def account_subscriptions_view(request):
    subscriptions = Subscription.objects.filter(
        customer=request.customer,
    ).order_by("-id")

    # get the page parameter from request
    page = request.GET.get("page", 1)

    # setup paginator with cache key
    paginator = Paginator(
        subscriptions,
        per_page=10,
        cache_key="account-subscriptions",
        cache_timeout=0,
    )

    # get the page object
    page_obj = paginator.page(page)

    return render(
        request,
        "pages/account/subscriptions.html",
        {
            "customer": request.customer,
            "page_obj": page_obj,
        },
    )


@customer_required
def account_subscription_cancel_view(request, token):
    try:
        subscription = Subscription.objects.get(token=token)
    except Subscription.DoesNotExist:
        return redirect("home")

    cancel_data = ShopHelper.process_cancel_for_subscription(request, subscription)
    action = cancel_data["action"]

    if action == PaymentGatewayCancelAction.REDIRECT:
        return redirect(cancel_data["url"])

    messages.error(request, _("message.shop-invalid-cancel-action"))
    return redirect("home")


@customer_required
def account_credits_view(request):
    credits = CreditLog.objects.filter(
        customer=request.customer,
    ).order_by("-id")

    # get the page parameter from request
    page = request.GET.get("page", 1)

    # setup paginator with cache key
    paginator = Paginator(
        credits,
        per_page=10,
        cache_key="account-credits",
        cache_timeout=0,
    )

    # get the page object
    page_obj = paginator.page(page)

    return render(
        request,
        "pages/account/credits.html",
        {
            "customer": request.customer,
            "page_obj": page_obj,
        },
    )


@customer_required
def account_credit_purchases_view(request):
    purchases = CreditPurchase.objects.filter(
        customer=request.customer,
    ).order_by("-id")

    # get the page parameter from request
    page = request.GET.get("page", 1)

    # setup paginator with cache key
    paginator = Paginator(
        purchases,
        per_page=10,
        cache_key="account-credit-purchases",
        cache_timeout=0,
    )

    # get the page object
    page_obj = paginator.page(page)

    return render(
        request,
        "pages/account/credit_purchases.html",
        {
            "customer": request.customer,
            "page_obj": page_obj,
        },
    )


@customer_required
def account_product_purchases_view(request):
    purchases = ProductPurchase.objects.filter(
        customer=request.customer,
    ).order_by("-id")

    # get the page parameter from request
    page = request.GET.get("page", 1)

    # setup paginator with cache key
    paginator = Paginator(
        purchases,
        per_page=10,
        cache_key="account-product-purchases",
        cache_timeout=0,
    )

    # get the page object
    page_obj = paginator.page(page)

    return render(
        request,
        "pages/account/product_purchases.html",
        {
            "customer": request.customer,
            "page_obj": page_obj,
        },
    )


def account_signup_success_view(request):
    next_url = RequestHelper.get_next_url(request)

    return render(
        request,
        "pages/account/signup_success.html",
        {
            "next_url": next_url,
        },
    )


def account_logout_success_view(request):
    return render(request, "pages/account/logout_success.html")


def account_password_recovery_view(request):
    if request.method == "POST":
        form = CustomerPasswordRecoveryForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data.get("user")

            if user and user.has_customer():
                # send recovery email if user exists
                CustomerHelper.send_password_recovery_email(user.customer)

            # always redirect to success page regardless of whether user exists
            return redirect("account_password_recovery_success")
    else:
        form = CustomerPasswordRecoveryForm()

    return render(
        request,
        "pages/account/password_recovery.html",
        {
            "form": form,
        },
    )


def account_password_recovery_success_view(request):
    return render(request, "pages/account/password_recovery_success.html")


def account_reset_password_view(request, token):
    try:
        # find customer with matching recovery token
        customer = Customer.objects.get(recovery_token=token)
    except (Customer.DoesNotExist, ValueError):
        raise Http404("Invalid token")

    if request.method == "POST":
        form = CustomerResetPasswordForm(request.POST)

        if form.is_valid():
            # update the user's password
            user = customer.user
            user.set_password(form.cleaned_data["password"])
            user.save()

            # reset recovery token to null after successful password reset
            CustomerHelper.reset_recovery_token(customer)

            # redirect to success page
            return redirect("account_reset_password_success")
    else:
        form = CustomerResetPasswordForm()

    return render(
        request,
        "pages/account/reset_password.html",
        {
            "form": form,
        },
    )


def account_reset_password_success_view(request):
    return render(request, "pages/account/reset_password_success.html")


def account_activation_pending_view(request):
    return render(
        request,
        "pages/account/activation_pending.html",
    )


def account_activate_view(request, token):
    try:
        # activate the account
        customer = CustomerHelper.activate_account(token)

        if customer:
            messages.success(request, _("message.account-activation-success"))
            return redirect("account_activation_success")
        else:
            messages.error(request, _("error.invalid-activation-token"))
            return redirect("home")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("home")


def account_activation_success_view(request):
    return render(
        request,
        "pages/account/activation_success.html",
    )


@login_required
def account_update_address_view(request):
    if request.method == "POST":
        # try to get existing address
        address = request.user.customer.get_address_by_type(CustomerAddressType.MAIN)

        form = CustomerUpdateAddressForm(
            request.POST, instance=address, customer=request.user.customer
        )

        if form.is_valid():
            form.save()
            messages.success(request, _("message.account-updated"))
            return redirect("account_profile")
    else:
        # try to get existing address
        address = request.user.customer.get_address_by_type(CustomerAddressType.MAIN)
        form = CustomerUpdateAddressForm(
            instance=address, customer=request.user.customer
        )

    return render(
        request,
        "pages/account/update_address.html",
        {
            "form": form,
        },
    )


urlpatterns = [
    path(
        "account/signup/",
        account_signup_view,
        name="account_signup",
    ),
    path(
        "account/login/",
        account_login_view,
        name="account_login",
    ),
    path(
        "account/logout/",
        account_logout_view,
        name="account_logout",
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
        "account/change-password/",
        account_change_password_view,
        name="account_change_password",
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
    path(
        "account/credit-purchases/",
        account_credit_purchases_view,
        name="account_credit_purchases",
    ),
    path(
        "account/product-purchases/",
        account_product_purchases_view,
        name="account_product_purchases",
    ),
    path(
        "account/signup/success",
        account_signup_success_view,
        name="account_signup_success",
    ),
    path(
        "account/logout/success",
        account_logout_success_view,
        name="account_logout_success",
    ),
    path(
        "account/password-recovery/",
        account_password_recovery_view,
        name="account_password_recovery",
    ),
    path(
        "account/password-recovery/success/",
        account_password_recovery_success_view,
        name="account_password_recovery_success",
    ),
    path(
        "account/reset-password/<uuid:token>/",
        account_reset_password_view,
        name="account_reset_password",
    ),
    path(
        "account/reset-password/success/",
        account_reset_password_success_view,
        name="account_reset_password_success",
    ),
    path(
        "account/activation/pending/",
        account_activation_pending_view,
        name="account_activation_pending",
    ),
    path(
        "account/activate/<uuid:token>/",
        account_activate_view,
        name="account_activate",
    ),
    path(
        "account/activation/success/",
        account_activation_success_view,
        name="account_activation_success",
    ),
    path(
        "account/address/update/",
        account_update_address_view,
        name="account_update_address",
    ),
]
