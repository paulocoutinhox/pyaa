from pyaa.fastapi.schemas import BaseSchema


class TokenObtainPairRequest(BaseSchema):
    login: str
    password: str


class TokenObtainPairResponse(BaseSchema):
    refresh: str
    access: str


class TokenRefreshRequest(BaseSchema):
    refresh: str


class TokenRefreshResponse(BaseSchema):
    access: str
