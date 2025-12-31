from datetime import datetime
from typing import Any

from pydantic import field_serializer

from pyaa.fastapi.schemas import BaseSchema


class PlanSchema(BaseSchema):
    name: str
    tag: str | None
    plan_type: str
    gateway: str
    external_id: str | None
    currency: str
    price: float
    credits: int | None
    frequency_type: str | None
    frequency_amount: int | None
    featured: bool
    bonus: int | None
    image: Any
    sort_order: int
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("image")
    def serialize_image(self, image) -> str | None:
        return image.url if image else None
