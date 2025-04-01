from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.shop.enums import PaymentGatewayAction, PaymentGatewayCancelAction
from apps.shop.models import EventLog, Subscription


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
    )

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": session.url,
    }


def process_cancel(request, subscription):
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

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # construct the stripe event from the payload and signature
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # handle invalid payload
        return {
            "response": JsonResponse(
                {"error": f"invalid payload: {str(e)}"}, status=400
            )
        }
    except stripe.error.SignatureVerificationError as e:
        # handle invalid signature
        return {
            "response": JsonResponse(
                {"error": f"invalid signature: {str(e)}"}, status=400
            )
        }
    except Exception as e:
        # handle unexpected errors
        return {
            "response": JsonResponse(
                {"error": f"unexpected error: {str(e)}"}, status=500
            )
        }

    event_type = event["type"]
    event_data = event["data"]["object"]

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

    # create initial event log
    event_log = EventLog.objects.create(
        status=event_type,
        amount=amount,
        currency=currency,
        description=str(event_data),
    )

    # find subscription by event type
    subscription = get_subscription_from_event(event_data, event_type)

    if subscription:
        # update event log with subscription and customer information
        event_log.object_id = subscription.id
        event_log.object_type = "subscription"
        event_log.customer = subscription.customer
        event_log.save()

        # update external_id if necessary
        external_id = event_data.get("subscription")

        if not subscription.external_id and external_id:
            subscription.external_id = external_id
            subscription.save()
            subscription.refresh_from_db()

        try:
            if event_type == "invoice.payment_succeeded":
                # handle successful payment for a new or renewed subscription
                subscription.process_completed()
            elif event_type == "customer.subscription.deleted":
                # handle subscription cancellation
                subscription.process_canceled()
            elif event_type == "charge.refunded":
                # handle refunded payment (full or partial)
                subscription.process_refunded()
        except Exception as e:
            return {
                "response": JsonResponse(
                    {"error": f"failed to process event: {str(e)}"}, status=500
                )
            }

    return {"response": JsonResponse({"status": "success"}, status=200)}


def get_subscription_from_event(event_data, event_type):
    subscription = None

    # specific case for subscription creation
    if event_type == "customer.subscription.created":
        # use the subscription ID (external_id) from the event
        subscription_id = event_data.get("id")
        # try to find the subscription using the external_id
        subscription = Subscription.objects.filter(external_id=subscription_id).first()

    # specific case for subscription deletion or update events
    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.updated",
    ):
        subscription = Subscription.objects.filter(
            external_id=event_data.get("id")
        ).first()

    # specific case for invoice-related events
    elif event_type in (
        "invoice.payment_succeeded",
        "invoice.payment_failed",
        "invoice.finalized",
        "invoice.upcoming",
        "invoice.paid",
        "invoice.created",
        "invoice.updated",
    ):
        subscription = Subscription.objects.filter(
            external_id=event_data.get("subscription")
        ).first()

    # specific case for payment intent events
    elif event_type.startswith("payment_intent.") and "invoice" in event_data:
        invoice_id = event_data.get("invoice")

        if invoice_id:
            try:
                # retrieve the invoice to get the subscription_id
                invoice = stripe.Invoice.retrieve(invoice_id)
                subscription_id = invoice.get("subscription")

                if subscription_id:
                    subscription = Subscription.objects.filter(
                        external_id=subscription_id
                    ).first()
            except Exception:
                pass

    # handle charge events by retrieving the invoice and its subscription
    elif event_type.startswith("charge.") and "invoice" in event_data:
        invoice_id = event_data.get("invoice")

        if invoice_id:
            try:
                # retrieve the invoice to get the subscription_id
                invoice = stripe.Invoice.retrieve(invoice_id)
                subscription_id = invoice.get("subscription")

                if subscription_id:
                    subscription = Subscription.objects.filter(
                        external_id=subscription_id
                    ).first()
            except Exception:
                pass

    # fallback for other events using client_reference_id
    elif "client_reference_id" in event_data:
        subscription = Subscription.objects.filter(
            token=event_data.get("client_reference_id")
        ).first()

    # if no subscription was found, try retrieving via charge -> invoice -> subscription
    if not subscription and "charge" in event_data:
        charge_id = event_data.get("charge")

        try:
            charge = stripe.Charge.retrieve(charge_id)
            invoice_id = charge.get("invoice")

            if invoice_id:
                invoice = stripe.Invoice.retrieve(invoice_id)
                subscription_id = invoice.get("subscription")

                if subscription_id:
                    subscription = Subscription.objects.filter(
                        external_id=subscription_id
                    ).first()
        except Exception:
            pass

    return subscription
