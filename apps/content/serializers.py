from rest_framework import serializers

from apps.content.models import Content, ContentCategory
from apps.language.serializers import LanguageSerializer


class ContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentCategory
        fields = [
            "id",
            "name",
            "tag",
        ]


class ContentSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    category = ContentCategorySerializer(read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "category",
            "tag",
            "content",
            "language",
            "published_at",
            "active",
        ]
