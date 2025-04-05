from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PaymentGatewayAction,
    PaymentGatewayCancelAction,
)
from apps.shop.models import CreditPurchase, EventLog, Subscription


def process_checkout_for_subscription(request, subscription):
    """create a checkout session for subscription payment"""
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
    )

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": session.url,
    }


def process_checkout_for_credit_purchase(request, purchase):
    """create a checkout session for one-time purchase payment"""
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
    )

    # log the credit purchase event
    EventLog.objects.create(
        site=Site.objects.get_current(),
        object_type=ObjectType.CREDIT_PURCHASE,
        object_id=purchase.id,
        status=purchase.status,
        amount=Decimal(purchase.price),
        customer=purchase.customer,
        description="credit purchase checkout session created on stripe",
    )

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": session.url,
    }


def process_cancel_for_subscription(request, subscription):
    """cancel an existing stripe subscription"""
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
    """handle stripe webhook events"""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # verify the webhook signature
    try:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return {
            "response": JsonResponse(
                {"error": f"invalid payload: {str(e)}"}, status=400
            )
        }
    except stripe.error.SignatureVerificationError as e:
        return {
            "response": JsonResponse(
                {"error": f"invalid signature: {str(e)}"}, status=400
            )
        }
    except Exception as e:
        return {
            "response": JsonResponse(
                {"error": f"unexpected error: {str(e)}"}, status=500
            )
        }

    # extract event details
    event_type = event["type"]
    event_data = event["data"]["object"]

    # log the event
    event_log = create_event_log(event_type, event_data)

    # handle subscription lifecycle events (create, update, delete)
    if event_type.startswith("customer.subscription."):
        handle_subscription_lifecycle(event_type, event_data, event_log)
        return {"response": JsonResponse({"status": "success"}, status=200)}

    # handle payment events
    token = extract_token(event_data)
    if token:
        if token.startswith("subscription."):
            handle_subscription_payment(event_type, event_data, token, event_log)
        elif token.startswith("credit-purchase."):
            handle_credit_purchase_payment(event_type, event_data, token, event_log)

    return {"response": JsonResponse({"status": "success"}, status=200)}


def create_event_log(event_type, event_data):
    """create an event log entry for the webhook event"""
    amount, currency = extract_amount_and_currency(event_data)

    event_log = EventLog.objects.create(
        site=Site.objects.get_current(),
        status=event_type,
        amount=amount,
        currency=currency,
        description=str(event_data),
    )

    return event_log


def handle_subscription_lifecycle(event_type, event_data, event_log):
    subscription_id = event_data.get("id")
    if not subscription_id:
        return

    subscription = Subscription.objects.filter(external_id=subscription_id).first()
    if not subscription:
        # try to find by token
        if "metadata" in event_data and "token" in event_data["metadata"]:
            token = event_data["metadata"]["token"]
            subscription = Subscription.objects.filter(token=token).first()

    if subscription:
        # update event log with subscription details
        event_log.object_id = subscription.id
        event_log.object_type = ObjectType.SUBSCRIPTION
        event_log.customer = subscription.customer
        event_log.save()

        # handle specific lifecycle events
        if event_type == "customer.subscription.created":
            # ensure the external_id is set
            subscription.external_id = subscription_id
            subscription.save()
        elif event_type == "customer.subscription.deleted":
            # handle subscription cancellation
            subscription.process_canceled()


def handle_subscription_payment(event_type, event_data, token, event_log):
    subscription = Subscription.objects.filter(token=token).first()
    if not subscription and "subscription" in event_data:
        # try to find by external_id
        subscription = Subscription.objects.filter(
            external_id=event_data.get("subscription")
        ).first()

    if subscription:
        # update event log with subscription details
        event_log.object_id = subscription.id
        event_log.object_type = ObjectType.SUBSCRIPTION
        event_log.customer = subscription.customer
        event_log.save()

        # handle payment events
        if event_type in ("invoice.payment_succeeded", "charge.succeeded"):
            subscription.process_completed()
        elif event_type == "charge.refunded":
            subscription.process_refunded()


def handle_credit_purchase_payment(event_type, event_data, token, event_log):
    purchase = CreditPurchase.objects.filter(token=token).first()

    if purchase:
        # update event log with purchase details
        event_log.object_id = purchase.id
        event_log.object_type = ObjectType.CREDIT_PURCHASE
        event_log.customer = purchase.customer
        event_log.save()

        # handle payment events
        if event_type in (
            "payment_intent.succeeded",
            "checkout.session.completed",
            "charge.succeeded",
        ):
            # process successful payment
            purchase.status = CreditPurchaseStatus.APPROVED
            purchase.save(update_fields=["status"])

            # add credits to customer
            from apps.customer.helpers import CustomerHelper

            CustomerHelper.add_credits(
                customer=purchase.customer,
                plan=purchase.plan,
                object_id=purchase.id,
                object_type=ObjectType.CREDIT_PURCHASE,
            )

            # send confirmation email
            CustomerHelper.send_credit_purchase_paid_email(purchase)
        elif event_type in ("payment_intent.canceled", "checkout.session.expired"):
            # handle canceled payment
            purchase.status = CreditPurchaseStatus.CANCELED
            purchase.save(update_fields=["status"])
        elif event_type == "charge.refunded":
            # handle refunded payment
            purchase.status = CreditPurchaseStatus.REFUNDED
            purchase.save(update_fields=["status"])


def extract_token(event_data):
    # try client_reference_id first (checkout sessions)
    if "client_reference_id" in event_data:
        return event_data.get("client_reference_id")

    # try metadata token
    if "metadata" in event_data and "token" in event_data["metadata"]:
        return event_data["metadata"]["token"]

    # check for payment intent metadata
    if "payment_intent" in event_data:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(event_data["payment_intent"])
            if "metadata" in payment_intent and "token" in payment_intent["metadata"]:
                return payment_intent["metadata"]["token"]
        except Exception:
            pass

    # check invoice for subscription token
    if "invoice" in event_data:
        try:
            invoice = stripe.Invoice.retrieve(event_data["invoice"])
            subscription_id = invoice.get("subscription")
            if subscription_id:
                subscription = Subscription.objects.filter(
                    external_id=subscription_id
                ).first()
                if subscription:
                    return subscription.token
        except Exception:
            pass

    # check subscription directly
    if "subscription" in event_data:
        subscription = Subscription.objects.filter(
            external_id=event_data["subscription"]
        ).first()
        if subscription:
            return subscription.token

    return None


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
