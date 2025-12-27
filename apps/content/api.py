from ninja import Router
from ninja.errors import HttpError

from apps.content.helpers import ContentHelper
from apps.content.schemas import ContentSchema

router = Router()


@router.get("/{tag}/", response=ContentSchema, auth=None, by_alias=True)
def get_content_by_tag(request, tag: str):
    content = ContentHelper.get_content(content_tag=tag)
    if not content:
        raise HttpError(404, "Not found")
    return content
