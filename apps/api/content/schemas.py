from datetime import datetime

from apps.api.language.schemas import LanguageSchema
from pyaa.fastapi.schemas import BaseSchema


class ContentCategorySchema(BaseSchema):
    id: int
    name: str
    tag: str


class ContentSchema(BaseSchema):
    id: int
    title: str
    category: ContentCategorySchema | None
    tag: str
    content: str
    language: LanguageSchema | None
    published_at: datetime | None
    active: bool
