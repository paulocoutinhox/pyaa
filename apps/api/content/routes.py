from fastapi import APIRouter, HTTPException, status

from apps.api.content.schemas import ContentSchema
from apps.content.helpers import ContentHelper

router = APIRouter()


@router.get("/{tag}/", response_model=ContentSchema)
def get_content_by_tag(tag: str):
    content = ContentHelper.get_content(content_tag=tag)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return content
