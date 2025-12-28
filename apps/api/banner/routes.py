from fastapi import APIRouter, HTTPException, status

from apps.api.banner.schemas import BannerAccessResponseSchema, BannerSchema
from apps.banner.enums import BannerAccessType
from apps.banner.helpers import BannerHelper

router = APIRouter()


@router.get("/", response_model=list[BannerSchema])
def list_banners(zone: str, language: str = None, site: int = None):
    banners = BannerHelper.get_banners(zone=zone, language=language, site_id=site)
    return list(banners)


@router.get("/access/{token}/", response_model=BannerAccessResponseSchema)
def track_banner_access(token: str, type: str):
    banner = BannerHelper.get_banner_by_token(token)
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found"
        )

    if type == BannerAccessType.VIEW.value:
        tracked = BannerHelper.track_banner_access(None, banner, BannerAccessType.VIEW)
    elif type == BannerAccessType.CLICK.value:
        tracked = BannerHelper.track_banner_access(None, banner, BannerAccessType.CLICK)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access type"
        )

    return {"success": tracked}
