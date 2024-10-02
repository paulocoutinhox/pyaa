from rest_framework import serializers

from apps.gallery.models import Gallery, GalleryPhoto


class GalleryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryPhoto
        fields = ["id", "image", "caption", "main"]


class GallerySerializer(serializers.ModelSerializer):
    photos = GalleryPhotoSerializer(many=True, read_only=True, source="gallery_photos")
    main_photo = serializers.SerializerMethodField()

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

    def get_main_photo(self, obj):
        request = self.context.get("request")
        return obj.get_main_photo_url(request)


class GalleryListSerializer(serializers.ModelSerializer):
    main_photo = serializers.SerializerMethodField()

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

    def get_main_photo(self, obj):
        request = self.context.get("request")
        return obj.get_main_photo_url(request)
