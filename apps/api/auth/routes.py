from django.contrib.auth import authenticate, get_user_model
from fastapi import APIRouter, HTTPException, status

from apps.api.auth.schemas import (
    TokenObtainPairRequest,
    TokenObtainPairResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from pyaa.fastapi.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

User = get_user_model()

router = APIRouter()


@router.post(
    "/pair", response_model=TokenObtainPairResponse, status_code=status.HTTP_200_OK
)
def token_obtain_pair(data: TokenObtainPairRequest):
    user = authenticate(username=data.login, password=data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active account found with the given credentials",
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenObtainPairResponse(refresh=refresh_token, access=access_token)


@router.post(
    "/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK
)
def token_refresh(data: TokenRefreshRequest):
    try:
        payload = verify_refresh_token(data.refresh)
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        access_token = create_access_token(user)
        return TokenRefreshResponse(access=access_token)
    except (ValueError, User.DoesNotExist):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
