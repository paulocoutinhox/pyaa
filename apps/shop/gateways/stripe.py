from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.shop.enums import ObjectType, PaymentGatewayAction, PaymentGatewayCancelAction
from apps.shop.models import CreditPurchase, EventLog, Subscription


def process_checkout_for_subscription(request, subscription):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    success_url = request.build_absolute_uri(
        reverse("shop_payment_success", kwargs={"token": subscription.token})
    )

    cancel_url = request.build_absolute_uri(
        reverse("shop_payment_error", kwargs={"token": subscription.token})
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price": subscription.plan.external_id,
                "quantity": 1,
            }
        ],
        client_reference_id=str(subscription.token),
        customer_email=request.user.email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "token": subscription.token,
        },
        subscription_data={
            "metadata": {
                "token": subscription.token,
            }
        },
    )

    # log the subscription event
    EventLog.objects.create(
        site=Site.objects.get_current(),
        object_type=ObjectType.SUBSCRIPTION,
        object_id=subscription.id,
        status=subscription.status,
        amount=Decimal(subscription.plan.price),
        customer=subscription.customer,
        description="Subscription checkout session created on Stripe",
    )

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": session.url,
    }


def process_checkout_for_credit_purchase(request, purchase):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    success_url = request.build_absolute_uri(
        reverse("shop_payment_success", kwargs={"token": purchase.token})
    )

    cancel_url = request.build_absolute_uri(
        reverse("shop_payment_error", kwargs={"token": purchase.token})
    )

    # create a stripe checkout session for one-time payment
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": purchase.plan.currency.lower(),
                    "product_data": {
                        "name": purchase.plan.name,
                    },
                    "unit_amount": int(purchase.plan.price * 100),
                },
                "quantity": 1,
            }
        ],
        client_reference_id=str(purchase.token),
        customer_email=request.user.email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "token": purchase.token,
        },
        payment_intent_data={
            "metadata": {
                "token": purchase.token,
            }
        },
    )

    # log the credit purchase event
    EventLog.objects.create(
        site=Site.objects.get_current(),
        object_type=ObjectType.CREDIT_PURCHASE,
        object_id=purchase.id,
        status=purchase.status,
        amount=Decimal(purchase.price),
        customer=purchase.customer,
        description="Credit Purchase checkout session created on Stripe",
    )

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": session.url,
    }


def process_cancel_for_subscription(request, subscription):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe_subscription = subscription.external_id
    redirect_url = reverse("account_profile")

    try:
        # attempt to cancel the stripe subscription
        stripe.Subscription.cancel(stripe_subscription)
        messages.success(request, _("message.subscription-canceled"))
    except Exception as e:
        # handle any exceptions and append the error message using format for translations
        error_message = _("message.error-cancel-subscription: %(error)s") % {
            "error": str(e),
        }

        messages.error(request, error_message)

    return {
        "action": PaymentGatewayCancelAction.REDIRECT,
        "url": redirect_url,
    }


def process_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # verify the webhook signature
    try:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return {"response": JsonResponse({"error": "invalid payload"}, status=400)}
    except stripe.error.SignatureVerificationError:
        return {"response": JsonResponse({"error": "invalid signature"}, status=400)}
    except Exception as e:
        return {"response": JsonResponse({"error": f"error: {str(e)}"}, status=500)}

    # extract event details
    event_type = event["type"]
    event_data = event["data"]["object"]

    # extract token from metadata
    token = extract_token(event_data)

    if not token:
        # no token found, return success as we don't know how to handle this
        return {"response": JsonResponse({"status": "success"}, status=200)}

    # create event log
    event_log = create_event_log(event_type, event_data)

    # determine the object type based on token prefix
    if token.startswith("subscription."):
        handle_subscription_event(event_type, event_data, token, event_log)
    elif token.startswith("credit-purchase."):
        handle_credit_purchase_event(event_type, event_data, token, event_log)

    return {"response": JsonResponse({"status": "success"}, status=200)}


def handle_subscription_event(event_type, event_data, token, event_log):
    # find the subscription object
    subscription = Subscription.objects.filter(token=token).first()

    if not subscription:
        return

    # update event log with subscription details
    event_log.object_id = subscription.id
    event_log.object_type = ObjectType.SUBSCRIPTION
    event_log.customer = subscription.customer
    event_log.save()

    # update external id if we have it and it's not set
    if not subscription.external_id and "subscription" in event_data:
        subscription.external_id = event_data.get("subscription")
        subscription.save(update_fields=["external_id"])

    # handle based on event type
    if event_type in ["invoice.payment_succeeded"]:
        # successful payment
        subscription.process_completed()
    elif event_type in ["customer.subscription.deleted"]:
        # canceled subscription
        subscription.process_canceled()
    elif event_type in ["charge.refunded"]:
        # refunded payment
        subscription.process_refunded()


def handle_credit_purchase_event(event_type, event_data, token, event_log):
    # find the credit purchase object
    purchase = CreditPurchase.objects.filter(token=token).first()

    if not purchase:
        return

    # update event log with purchase details
    event_log.object_id = purchase.id
    event_log.object_type = ObjectType.CREDIT_PURCHASE
    event_log.customer = purchase.customer
    event_log.save()

    # handle based on event type
    if event_type in ["checkout.session.completed"]:
        # successful payment
        purchase.process_completed()
    elif event_type in ["payment_intent.canceled"]:
        # canceled payment
        purchase.process_canceled()
    elif event_type in ["charge.refunded"]:
        # refunded payment
        purchase.process_refunded()


def create_event_log(event_type, event_data):
    amount, currency = extract_amount_and_currency(event_data)

    event_log = EventLog.objects.create(
        site=Site.objects.get_current(),
        status=event_type,
        amount=amount,
        currency=currency,
        description=str(event_data),
    )

    return event_log


def extract_amount_and_currency(event_data):
    # retrieve amount from event data
    if "total" in event_data:
        amount = Decimal(event_data["total"]) / 100
    elif "amount_paid" in event_data:
        amount = Decimal(event_data["amount_paid"]) / 100
    elif "amount_total" in event_data:
        amount = Decimal(event_data["amount_total"]) / 100
    elif "amount" in event_data:
        amount = Decimal(event_data["amount"]) / 100
    elif "plan" in event_data and "amount" in event_data["plan"]:
        amount = Decimal(event_data["plan"]["amount"]) / 100
    else:
        amount = Decimal(0)

    # retrieve currency from event data
    if "currency" in event_data:
        currency = event_data["currency"]
    elif "plan" in event_data and "currency" in event_data["plan"]:
        currency = event_data["plan"]["currency"]
    else:
        currency = None

    return amount, currency


def extract_token(event_data):
    """
    Extract token from event data using various possible locations,
    checking all paths regardless of event type.
    """
    # check directly in metadata
    if "metadata" in event_data:
        if "token" in event_data["metadata"]:
            return event_data["metadata"]["token"]

    # check in client reference id
    if "client_reference_id" in event_data:
        return event_data.get("client_reference_id")

    # check in subscription details metadata
    if "subscription_details" in event_data:
        sd = event_data["subscription_details"]

        if "metadata" in sd:
            if "token" in sd["metadata"]:
                return sd["metadata"]["token"]

    # check in parent metadata
    if "parent" in event_data and event_data["parent"]:
        parent = event_data["parent"]
        if "subscription_details" in parent and parent["subscription_details"]:
            sd = parent["subscription_details"]
            if "metadata" in sd and "token" in sd["metadata"]:
                return sd["metadata"]["token"]

    # check in lines metadata
    if "lines" in event_data and event_data["lines"]:
        lines = event_data["lines"]

        if "data" in lines and lines["data"]:
            for line_item in lines["data"]:
                if "metadata" in line_item:
                    if "token" in line_item["metadata"]:
                        return line_item["metadata"]["token"]

    return None
