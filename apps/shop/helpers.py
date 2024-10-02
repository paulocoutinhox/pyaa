from apps.shop.enums import PaymentGateway
from apps.shop.gateways import stripe


def process_checkout(request, subscription):
    gateway = subscription.plan.gateway

    if gateway == PaymentGateway.STRIPE:
        return stripe.process_checkout(request, subscription)

    return None


def process_webhook(request, gateway):
    if gateway == PaymentGateway.STRIPE:
        return stripe.process_webhook(request)

    return None


def process_cancel(request, subscription):
    gateway = subscription.plan.gateway

    if gateway == PaymentGateway.STRIPE:
        return stripe.process_cancel(request, subscription)

    return None
