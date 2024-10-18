from django.conf import settings
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Coalesce

from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog


class CustomerHelper:
    @staticmethod
    @transaction.atomic
    def post_save(customer: Customer):
        # add initial credits
        customer, log = CustomerHelper.add_credits(
            customer,
            settings.CUSTOMER_INITIAL_CREDITS,
            False,
            True,
            0,
            ObjectType.BONUS,
        )

        return customer, log

    @staticmethod
    @transaction.atomic
    def add_credits(
        customer, amount, is_refund=False, add_log=False, object_id=0, object_type=None
    ):
        if amount == 0:
            return customer, None

        # ensure credits is treated as 0 if it's null
        current_credits = Coalesce(F("credits"), Value(0))

        log_entry = None

        # atomically check and update credits
        if amount < 0:
            # attempt to deduct credits only if sufficient credits are available
            updated_rows = Customer.objects.filter(
                id=customer.id, credits__gte=abs(amount)
            ).update(credits=current_credits + amount)

            if updated_rows == 0:
                # not enough credits to deduct, return customer without log
                return customer, None
        else:
            # add credits without any condition
            Customer.objects.filter(id=customer.id).update(
                credits=current_credits + amount
            )

        # refresh the customer instance to reflect the updated credits
        customer.refresh_from_db()

        # optionally log the credit change
        if add_log:
            log_entry = CreditLog.objects.create(
                object_id=object_id,
                object_type=object_type,
                customer=customer,
                amount=amount,
                is_refund=is_refund,
            )

        # return the customer and the log entry (if created)
        return customer, log_entry
