from ninja import ModelSchema

from apps.gallery.models import Gallery, GalleryPhoto
from apps.language.schemas import LanguageSchema
from pyaa.api.base import BaseSchema


class GalleryPhotoSchema(ModelSchema, BaseSchema):
    class Meta:
        model = GalleryPhoto
        fields = ["id", "image", "caption", "main"]


class GalleryListSchema(ModelSchema, BaseSchema):
    language: LanguageSchema | None
    photos_count: int
    main_photo: str | None

    class Meta:
        model = Gallery
        fields = ["id", "title", "tag", "language", "published_at", "active"]

    @staticmethod
    def resolve_photos_count(obj):
        return obj.gallery_photos.count()

    @staticmethod
    def resolve_main_photo(obj, context):
        request = context.get("request")
        return obj.get_main_photo_url(request)


class GallerySchema(ModelSchema, BaseSchema):
    language: LanguageSchema | None
    photos_count: int
    photos: list[GalleryPhotoSchema]
    main_photo: str | None

    class Meta:
        model = Gallery
        fields = ["id", "title", "tag", "language", "published_at", "active"]

    @staticmethod
    def resolve_photos_count(obj):
        return obj.gallery_photos.count()

    @staticmethod
    def resolve_photos(obj):
        return list(obj.gallery_photos.all())

    @staticmethod
    def resolve_main_photo(obj, context):
        request = context.get("request")
        return obj.get_main_photo_url(request)
