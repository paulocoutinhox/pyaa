from fastapi import APIRouter, HTTPException, Query, status

from apps.api.gallery.schemas import (
    GalleryListSchema,
    GallerySchema,
    PaginatedGalleryListResponse,
)
from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery

router = APIRouter()


@router.get("/", response_model=PaginatedGalleryListResponse)
def list_galleries(limit: int = Query(100, ge=1), offset: int = Query(0, ge=0)):
    queryset = Gallery.objects.filter(active=True).order_by("-published_at")
    total_count = queryset.count()
    galleries = list(queryset[offset : offset + limit])

    # prepare data for schemas
    items = []
    for gallery in galleries:
        gallery_dict = {
            "title": gallery.title,
            "tag": gallery.tag,
            "language": (
                {
                    "id": gallery.language.id,
                    "name": gallery.language.name,
                    "native_name": gallery.language.native_name,
                    "code_iso_639_1": gallery.language.code_iso_639_1,
                    "code_iso_language": gallery.language.code_iso_language,
                }
                if gallery.language
                else None
            ),
            "published_at": gallery.published_at,
            "active": gallery.active,
            "photos_count": gallery.gallery_photos.count(),
            "main_photo": gallery.get_main_photo_url(None),
        }
        items.append(GalleryListSchema(**gallery_dict))

    return PaginatedGalleryListResponse(count=total_count, items=items)


@router.get("/{tag}/", response_model=GallerySchema)
def get_gallery_by_tag(tag: str):
    gallery = GalleryHelper.get_gallery(gallery_tag=tag)
    if not gallery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    # prepare data for schema
    photos = []
    for photo in gallery.gallery_photos.all():
        photo_dict = {
            "image": photo.image.url if photo.image else "",
            "caption": photo.caption,
            "main": photo.main,
        }
        photos.append(photo_dict)

    gallery_dict = {
        "title": gallery.title,
        "tag": gallery.tag,
        "language": (
            {
                "name": gallery.language.name,
                "native_name": gallery.language.native_name,
                "code_iso_639_1": gallery.language.code_iso_639_1,
                "code_iso_language": gallery.language.code_iso_language,
            }
            if gallery.language
            else None
        ),
        "published_at": gallery.published_at,
        "active": gallery.active,
        "photos_count": gallery.gallery_photos.count(),
        "photos": photos,
        "main_photo": gallery.get_main_photo_url(None),
    }

    return GallerySchema(**gallery_dict)
