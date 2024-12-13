from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.shop import helpers as gh
from apps.shop.enums import PaymentGatewayAction, SubscriptionStatus
from apps.shop.models import Plan, Subscription


@login_required
def shop_buy_by_tag_view(request, plan_tag):
    plan = Plan.objects.filter(tag=plan_tag, active=True).first()

    if not plan:
        messages.error(request, _("message.shop-plan-not-found"))
        return redirect("home")

    subscription = Subscription.objects.create(
        customer=request.user.customer,
        plan=plan,
        status=SubscriptionStatus.INITIAL,
    )

    checkout_data = gh.process_checkout(request, subscription)
    action = checkout_data["action"]

    if action == PaymentGatewayAction.REDIRECT:
        return redirect(checkout_data["url"])

    messages.error(request, _("message.shop-invalid-action"))
    return redirect("home")


@login_required
def shop_payment_success_view(request, token):
    subscription = Subscription.objects.filter(
        token=token, customer=request.user.customer
    ).first()

    if not subscription:
        messages.error(request, _("message.shop-subscription-not-found"))
        return redirect("home")

    context = {
        "subscription": subscription,
    }

    return render(request, "pages/shop/payment_success.html", context)


@login_required
def shop_payment_failure_view(request, token):
    subscription = Subscription.objects.filter(
        token=token, customer=request.user.customer
    ).first()

    if not subscription:
        messages.error(request, _("message.shop-subscription-not-found"))
        return redirect("home")

    context = {
        "subscription": subscription,
    }

    return render(request, "pages/shop/payment_failure.html", context)


def shop_plans_view(request):
    customer = None

    if request.user.is_authenticated:
        customer = request.user.get_customer()

    if customer and customer.has_active_subscription():
        messages.info(request, _("message.shop-already-subscriber"))
        return redirect("account_profile")

    plans = Plan.objects.filter(active=True).order_by("sort_order").all()

    context = {
        "plans": plans,
    }

    return render(request, "pages/shop/plans.html", context)


urlpatterns = [
    path(
        "shop/buy/<slug:plan_tag>",
        shop_buy_by_tag_view,
        name="shop_buy_by_tag",
    ),
    path(
        "shop/payment/success/<str:token>/",
        shop_payment_success_view,
        name="shop_payment_success",
    ),
    path(
        "shop/payment/failure/<str:token>/",
        shop_payment_failure_view,
        name="shop_payment_failure",
    ),
    path(
        "shop/plans/",
        shop_plans_view,
        name="shop_plans",
    ),
]
