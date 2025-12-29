from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.customer.models import Customer
from apps.system_log.enums import LogLevel
from apps.system_log.models import SystemLog
from pyaa.fastapi.jwt import create_access_token

User = get_user_model()


@override_settings(SYSTEM_LOG_API_ENABLED=True)
def test_create_system_log(client):
    log_data = {
        "level": LogLevel.INFO,
        "description": "Test log entry",
        "category": "test",
    }

    response = client.post("/api/system-log/create", json=log_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    assert SystemLog.objects.filter(description="Test log entry").exists()


@override_settings(SYSTEM_LOG_API_ENABLED=False)
def test_create_system_log_api_disabled(client):
    log_data = {
        "level": LogLevel.INFO,
        "description": "Test log entry",
        "category": "test",
    }

    response = client.post("/api/system-log/create", json=log_data)

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "System log API is disabled"


@override_settings(SYSTEM_LOG_API_ENABLED=True)
def test_create_system_log_with_different_levels(client, db):
    SystemLog.objects.all().delete()

    for level in [LogLevel.ERROR, LogLevel.WARNING]:
        log_data = {
            "level": level,
            "description": f"{level} log",
            "category": "test",
        }

        response = client.post("/api/system-log/create", json=log_data)
        assert response.status_code == 200

    assert SystemLog.objects.count() == 2


@override_settings(SYSTEM_LOG_API_ENABLED=True)
def test_create_system_log_with_authenticated_user(client, db):
    user = User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="testpassword",
        is_active=True,
    )

    customer = Customer.objects.create(
        user=user,
        language_id=1,
        gender="male",
    )

    access_token = create_access_token(user)

    log_data = {
        "level": LogLevel.INFO,
        "description": "Authenticated user log",
        "category": "test",
    }

    response = client.post(
        "/api/system-log/create",
        json=log_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    log = SystemLog.objects.get(description="Authenticated user log")
    assert log.customer == customer


@override_settings(SYSTEM_LOG_API_ENABLED=True)
def test_create_system_log_with_user_without_customer(client):
    user = User.objects.create_user(
        username="testuser2@example.com",
        email="testuser2@example.com",
        password="testpassword",
        is_active=True,
    )

    access_token = create_access_token(user)

    log_data = {
        "level": LogLevel.INFO,
        "description": "User without customer log",
        "category": "test",
    }

    response = client.post(
        "/api/system-log/create",
        json=log_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    log = SystemLog.objects.get(description="User without customer log")
    assert log.customer is None


@override_settings(SYSTEM_LOG_API_ENABLED=True)
def test_create_system_log_with_invalid_token(client):
    log_data = {
        "level": LogLevel.INFO,
        "description": "Invalid token log",
        "category": "test",
    }

    response = client.post(
        "/api/system-log/create",
        json=log_data,
        headers={"Authorization": "Bearer invalid.token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    log = SystemLog.objects.get(description="Invalid token log")
    assert log.customer is None
