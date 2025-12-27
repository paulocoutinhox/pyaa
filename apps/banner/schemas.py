from ninja import ModelSchema

from apps.banner.models import Banner
from pyaa.api.base import BaseSchema


class BannerSchema(ModelSchema, BaseSchema):
    class Meta:
        model = Banner
        fields = [
            "title",
            "image",
            "link",
            "target_blank",
            "zone",
            "token",
            "sort_order",
            "start_at",
            "end_at",
        ]


class BannerAccessResponseSchema(BaseSchema):
    success: bool
