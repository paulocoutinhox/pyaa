from typing import Annotated

from django.contrib.auth import get_user_model
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pyaa.fastapi.jwt import get_user_from_token

User = get_user_model()

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """
    Dependency to get the authenticated user via JWT.
    """
    token = credentials.credentials

    try:
        user = get_user_from_token(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission: str):
    def dependency(user: CurrentUser) -> User:
        if not user.has_perm(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return user

    return dependency
