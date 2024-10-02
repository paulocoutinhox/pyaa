from rest_framework import serializers

from apps.content.models import Content


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "tag",
            "content",
            "language",
            "published_at",
            "active",
        ]
