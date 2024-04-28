import stripe
from django.shortcuts import redirect
from django.urls import path

from pyaa import settings


def create_view(request):
    try:
        base_url = "{0}://{1}".format(request.scheme, request.get_host())

        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": settings.SUBSCRIPTION_PLANS["premium-monthly"]["code"],
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=base_url + "/subscription/success.html",
            cancel_url=base_url + "/subscription/cancel.html",
        )
    except Exception as e:
        print(e)
        pass

    return redirect(checkout_session.url, code=200)


urlpatterns = [
    path(
        "subscription/create",
        create_view,
        name="subscription_create",
    ),
]
