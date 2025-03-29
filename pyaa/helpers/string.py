import re
import uuid


class StringHelper:
    @staticmethod
    def only_numbers(value):
        if value:
            data = re.sub("[^0-9]", "", value)
            return data
        else:
            return None

    @staticmethod
    def generate_subscription_token():
        return f"subscription.{uuid.uuid4()}"

    @staticmethod
    def generate_credit_purchase_token():
        return f"credit-purchase.{uuid.uuid4()}"
