from ninja import ModelSchema

from apps.language.models import Language
from pyaa.api.base import BaseSchema


class LanguageSchema(ModelSchema, BaseSchema):
    class Meta:
        model = Language
        fields = ["id", "name", "native_name", "code_iso_639_1", "code_iso_language"]


class LanguageCreateSchema(ModelSchema, BaseSchema):
    class Meta:
        model = Language
        fields = ["name", "native_name", "code_iso_639_1", "code_iso_language"]
