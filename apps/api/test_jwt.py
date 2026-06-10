from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest
from django.contrib.auth import get_user_model

from pyaa.fastapi import jwt as jwt_module
from pyaa.fastapi.jwt import (
    ALGORITHM,
    SIGNING_KEY,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_from_token,
    verify_access_token,
    verify_refresh_token,
)

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="jwtuser@example.com",
        email="jwtuser@example.com",
        password="testpassword123",
        first_name="Jwt",
        last_name="User",
        is_active=True,
    )


def _encode(payload: dict, key: str = SIGNING_KEY) -> str:
    return pyjwt.encode(payload, key, algorithm=ALGORITHM)


def test_create_access_token_has_access_type(test_user):
    token = create_access_token(test_user)
    payload = decode_token(token)

    assert payload["type"] == "access"
    assert payload["user_id"] == test_user.id
    assert payload["email"] == test_user.email


def test_create_refresh_token_has_refresh_type(test_user):
    token = create_refresh_token(test_user)
    payload = decode_token(token)

    assert payload["type"] == "refresh"
    assert payload["user_id"] == test_user.id
    assert payload["email"] == test_user.email


def test_decode_token_valid(test_user):
    token = create_access_token(test_user)
    payload = decode_token(token)

    assert payload["user_id"] == test_user.id


def test_decode_token_expired():
    now = datetime.now(timezone.utc)
    expired = _encode(
        {
            "user_id": 1,
            "email": "x@example.com",
            "exp": now - timedelta(minutes=5),
            "iat": now - timedelta(minutes=10),
            "type": "access",
        }
    )

    with pytest.raises(ValueError, match="Token expired"):
        decode_token(expired)


def test_decode_token_invalid_signature():
    now = datetime.now(timezone.utc)
    token = _encode(
        {
            "user_id": 1,
            "exp": now + timedelta(minutes=5),
            "iat": now,
            "type": "access",
        },
        key="some-other-signing-key",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        decode_token(token)


def test_decode_token_malformed():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token("not.a.valid.token")


def test_verify_access_token_valid(test_user):
    token = create_access_token(test_user)
    payload = verify_access_token(token)

    assert payload["type"] == "access"


def test_verify_access_token_rejects_refresh_token(test_user):
    token = create_refresh_token(test_user)

    with pytest.raises(ValueError, match="Token is not an access token"):
        verify_access_token(token)


def test_verify_refresh_token_valid(test_user):
    token = create_refresh_token(test_user)
    payload = verify_refresh_token(token)

    assert payload["type"] == "refresh"


def test_verify_refresh_token_rejects_access_token(test_user):
    token = create_access_token(test_user)

    with pytest.raises(ValueError, match="Token is not a refresh token"):
        verify_refresh_token(token)


def test_get_user_from_token_valid(test_user):
    token = create_access_token(test_user)
    user = get_user_from_token(token)

    assert user.id == test_user.id


def test_get_user_from_token_rejects_inactive_user(test_user):
    token = create_access_token(test_user)

    test_user.is_active = False
    test_user.save(update_fields=["is_active"])

    with pytest.raises(ValueError, match="User is inactive"):
        get_user_from_token(token)


def test_get_user_from_token_missing_user_id(db):
    now = datetime.now(timezone.utc)
    token = _encode(
        {
            "email": "x@example.com",
            "exp": now + timedelta(minutes=5),
            "iat": now,
            "type": "access",
        }
    )

    with pytest.raises(ValueError, match="Token does not contain user_id"):
        get_user_from_token(token)


def test_get_user_from_token_nonexistent_user(db):
    now = datetime.now(timezone.utc)
    token = _encode(
        {
            "user_id": 999999,
            "email": "x@example.com",
            "exp": now + timedelta(minutes=5),
            "iat": now,
            "type": "access",
        }
    )

    with pytest.raises(ValueError, match="User not found"):
        get_user_from_token(token)
