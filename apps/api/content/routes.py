from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, status

from apps.api.content.schemas import ContentSchema
from apps.content.helpers import ContentHelper

router = APIRouter()


@router.get("/{tag}/", response_model=ContentSchema)
async def get_content_by_tag(tag: str):
    content = await sync_to_async(ContentHelper.get_content)(content_tag=tag)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return content
