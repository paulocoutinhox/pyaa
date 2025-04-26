import json

from django.conf import settings
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.shop.enums import PaymentGateway
from apps.shop.helpers import ShopHelper
from apps.system_log.enums import LogLevel
from apps.system_log.helpers import SystemLogHelper


@csrf_exempt
def webhook_stripe_view(request):
    if settings.WEBHOOK_LOG_REQUESTS:
        # capturing request data
        request_headers = dict(request.headers)
        request_body = request.body.decode("utf-8") if request.body else None
        request_query_params = dict(request.GET)
        request_post_data = dict(request.POST)

        # creating a log entry with request details
        SystemLogHelper.create(
            level=LogLevel.DEBUG,
            category="stripe-webhook",
            description=f"Stripe webhook received with the following details:\n"
            f"Headers: {json.dumps(request_headers, indent=2)}\n"
            f"Body: {request_body}\n"
            f"Query Params: {json.dumps(request_query_params, indent=2)}\n"
            f"POST Data: {json.dumps(request_post_data, indent=2)}",
        )

    # processing the webhook
    webhook_data = ShopHelper.process_webhook(
        request,
        PaymentGateway.STRIPE,
    )

    # returning the response
    return webhook_data["response"]


urlpatterns = [
    path(
        "shop/webhook/stripe/",
        webhook_stripe_view,
        name="shop_webhook_stripe",
    ),
]
