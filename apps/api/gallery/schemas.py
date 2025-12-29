from datetime import datetime
from typing import Any

from pydantic import field_serializer

from apps.api.language.schemas import LanguageSchema
from pyaa.fastapi.schemas import BaseSchema


class GalleryPhotoSchema(BaseSchema):
    image: Any
    caption: str
    main: bool

    @field_serializer("image")
    def serialize_image(self, image) -> str:
        return image.url if image else ""


class GalleryListSchema(BaseSchema):
    title: str
    tag: str
    language: LanguageSchema | None
    published_at: datetime | None
    active: bool
    photos_count: int = 0
    main_photo: str | None = None


class GallerySchema(BaseSchema):
    title: str
    tag: str
    language: LanguageSchema | None
    published_at: datetime | None
    active: bool
    photos_count: int = 0
    photos: list[GalleryPhotoSchema] = []
    main_photo: str | None = None


class PaginatedGalleryListResponse(BaseSchema):
    count: int
    items: list[GalleryListSchema]
