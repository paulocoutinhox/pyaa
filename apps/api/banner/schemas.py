from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import field_serializer

from pyaa.fastapi.schemas import BaseSchema


class BannerSchema(BaseSchema):
    title: str
    image: Any
    link: str | None
    target_blank: bool
    zone: str
    token: UUID
    sort_order: int
    start_at: datetime | None
    end_at: datetime | None

    @field_serializer("image")
    def serialize_image(self, image) -> str:
        return image.url if image else ""


class BannerAccessResponseSchema(BaseSchema):
    success: bool
