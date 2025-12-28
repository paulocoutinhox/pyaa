from datetime import datetime
from uuid import UUID

from pyaa.fastapi.schemas import BaseSchema


class BannerSchema(BaseSchema):
    title: str
    image: str
    link: str | None
    target_blank: bool
    zone: str
    token: UUID
    sort_order: int
    start_at: datetime | None
    end_at: datetime | None


class BannerAccessResponseSchema(BaseSchema):
    success: bool
