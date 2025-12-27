from ninja import Router
from ninja.errors import HttpError

from apps.banner.enums import BannerAccessType
from apps.banner.helpers import BannerHelper
from apps.banner.schemas import BannerAccessResponseSchema, BannerSchema

router = Router()


@router.get("/", response=list[BannerSchema], auth=None, by_alias=True)
def list_banners(request, zone: str, language: str = None, site: int = None):
    banners = BannerHelper.get_banners(zone=zone, language=language, site_id=site)
    return list(banners)


@router.get(
    "/access/{token}/", response=BannerAccessResponseSchema, auth=None, by_alias=True
)
def track_banner_access(request, token: str, type: str):
    banner = BannerHelper.get_banner_by_token(token)
    if not banner:
        raise HttpError(404, "Banner not found")

    if type == BannerAccessType.VIEW.value:
        tracked = BannerHelper.track_banner_access(
            request, banner, BannerAccessType.VIEW
        )
    elif type == BannerAccessType.CLICK.value:
        tracked = BannerHelper.track_banner_access(
            request, banner, BannerAccessType.CLICK
        )
    else:
        raise HttpError(400, "Invalid access type")

    return {"success": tracked}
