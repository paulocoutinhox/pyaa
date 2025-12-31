from asgiref.sync import sync_to_async
from django.contrib.sites.models import Site
from fastapi import APIRouter

from apps.api.shop.schemas import PlanSchema
from apps.shop.models import Plan

router = APIRouter()


@router.get("/plan", response_model=list[PlanSchema])
async def list_plans(
    gateway: str | None = None,
    site: int | None = None,
    active: bool | None = None,
):
    """
    List all plans with optional filters.

    Args:
        gateway: Filter by gateway
        site: Filter by site ID
        active: Filter by active status

    Returns:
        List of plans matching the filters
    """

    def _get_plans():
        queryset = Plan.objects.all()

        if gateway:
            queryset = queryset.filter(gateway=gateway)

        if site:
            try:
                site_obj = Site.objects.get(id=site)
                queryset = queryset.filter(site=site_obj)
            except Site.DoesNotExist:
                pass

        if active is not None:
            queryset = queryset.filter(active=active)

        return list(queryset.order_by("sort_order", "name"))

    plans = await sync_to_async(_get_plans)()

    return [PlanSchema.model_validate(plan) for plan in plans]
