from pyaa.fastapi.schemas import BaseSchema


class LanguageSchema(BaseSchema):
    name: str
    native_name: str
    code_iso_639_1: str
    code_iso_language: str


class LanguageCreateSchema(BaseSchema):
    name: str
    native_name: str
    code_iso_639_1: str
    code_iso_language: str


class PaginatedLanguageListResponse(BaseSchema):
    count: int
    items: list[LanguageSchema]
