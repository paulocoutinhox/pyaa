from fastapi import APIRouter, HTTPException, status

from apps.api.banner.schemas import BannerAccessResponseSchema, BannerSchema
from apps.banner.enums import BannerAccessType
from apps.banner.helpers import BannerHelper

router = APIRouter()


@router.get("/", response_model=list[BannerSchema])
def list_banners(zone: str, language: str = None, site: int = None):
    banners = BannerHelper.get_banners(zone=zone, language=language, site_id=site)
    return [
        BannerSchema(
            title=banner.title,
            image=banner.image.url if banner.image else "",
            link=banner.link,
            target_blank=banner.target_blank,
            zone=banner.zone,
            token=banner.token,
            sort_order=banner.sort_order,
            start_at=banner.start_at,
            end_at=banner.end_at,
        )
        for banner in banners
    ]


@router.get("/access/{token}/", response_model=BannerAccessResponseSchema)
def track_banner_access(token: str, type: str):
    from apps.banner.models import BannerAccess

    banner = BannerHelper.get_banner_by_token(token)
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found"
        )

    if type == BannerAccessType.VIEW.value:
        access_type = BannerAccessType.VIEW
    elif type == BannerAccessType.CLICK.value:
        access_type = BannerAccessType.CLICK
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access type"
        )

    BannerAccess.objects.create(
        banner=banner, access_type=access_type, ip_address="127.0.0.1", country_code=""
    )

    return {"success": True}
