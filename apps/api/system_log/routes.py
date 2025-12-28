from typing import Annotated

from django.conf import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from apps.api.system_log.schemas import SystemLogCreateSchema, SystemLogResponseSchema
from apps.system_log.helpers import SystemLogHelper

router = APIRouter()

security = HTTPBearer(auto_error=False)


@router.post("/create/", response_model=SystemLogResponseSchema)
def create_system_log(
    data: SystemLogCreateSchema,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ] = None,
):
    if not settings.SYSTEM_LOG_API_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="System log API is disabled"
        )

    customer = None
    if credentials:
        # try to get the customer if authenticated
        try:
            from apps.api.auth.dependencies import get_current_user

            user = get_current_user(credentials)
            if hasattr(user, "customer"):
                customer = user.customer
        except:
            pass

    SystemLogHelper.create(
        level=data.level,
        description=data.description,
        category=data.category,
        customer=customer,
    )

    return {"success": True}
