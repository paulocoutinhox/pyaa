from typing import Annotated

from asgiref.sync import sync_to_async
from django.conf import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from apps.api.system_log.schemas import SystemLogCreateSchema, SystemLogResponseSchema
from apps.system_log.helpers import SystemLogHelper

router = APIRouter()

security = HTTPBearer(auto_error=False)


@router.post("/create/", response_model=SystemLogResponseSchema)
async def create_system_log(
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
            from apps.customer.models import Customer

            user = await sync_to_async(get_current_user)(credentials)
            # try to get customer with select_related
            try:
                customer = await Customer.objects.select_related("user").aget(user=user)
            except Customer.DoesNotExist:
                pass
        except:
            pass

    await sync_to_async(SystemLogHelper.create)(
        level=data.level,
        description=data.description,
        category=data.category,
        customer=customer,
    )

    return {"success": True}
