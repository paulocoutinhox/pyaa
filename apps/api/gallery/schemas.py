from datetime import datetime

from apps.api.language.schemas import LanguageSchema
from pyaa.fastapi.schemas import BaseSchema


class GalleryPhotoSchema(BaseSchema):
    image: str
    caption: str
    main: bool


class GalleryListSchema(BaseSchema):
    title: str
    tag: str
    language: LanguageSchema | None
    published_at: datetime | None
    active: bool
    photos_count: int
    main_photo: str | None


class GallerySchema(BaseSchema):
    title: str
    tag: str
    language: LanguageSchema | None
    published_at: datetime | None
    active: bool
    photos_count: int
    photos: list[GalleryPhotoSchema]
    main_photo: str | None


class PaginatedGalleryListResponse(BaseSchema):
    count: int
    items: list[GalleryListSchema]
