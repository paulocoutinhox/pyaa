from django.conf import settings
from django.core.cache import cache
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
        First tries to fetch plans for the user's language. If no plans are found, falls back to general plans.

        :param plan_type: the type of the plan to filter (optional).
        :param cache_time: cache expiration time in seconds (default is 60 seconds).
        :return: a queryset of filtered and ordered plans.
        """
        # get the current site from settings
        site_id = settings.SITE_ID

        # get user language
        user_language = get_language()

        if user_language:
            user_language = user_language.lower()

        # build the base query to filter plans
        base_filters = Q(active=True)
        base_filters &= Q(site_id=site_id) | Q(site_id__isnull=True)

        if plan_type is not None:
            base_filters &= Q(plan_type=plan_type)

        # first, try to fetch plans for the user's language
        if user_language:
            # generate cache key for language-specific plans
            cache_key = f"plans_site_{site_id}_type_{plan_type if plan_type else 'all'}_lang_{user_language}"

            # attempt to retrieve the plans from cache
            cached_plans = cache.get(cache_key)

            if cached_plans is not None:
                return cached_plans

            language_filters = base_filters & (
                Q(language__code_iso_language=user_language)
                | Q(language__code_iso_639_1=user_language)
            )

            plans_queryset = (
                Plan.objects.filter(language_filters)
                .select_related("language")
                .order_by("sort_order")
            )

            # check if any plans exist before evaluating the queryset
            if plans_queryset.exists():
                plans = plans_queryset.all()
                # store the result in cache with language-specific key
                cache.set(cache_key, plans, cache_time)
                return plans
            else:
                # if no plans found for the language, fall back to general plans
                # use a different cache key for general plans (not language-specific)
                general_cache_key = f"plans_site_{site_id}_type_{plan_type if plan_type else 'all'}_lang_general"

                # attempt to retrieve general plans from cache
                cached_general_plans = cache.get(general_cache_key)

                if cached_general_plans is not None:
                    return cached_general_plans

                general_filters = base_filters & Q(language__isnull=True)

                plans = (
                    Plan.objects.filter(general_filters)
                    .select_related("language")
                    .order_by("sort_order")
                    .all()
                )

                # store the result in cache with general key
                cache.set(general_cache_key, plans, cache_time)
                return plans
        else:
            # if no language is set, fetch general plans
            # use cache key for general plans
            general_cache_key = f"plans_site_{site_id}_type_{plan_type if plan_type else 'all'}_lang_general"

            # attempt to retrieve general plans from cache
            cached_general_plans = cache.get(general_cache_key)

            if cached_general_plans is not None:
                return cached_general_plans

            general_filters = base_filters & Q(language__isnull=True)

            plans = (
                Plan.objects.filter(general_filters)
                .select_related("language")
                .order_by("sort_order")
                .all()
            )

            # store the result in cache
            cache.set(general_cache_key, plans, cache_time)
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

        if len(token_parts) < 2:
            return None

        return token_parts[0]
