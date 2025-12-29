from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.customer.models import Customer
from pyaa.fastapi.jwt import create_access_token

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
        mobile_phone="1234567890",
        is_active=True,
    )


@pytest.fixture
def customer(test_user):
    return Customer.objects.create(
        user=test_user,
        language_id=1,
        gender="male",
        timezone="America/Sao_Paulo",
    )


@pytest.fixture
def access_token(test_user):
    return create_access_token(test_user)


def test_create_and_get_customer(client):
    customer_data = {
        "email": "testuser3@example.com",
        "password": "testpassword",
        "firstName": "Test",
        "lastName": "User",
        "language": 1,
        "mobilePhone": "1234567890",
        "gender": "male",
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/api/customer", json=customer_data)

    assert response.status_code == 201
    data = response.json()
    assert "access" in data["token"]
    assert "refresh" in data["token"]

    access_token = data["token"]["access"]

    response = client.get(
        "/api/customer/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["firstName"] == "Test"
    assert data["user"]["lastName"] == "User"
    assert data["user"]["email"] == "testuser3@example.com"
    assert data["user"]["mobilePhone"] == "1234567890"
    assert data["gender"] == "male"


def test_get_customer_me(client, customer, access_token):
    response = client.get(
        "/api/customer/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["firstName"] == "Test"
    assert data["user"]["lastName"] == "User"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["mobilePhone"] == "1234567890"
    assert data["gender"] == "male"


def test_get_customer_me_invalid_token(client):
    response = client.get("/api/customer/me")
    assert response.status_code == 401


def test_patch_update_customer_with_patch(client, customer, access_token):
    patch_data = {
        "language": 1,
        "mobilePhone": "11111111111",
        "timezone": "America/Sao_Paulo",
    }

    response = client.patch(
        "/api/customer",
        json=patch_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["mobilePhone"] == "11111111111"


def test_patch_update_customer_with_put(client, customer, access_token):
    patch_data = {
        "language": 1,
        "mobilePhone": "22222222222",
        "timezone": "America/Sao_Paulo",
    }

    response = client.put(
        "/api/customer",
        json=patch_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["mobilePhone"] == "22222222222"


def test_update_customer_invalid_token(client):
    update_data = {
        "mobilePhone": "0987654321",
        "gender": "female",
        "language": 1,
    }

    response = client.put("/api/customer", json=update_data)
    assert response.status_code == 401


def test_patch_update_customer_invalid_token(client):
    patch_data = {
        "mobilePhone": "0987654321",
        "gender": "female",
        "language": 1,
    }

    response = client.patch("/api/customer", json=patch_data)
    assert response.status_code == 401


def test_update_customer_not_found(client, db):
    user = User.objects.create_user(
        username="testuser8@example.com",
        email="testuser8@example.com",
        password="testpassword",
        is_active=True,
    )
    access_token = create_access_token(user)

    update_data = {
        "mobilePhone": "1234567890",
        "gender": "male",
        "language": 1,
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Customer not found."


def test_create_user_validation_error(client):
    customer_data = {
        "email": "invalid-email",
        "password": "testpassword",
        "firstName": "Test",
        "lastName": "User",
        "language": 1,
        "mobilePhone": "1234567890",
        "gender": "male",
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/api/customer", json=customer_data)
    assert response.status_code == 422


@patch("apps.user.models.User.full_clean")
def test_create_user_full_clean_validation_error(mock_full_clean, client):
    mock_full_clean.side_effect = ValidationError({"email": "Invalid email format"})

    customer_data = {
        "email": "testuser10@example.com",
        "password": "testpassword",
        "firstName": "Test",
        "lastName": "User",
        "language": 1,
        "mobilePhone": "1234567890",
        "gender": "male",
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/api/customer", json=customer_data)
    assert response.status_code == 422


def test_update_customer_with_valid_password(client, customer, access_token, test_user):
    update_data = {
        "password": "NewValidPassword123",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.check_password("NewValidPassword123")


def test_update_nickname(client, customer, access_token):
    update_data = {
        "nickname": "TestNickname",
    }

    response = client.patch(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "TestNickname"

    customer.refresh_from_db()
    assert customer.nickname == "TestNickname"


def test_create_customer_without_optional_fields(client):
    customer_data = {
        "email": "testuser16@example.com",
        "password": "testpassword",
        "language": 1,
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/api/customer", json=customer_data)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["firstName"] == ""
    assert data["user"]["lastName"] == ""


def test_update_customer_individual_fields(client, customer, access_token, test_user):
    update_data = {
        "firstName": "New",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.first_name == "New"


def test_update_customer_last_name(client, customer, access_token, test_user):
    update_data = {
        "lastName": "NewLast",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.last_name == "NewLast"


def test_update_customer_email(client, customer, access_token, test_user):
    update_data = {
        "email": "newemail@example.com",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.email == "newemail@example.com"


def test_update_customer_mobile_phone(client, customer, access_token, test_user):
    update_data = {
        "mobilePhone": "9876543210",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.mobile_phone == "9876543210"


def test_update_customer_obs(client, customer, access_token):
    update_data = {
        "obs": "New observation",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    customer.refresh_from_db()
    assert customer.obs == "New observation"


def test_update_customer_timezone(client, customer, access_token):
    update_data = {
        "timezone": "America/New_York",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    customer.refresh_from_db()
    assert str(customer.timezone) == "America/New_York"


def test_update_customer_with_invalid_language(client, customer, access_token):
    update_data = {
        "language": 99999,
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    customer.refresh_from_db()
    assert customer.language_id == 1


def test_update_customer_gender(client, customer, access_token):
    update_data = {
        "gender": "female",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    customer.refresh_from_db()
    assert customer.gender == "female"


def test_update_customer_cpf(client, customer, access_token, test_user):
    update_data = {
        "cpf": "11144477735",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    test_user.refresh_from_db()
    assert test_user.cpf == "11144477735"


def test_update_customer_validation_error(client, customer, access_token, db):
    User.objects.create_user(
        username="existing@example.com",
        email="existing@example.com",
        password="testpassword",
        is_active=True,
    )

    update_data = {
        "email": "existing@example.com",
    }

    response = client.put(
        "/api/customer",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_get_customer_me_not_found(client, db):
    user = User.objects.create_user(
        username="testuser28@example.com",
        email="testuser28@example.com",
        password="testpassword",
        is_active=True,
    )
    access_token = create_access_token(user)

    response = client.get(
        "/api/customer/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Customer not found."
