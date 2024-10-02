from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.shop import helpers as gh
from apps.shop.enums import PaymentGateway


@csrf_exempt
def webhook_stripe_view(request):
    webhook_data = gh.process_webhook(request, PaymentGateway.STRIPE)
    return webhook_data["response"]


urlpatterns = [
    path(
        "shop/webhook/stripe/",
        webhook_stripe_view,
        name="shop_webhook_stripe",
    ),
]
