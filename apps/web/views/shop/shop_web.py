from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.shop.enums import (
    CheckoutStep,
    CreditPurchaseStatus,
    ObjectType,
    PaymentGatewayAction,
    PlanType,
    SubscriptionStatus,
)
from apps.shop.forms import CheckoutForm
from apps.shop.helpers import ShopHelper
from apps.shop.models import CreditPurchase, Plan, Subscription


def shop_plans_view(request, plan_type):
    customer = None

    # allowed plan types
    allowed_plan_types = [
        PlanType.SUBSCRIPTION,
        PlanType.CREDIT_PURCHASE,
        PlanType.VOUCHER,
    ]

    if plan_type not in [pt.value for pt in allowed_plan_types]:
        messages.error(request, _("message.shop-invalid-plan-type"))
        return redirect("home")

    if request.user.is_authenticated:
        customer = request.user.get_customer()

    # for subscription plans, check if the customer already has an active subscription
    if plan_type == PlanType.SUBSCRIPTION:
        if customer and customer.has_active_subscription():
            messages.info(request, _("message.shop-already-subscriber"))
            return redirect("account_profile")

    cache_key = f"shop_plans_{plan_type}"
    plans = cache.get(cache_key)

    if plans is None:
        plans = list(ShopHelper.get_plans_by_type(plan_type))
        cache.set(cache_key, plans, 3600)

    context = {
        "plans": plans,
        "plan_type": plan_type,
    }

    return render(request, "pages/shop/plans.html", context)


@login_required
def shop_checkout_view(request, type, code):
    if not request.user.has_customer():
        return redirect("home")

    customer = request.user.customer
    checkout_data = {}
    form_is_valid = False
    external_reference = None

    if request.method == "POST":
        if type == ObjectType.SUBSCRIPTION:
            plan = Plan.objects.filter(id=code, active=True).first()

            if not plan:
                messages.error(request, _("message.shop-plan-not-found"))
                return redirect("home")

            form = CheckoutForm(request.POST)
            form.create_for_subscription(plan, customer)

            if form.is_valid():
                form_is_valid = True

                subscription = Subscription.objects.create(
                    site=Site.objects.get_current(),
                    customer=customer,
                    plan=plan,
                    status=SubscriptionStatus.INITIAL,
                )

                checkout_data = ShopHelper.process_checkout_for_subscription(
                    request, subscription
                )

                if checkout_data.get("action") == PaymentGatewayAction.REDIRECT:
                    return redirect(checkout_data.get("url"))
                else:
                    messages.error(request, _("message.shop-invalid-action"))
                    return redirect("home")

        elif type == ObjectType.CREDIT_PURCHASE:
            plan = Plan.objects.filter(id=code, active=True).first()

            if not plan:
                messages.error(request, _("message.shop-plan-not-found"))
                return redirect("home")

            form = CheckoutForm(request.POST)
            form.create_for_credit_purchase(plan, customer)

            if form.is_valid():
                form_is_valid = True

                purchase = CreditPurchase.objects.create(
                    site=Site.objects.get_current(),
                    customer=customer,
                    plan=plan,
                    price=plan.price,
                    status=CreditPurchaseStatus.INITIAL,
                )

                checkout_data = ShopHelper.process_checkout_for_credit_purchase(
                    request, purchase
                )

                if checkout_data.get("action") == PaymentGatewayAction.REDIRECT:
                    return redirect(checkout_data.get("url"))
                else:
                    messages.error(request, _("message.shop-invalid-action"))
                    return redirect("home")

        else:
            messages.error(request, _("message.shop-invalid-type"))
            return redirect("home")

        if form_is_valid:
            external_reference = checkout_data.get("external_reference")

            if not external_reference:
                messages.error(request, _("message.shop-invalid-external-reference"))
                return redirect("home")

            form.gateway_code = external_reference
            form.checkout_step = CheckoutStep.PAYMENT

        return render(
            request,
            "pages/shop/checkout/index.html",
            {
                "checkout": form,
            },
        )

    else:
        form = CheckoutForm()

        if type == ObjectType.SUBSCRIPTION:
            plan = Plan.objects.filter(id=code, active=True).first()

            if plan:
                form.create_for_subscription(plan, customer)

        elif type == ObjectType.CREDIT_PURCHASE:
            plan = Plan.objects.filter(id=code, active=True).first()

            if plan:
                form.create_for_credit_purchase(plan, customer)

        else:
            messages.error(request, _("message.shop-invalid-type"))
            return redirect("home")

    return render(
        request,
        "pages/shop/checkout/index.html",
        {
            "checkout": form,
            "csrf_token": get_token(request),
        },
    )


@login_required
def shop_payment_success_view(request, token):
    if not request.user.has_customer():
        return redirect("home")

    paid_item = ShopHelper.get_item_by_token(token, request.user.customer)

    if not paid_item:
        messages.error(request, _("message.shop-paid-item-not-found"))
        return redirect("home")

    paid_item_type = ShopHelper.get_item_type_by_token(token)

    context = {
        "paid_item": paid_item,
        "paid_item_type": paid_item_type,
    }

    return render(request, "pages/shop/payment/success.html", context)


@login_required
def shop_payment_error_view(request, token):
    if not request.user.has_customer():
        return redirect("home")

    paid_item = ShopHelper.get_item_by_token(token, request.user.customer)

    if not paid_item:
        messages.error(request, _("message.shop-paid-item-not-found"))
        return redirect("home")

    paid_item_type = ShopHelper.get_item_type_by_token(token)

    context = {
        "paid_item": paid_item,
        "paid_item_type": paid_item_type,
    }

    return render(request, "pages/shop/payment/error.html", context)


@login_required
def shop_payment_pending_view(request, token):
    if not request.user.has_customer():
        return redirect("home")

    paid_item = ShopHelper.get_item_by_token(token, request.user.customer)

    if not paid_item:
        messages.error(request, _("message.shop-paid-item-not-found"))
        return redirect("home")

    paid_item_type = ShopHelper.get_item_type_by_token(token)

    context = {
        "paid_item": paid_item,
        "paid_item_type": paid_item_type,
    }

    return render(request, "pages/shop/payment/pending.html", context)


urlpatterns = [
    path(
        "shop/plans/<str:plan_type>/",
        shop_plans_view,
        name="shop_plans",
    ),
    path(
        "shop/checkout/<str:type>/<str:code>/",
        shop_checkout_view,
        name="shop_checkout",
    ),
    path(
        "shop/payment/success/<str:token>/",
        shop_payment_success_view,
        name="shop_payment_success",
    ),
    path(
        "shop/payment/error/<str:token>/",
        shop_payment_error_view,
        name="shop_payment_error",
    ),
    path(
        "shop/payment/pending/<str:token>/",
        shop_payment_pending_view,
        name="shop_payment_pending",
    ),
]
