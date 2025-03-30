from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone

User = get_user_model()


def populate_users():
    password = "user@123456"

    users_data = [
        {
            "id": 2,
            "site_id": 1,
            "email": "user@user.com",
            "first_name": "First",
            "last_name": "Last",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)),
            "last_login": timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0)),
            "password": make_password(password),
        },
    ]

    for user_data in users_data:
        User.objects.update_or_create(
            id=user_data["id"],
            defaults={
                "site_id": user_data["site_id"],
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "is_active": user_data["is_active"],
                "is_staff": user_data["is_staff"],
                "is_superuser": user_data["is_superuser"],
                "date_joined": user_data["date_joined"],
                "last_login": user_data["last_login"],
                "password": user_data["password"],
            },
        )


populate_users()
