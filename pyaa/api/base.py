from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(Schema):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )
