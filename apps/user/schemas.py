from ninja import ModelSchema

from apps.user.models import User
from pyaa.api.base import BaseSchema


class UserSchema(ModelSchema, BaseSchema):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "cpf", "mobile_phone"]
