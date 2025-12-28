from pyaa.fastapi.schemas import BaseSchema


class UserSchema(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    cpf: str | None = None
    mobile_phone: str | None = None
