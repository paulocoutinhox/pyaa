from datetime import date, datetime

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


class ContentCreateSchema(BaseSchema):
    title: str
    content: str = ""
    tag: str | None = None
    category_id: int | None = None
    language_id: int | None = None
    published_at: date | None = None
    active: bool = True
