from datetime import datetime

from django.conf import settings
from django.utils import timezone

from apps.customer.models import Customer


def populate_customers():
    customers_data = [
        {
            "id": 1,
            "site_id": 1,
            "user_id": 2,
            "language_id": 2,
            "updated_at": timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)),
            "created_at": timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)),
            "obs": None,
            "avatar": None,
            "gender": "male",
            "nickname": "Paulo Coutinho",
            "timezone": settings.DEFAULT_TIME_ZONE,
        },
    ]

    for customer_data in customers_data:
        Customer.objects.update_or_create(
            id=customer_data["id"],
            defaults={
                "site_id": customer_data["site_id"],
                "user_id": customer_data["user_id"],
                "language_id": customer_data["language_id"],
                "updated_at": customer_data["updated_at"],
                "created_at": customer_data["created_at"],
                "timezone": customer_data["timezone"],
                "obs": customer_data["obs"],
                "avatar": customer_data["avatar"],
                "gender": customer_data["gender"],
                "nickname": customer_data["nickname"],
            },
        )


populate_customers()
