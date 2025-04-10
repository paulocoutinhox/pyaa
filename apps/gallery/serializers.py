from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.gallery.models import Gallery, GalleryPhoto
from apps.language.serializers import LanguageSerializer


class GalleryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryPhoto
        fields = ["id", "image", "caption", "main"]


class GallerySerializer(serializers.ModelSerializer):
    photos = GalleryPhotoSerializer(many=True, read_only=True, source="gallery_photos")
    main_photo = serializers.SerializerMethodField()
    language = LanguageSerializer(read_only=True)
    photos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Gallery
        fields = [
            "id",
            "title",
            "tag",
            "language",
            "published_at",
            "photos_count",
            "photos",
            "main_photo",
            "active",
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_photo(self, obj) -> str:
        request = self.context.get("request")
        return obj.get_main_photo_url(request)


class GalleryListSerializer(serializers.ModelSerializer):
    main_photo = serializers.SerializerMethodField()
    language = LanguageSerializer(read_only=True)
    photos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Gallery
        fields = [
            "id",
            "title",
            "tag",
            "language",
            "published_at",
            "photos_count",
            "main_photo",
            "active",
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_photo(self, obj) -> str:
        request = self.context.get("request")
        return obj.get_main_photo_url(request)
