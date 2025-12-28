from pyaa.fastapi.schemas import BaseSchema


class SystemLogCreateSchema(BaseSchema):
    level: str
    description: str
    category: str | None = None


class SystemLogResponseSchema(BaseSchema):
    success: bool
