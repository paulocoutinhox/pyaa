from django.conf import settings
from ninja import ModelSchema
from pydantic import EmailStr

from apps.customer.models import Customer
from apps.language.schemas import LanguageSchema
from apps.user.schemas import UserSchema
from pyaa.api.base import BaseSchema


class CustomerUserCreateSchema(BaseSchema):
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


class CustomerUserUpdateSchema(BaseSchema):
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


class CustomerResponseSchema(ModelSchema, BaseSchema):
    user: UserSchema
    language: LanguageSchema | None
    timezone: str

    class Meta:
        model = Customer
        fields = [
            "id",
            "user",
            "language",
            "nickname",
            "gender",
            "avatar",
            "credits",
            "obs",
            "created_at",
            "updated_at",
        ]

    @staticmethod
    def resolve_timezone(obj):
        return str(obj.timezone) if obj.timezone else None


class CustomerCreateResponseSchema(CustomerResponseSchema):
    token: TokenSchema
