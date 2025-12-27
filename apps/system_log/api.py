from django.conf import settings
from ninja import Router
from ninja.errors import HttpError

from apps.system_log.helpers import SystemLogHelper
from apps.system_log.schemas import SystemLogCreateSchema, SystemLogResponseSchema

router = Router()


@router.post("/create/", response=SystemLogResponseSchema, auth=None, by_alias=True)
def create_system_log(request, data: SystemLogCreateSchema):
    if not settings.SYSTEM_LOG_API_ENABLED:
        raise HttpError(403, "System log API is disabled")

    customer = None
    if request.user.is_authenticated and hasattr(request.user, "customer"):
        customer = request.user.customer

    SystemLogHelper.create(
        level=data.level,
        description=data.description,
        category=data.category,
        customer=customer,
    )

    return {"success": True}
