from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination

from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery
from apps.gallery.schemas import GalleryListSchema, GallerySchema

router = Router()


@router.get("/", response=list[GalleryListSchema], auth=None)
@paginate(LimitOffsetPagination)
def list_galleries(request):
    return Gallery.objects.filter(active=True).order_by("-published_at")


@router.get("/{tag}/", response=GallerySchema, auth=None)
def get_gallery_by_tag(request, tag: str):
    gallery = GalleryHelper.get_gallery(gallery_tag=tag)
    if not gallery:
        raise HttpError(404, "Not found")
    return gallery
