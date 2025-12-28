from datetime import datetime

from django.conf import settings
from pydantic import EmailStr, field_serializer

from apps.api.language.schemas import LanguageSchema
from apps.api.user.schemas import UserSchema
from pyaa.fastapi.schemas import BaseSchema


class CustomerCreateSchema(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    mobile_phone: str | None = None
    password: str
    language: int | None = None
    gender: str | None = None
    obs: str | None = None
    timezone: str = settings.DEFAULT_TIME_ZONE


class CustomerUpdateSchema(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    mobile_phone: str | None = None
    password: str | None = None
    language: int | None = None
    gender: str | None = None
    obs: str | None = None
    timezone: str | None = None


class TokenSchema(BaseSchema):
    refresh: str
    access: str


class CustomerResponseSchema(BaseSchema):
    user: UserSchema
    nickname: str | None = None
    gender: str | None = None
    avatar: str | None = None
    credits: int | None = None
    obs: str | None = None
    language: LanguageSchema | None
    timezone: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_serializer("timezone")
    def serialize_timezone(self, timezone, _info):
        return str(timezone) if timezone else None


class CustomerCreateResponseSchema(CustomerResponseSchema):
    token: TokenSchema
