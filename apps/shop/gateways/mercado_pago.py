import json
import uuid
from decimal import Decimal

import mercadopago
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PaymentGatewayAction,
    SubscriptionStatus,
)
from apps.shop.models import CreditPurchase, EventLog, Subscription
from pyaa.helpers.mail import MailHelper
from pyaa.helpers.string import StringHelper


def process_checkout_for_subscription(request, subscription):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    success_url = request.build_absolute_uri(
        reverse(
            "shop_subscription_payment_success", kwargs={"token": subscription.token}
        )
    )
    cancel_url = request.build_absolute_uri(
        reverse(
            "shop_subscription_payment_failure", kwargs={"token": subscription.token}
        )
    )

    preapproval_data = {
        "reason": subscription.plan.name,
        "auto_recurring": {
            "frequency": subscription.plan.frequency_amount,
            "frequency_type": subscription.plan.frequency_type.lower(),
            "transaction_amount": float(subscription.plan.price),
            "currency_id": subscription.plan.currency,
            "start_date": timezone.now().isoformat(),
        },
        "payer_email": request.user.email,
        "external_reference": str(subscription.token),
        "back_url": success_url,
    }

    preapproval = sdk.preapproval().create(preapproval_data)

    EventLog.objects.create(
        site=Site.objects.get_current(),
        object_type=ObjectType.SUBSCRIPTION,
        object_id=subscription.id,
        status=subscription.status,
        amount=Decimal(subscription.plan.price),
        customer=request.user.customer,
        description="Subscription preapproval created",
    )

    subscription.external_id = preapproval["response"]["id"]
    subscription.save(update_fields=["external_id"])

    return {
        "action": PaymentGatewayAction.REDIRECT,
        "url": preapproval["response"]["init_point"],
    }


def process_checkout_for_credit_purchase(request, purchase):
    EventLog.objects.create(
        site=Site.objects.get_current(),
        object_type=ObjectType.CREDIT_PURCHASE,
        object_id=purchase.id,
        status=purchase.status,
        amount=Decimal(purchase.price),
        customer=request.user.customer,
        description="Credit purchase preference created on Mercado Pago",
    )

    return {
        "external_reference": purchase.token,
    }


def process_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return {
            "response": JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)
        }

    topic = payload.get("type")
    data_id = payload.get("data", {}).get("id")

    if not topic or not data_id:
        return {
            "response": JsonResponse(
                {"error": "Invalid payload: missing 'type' or 'data.id'"}, status=400
            )
        }

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    try:
        if topic == "payment":
            payment_data = sdk.payment().get(data_id)["response"]
            return process_webhook_payment(payment_data)
        elif topic in ["subscription_preapproval", "subscription_authorized_payment"]:
            subscription_data = sdk.preapproval().get(data_id)["response"]
            return process_webhook_subscription(subscription_data)
        else:
            raise ValueError(f"Unsupported topic ({topic})")
    except Exception as e:
        error = (
            f"Failed to process webhook for topic {topic} and id {data_id}: {str(e)}"
        )

        EventLog.objects.create(
            site=Site.objects.get_current(),
            object_type=ObjectType.UNKNOWN,
            object_id=None,
            status="error",
            description=error,
        )

        return {"response": JsonResponse({"error": error}, status=500)}


def process_webhook_payment(payment_data):
    # external reference
    external_reference = payment_data.get("external_reference", "")
    external_reference_parts = external_reference.split(".")

    if len(external_reference_parts) == 2:
        object_type = external_reference_parts[0]

        if object_type == ObjectType.CREDIT_PURCHASE:
            # credit purchase
            return process_webhook_payment_for_credit_purchase(
                external_reference, payment_data
            )
        else:
            return {
                "response": JsonResponse({"error": "Invalid object type."}, status=404)
            }
    else:
        return {"response": JsonResponse({"error": "Invalid reference."}, status=404)}


def process_webhook_payment_for_credit_purchase(external_reference, payment_data):
    transaction_id = payment_data.get("id")
    marketplace_status = payment_data.get("status")
    amount = Decimal(payment_data["transaction_details"]["total_paid_amount"])

    internal_status = {
        "approved": CreditPurchaseStatus.APPROVED,
        "pending": CreditPurchaseStatus.ANALYSIS,
        "in_process": CreditPurchaseStatus.ANALYSIS,
        "rejected": CreditPurchaseStatus.REJECTED,
        "cancelled": CreditPurchaseStatus.CANCELED,
        "refunded": CreditPurchaseStatus.REFUNDED,
        "charged_back": CreditPurchaseStatus.CHARGED_BACK,
    }.get(marketplace_status, CreditPurchaseStatus.FAILED)

    purchase = CreditPurchase.objects.filter(token=external_reference).first()

    if purchase:
        EventLog.objects.create(
            site=Site.objects.get_current(),
            object_type=ObjectType.CREDIT_PURCHASE,
            object_id=purchase.id,
            status=internal_status,
            amount=amount,
            customer=purchase.customer,
            description=f"Webhook received for credit purchase {purchase.id} with status {internal_status} ({marketplace_status})",
        )

        purchase.status = internal_status
        purchase.save(update_fields=["status"])

        if internal_status == CreditPurchaseStatus.APPROVED:
            from apps.customer.helpers import CustomerHelper

            CustomerHelper.add_credits(
                customer=purchase.customer,
                plan=purchase.plan,
                object_id=purchase.id,
                object_type=ObjectType.CREDIT_PURCHASE,
            )

            CustomerHelper.send_credit_purchase_paid_email(purchase)

        return {"response": JsonResponse({"status": "success"}, status=200)}

    return {
        "response": JsonResponse({"error": "Credit purchase not found."}, status=404)
    }


def process_webhook_subscription(subscription_data):
    subscription_id = subscription_data.get("id")
    external_reference = subscription_data.get("external_reference")
    marketplace_status = subscription_data.get("status")

    internal_status = {
        "authorized": SubscriptionStatus.ACTIVE,
        "paused": SubscriptionStatus.SUSPENDED,
        "cancelled": SubscriptionStatus.CANCELED,
        "expired": SubscriptionStatus.CANCELED,
        "pending": SubscriptionStatus.ANALYSIS,
        "rejected": SubscriptionStatus.FAILED,
        "refunded": SubscriptionStatus.REFUNDED,
    }.get(marketplace_status, SubscriptionStatus.FAILED)

    subscription = Subscription.objects.filter(token=external_reference).first()

    if subscription:
        EventLog.objects.create(
            site=Site.objects.get_current(),
            object_type=ObjectType.SUBSCRIPTION,
            object_id=subscription.id,
            status=internal_status,
            customer=subscription.customer,
            description=f"Webhook received for subscription {subscription.id} with status {internal_status} ({marketplace_status})",
        )

        subscription.status = internal_status
        subscription.save(update_fields=["status"])

        if internal_status == SubscriptionStatus.ACTIVE:
            subscription.process_completed()
        elif internal_status == SubscriptionStatus.CANCELED:
            subscription.process_canceled()

        return {"response": JsonResponse({"status": "success"}, status=200)}

    return {"response": JsonResponse({"error": "Subscription not found."}, status=404)}


def process_cancel_for_subscription(request, subscription):
    return True


def process_payment(request):
    try:
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        # create idempotency key to prevent duplicate transactions
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(uuid.uuid4())}

        # parse json data from request body
        data = json.loads(request.body.decode("utf-8"))

        # send payment request to mercado pago
        payment_response = sdk.payment().create(data, request_options)

        return JsonResponse(payment_response, status=payment_response["status"])

    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
