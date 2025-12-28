from asgiref.sync import sync_to_async
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
async def list_galleries(limit: int = Query(100, ge=1), offset: int = Query(0, ge=0)):
    queryset = (
        Gallery.objects.filter(active=True)
        .select_related("language")
        .order_by("-published_at")
    )
    total_count = await queryset.acount()
    galleries = await sync_to_async(list)(queryset[offset : offset + limit])

    # prepare data for schemas
    items = []
    for gallery in galleries:
        photos_count = await gallery.gallery_photos.acount()
        main_photo = await sync_to_async(gallery.get_main_photo_url)(None)
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
            "photos_count": photos_count,
            "main_photo": main_photo,
        }
        items.append(GalleryListSchema(**gallery_dict))

    return PaginatedGalleryListResponse(count=total_count, items=items)


@router.get("/{tag}/", response_model=GallerySchema)
async def get_gallery_by_tag(tag: str):
    gallery = await sync_to_async(GalleryHelper.get_gallery)(gallery_tag=tag)
    if not gallery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    # prepare data for schema
    photos = []
    async for photo in gallery.gallery_photos.all():
        photo_dict = {
            "image": photo.image.url if photo.image else "",
            "caption": photo.caption,
            "main": photo.main,
        }
        photos.append(photo_dict)

    photos_count = await gallery.gallery_photos.acount()
    main_photo = await sync_to_async(gallery.get_main_photo_url)(None)
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
        "photos_count": photos_count,
        "photos": photos,
        "main_photo": main_photo,
    }

    return GallerySchema(**gallery_dict)
