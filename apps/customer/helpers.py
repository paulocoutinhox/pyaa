from django.conf import settings
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Coalesce

from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog, Subscription


class CustomerHelper:
    @staticmethod
    @transaction.atomic
    def post_save(customer: Customer):
        # add initial credits
        CustomerHelper.add_credits(
            customer,
            settings.CUSTOMER_INITIAL_CREDITS,
            True,
            0,
            ObjectType.BONUS,
        )

        return customer

    @staticmethod
    @transaction.atomic
    def add_credits(customer, amount, add_log=False, object_id=0, object_type=None):
        if amount == 0:
            return

        customer.credits = Coalesce(F("credits"), Value(0)) + amount
        customer.save(update_fields=["credits"])

        if add_log:
            CreditLog.objects.create(
                object_id=object_id,
                object_type=object_type,
                customer=customer,
                amount=amount,
            )

        return customer
