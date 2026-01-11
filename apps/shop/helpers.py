from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils.translation import get_language

from apps.shop.enums import ObjectType, PaymentGateway
from apps.shop.gateways import stripe
from apps.shop.models import CreditPurchase, Plan, ProductPurchase, Subscription


class ShopHelper:
    @staticmethod
    def process_checkout_for_subscription(request, subscription):
        gateway = subscription.plan.gateway

        if gateway == PaymentGateway.STRIPE:
            return stripe.process_checkout_for_subscription(request, subscription)

        return None

    @staticmethod
    def process_checkout_for_credit_purchase(request, purchase):
        gateway = purchase.plan.gateway

        if gateway == PaymentGateway.STRIPE:
            return stripe.process_checkout_for_credit_purchase(request, purchase)

        return None

    @staticmethod
    def process_checkout_for_product_purchase(request, purchase):
        # for product purchases, we'll use the default gateway
        gateway = settings.GATEWAY_FOR_PRODUCT_PURCHASE

        if gateway == PaymentGateway.STRIPE:
            return stripe.process_checkout_for_product_purchase(request, purchase)

        return None

    @staticmethod
    def process_cancel_for_subscription(request, subscription):
        gateway = subscription.plan.gateway

        if gateway == PaymentGateway.STRIPE:
            return stripe.process_cancel_for_subscription(request, subscription)

        return None

    @staticmethod
    def process_webhook(request, gateway):
        if gateway == PaymentGateway.STRIPE:
            return stripe.process_webhook(request)

        return None

    @staticmethod
    def get_plans_by_type(plan_type=None, cache_time=60):
        """
        Fetches plans filtered by plan type, site, and language. If plan_type is None, fetches all active plans.
        The results are cached to improve performance.

        :param plan_type: the type of the plan to filter (optional).
        :param cache_time: cache expiration time in seconds (default is 60 seconds).
        :return: a queryset of filtered and ordered plans.
        """
        # get the current site ID from settings
        site_id = settings.SITE_ID

        # get user language
        user_language = get_language()

        if user_language:
            user_language = user_language.lower()

        # generate a unique cache key based on plan_type, site_id, and language
        cache_key = f"plans_site_{site_id}_type_{plan_type if plan_type else 'all'}_lang_{user_language}"

        # attempt to retrieve the plans from cache
        cached_plans = cache.get(cache_key)

        if cached_plans is not None:
            return cached_plans

        # build the query to filter plans
        filters = Q(active=True)
        filters &= Q(site_id=site_id) | Q(site_id__isnull=True)

        if plan_type is not None:
            filters &= Q(plan_type=plan_type)

        # fetch plans from the database with language priority
        plans = (
            Plan.objects.filter(filters)
            .select_related("language")
            .order_by(
                models.Case(
                    # priority to plans in user's language
                    models.When(
                        models.Q(language__code_iso_language=user_language)
                        | models.Q(language__code_iso_639_1=user_language),
                        then=0,
                    ),
                    # fallback to en-us
                    models.When(
                        models.Q(language__code_iso_language="en-us")
                        | models.Q(language__code_iso_639_1="en"),
                        then=1,
                    ),
                    # global plans (language=None)
                    models.When(language__isnull=True, then=2),
                    default=models.Value(3),
                    output_field=models.IntegerField(),
                ),
                "sort_order",
            )
            .all()
        )

        # store the result in cache
        cache.set(cache_key, plans, cache_time)

        return plans

    @staticmethod
    def get_item_by_token(token, customer):
        # validate
        if not token:
            return None

        if not customer:
            return None

        # token parts
        token_parts = token.split(".")

        if len(token_parts) < 2:
            return None

        object_type = token_parts[0]
        object_id = token_parts[1]

        # find object
        if object_type == ObjectType.CREDIT_PURCHASE:
            return CreditPurchase.objects.filter(
                token=token,
                customer=customer,
            ).first()
        elif object_type == ObjectType.SUBSCRIPTION:
            return Subscription.objects.filter(
                token=token,
                customer=customer,
            ).first()
        elif object_type == ObjectType.PRODUCT_PURCHASE:
            return ProductPurchase.objects.filter(
                token=token,
                customer=customer,
            ).first()

        return None

    @staticmethod
    def get_item_type_by_token(token):
        # validate
        if not token:
            return None

        # token parts
        token_parts = token.split(".")

        return token_parts[0]
