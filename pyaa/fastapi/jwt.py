from datetime import datetime, timezone
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

SIGNING_KEY = settings.AUTH_JWT["SIGNING_KEY"]
ALGORITHM = settings.AUTH_JWT["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_TIME = settings.AUTH_JWT["ACCESS_TOKEN_LIFETIME"]
REFRESH_TOKEN_EXPIRE_TIME = settings.AUTH_JWT["REFRESH_TOKEN_LIFETIME"]


def create_access_token(user: User) -> str:
    """
    Create a JWT access token for the user.
    """
    now = datetime.now(timezone.utc)
    expire = now + ACCESS_TOKEN_EXPIRE_TIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    return jwt.encode(payload, SIGNING_KEY, algorithm=ALGORITHM)


def create_refresh_token(user: User) -> str:
    """
    Create a JWT refresh token for the user.
    """
    now = datetime.now(timezone.utc)
    expire = now + REFRESH_TOKEN_EXPIRE_TIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(payload, SIGNING_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode a JWT token.
    Raises exception if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SIGNING_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Verify and decode an access token.
    Raises exception if not a valid access token.
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Token is not an access token")
    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a refresh token.
    Raises exception if not a valid refresh token.
    """
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token")
    return payload


def get_user_from_token(token: str) -> User:
    """
    Get user from an access token.
    """
    payload = verify_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise ValueError("Token does not contain user_id")

    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        raise ValueError("User not found")
