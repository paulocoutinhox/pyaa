import pytest
from django.contrib.auth import get_user_model

from pyaa.fastapi.jwt import create_refresh_token

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User",
        is_active=True,
    )


def test_token_obtain_pair_success(client, test_user):
    response = client.post(
        "/api/token/pair",
        json={"login": "testuser@example.com", "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert isinstance(data["access"], str)
    assert isinstance(data["refresh"], str)


def test_token_obtain_pair_invalid_credentials(client):
    response = client.post(
        "/api/token/pair",
        json={"login": "invalid@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "No active account found with the given credentials"


def test_token_obtain_pair_wrong_password(client, test_user):
    response = client.post(
        "/api/token/pair",
        json={"login": "testuser@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "No active account found with the given credentials"


def test_token_refresh_success(client, test_user):
    refresh_token = create_refresh_token(test_user)

    response = client.post(
        "/api/token/refresh",
        json={"refresh": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert isinstance(data["access"], str)


def test_token_refresh_invalid_token(client):
    response = client.post(
        "/api/token/refresh",
        json={"refresh": "invalid.token.here"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Token is invalid or expired"


def test_token_refresh_access_token_instead_of_refresh(client, test_user):
    from pyaa.fastapi.jwt import create_access_token

    access_token = create_access_token(test_user)

    response = client.post(
        "/api/token/refresh",
        json={"refresh": access_token},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Token is invalid or expired"


def test_token_refresh_nonexistent_user(client, test_user):
    refresh_token = create_refresh_token(test_user)
    user_id = test_user.id
    test_user.delete()

    response = client.post(
        "/api/token/refresh",
        json={"refresh": refresh_token},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Token is invalid or expired"


def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/api/customer/me", headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_get_current_user_with_deleted_user(client, test_user, db):
    from pyaa.fastapi.jwt import create_access_token

    access_token = create_access_token(test_user)
    user_id = test_user.id
    test_user.delete()

    response = client.get(
        "/api/customer/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "User not found"
