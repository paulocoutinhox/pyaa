from ninja import ModelSchema

from apps.content.models import Content, ContentCategory
from apps.language.schemas import LanguageSchema
from pyaa.api.base import BaseSchema


class ContentCategorySchema(ModelSchema, BaseSchema):
    class Meta:
        model = ContentCategory
        fields = ["id", "name", "tag"]


class ContentSchema(ModelSchema, BaseSchema):
    category: ContentCategorySchema | None
    language: LanguageSchema | None

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
