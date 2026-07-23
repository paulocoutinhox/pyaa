from asgiref.sync import sync_to_async
from django.db import transaction
from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.auth.dependencies import require_permission
from apps.api.content.schemas import ContentCreateSchema, ContentSchema
from apps.content.helpers import ContentHelper
from apps.content.models import Content

router = APIRouter()


@router.get("/{tag}", response_model=ContentSchema)
async def get_content_by_tag(tag: str):
    content = await sync_to_async(ContentHelper.get_content)(content_tag=tag)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ContentSchema.model_validate(content)


@sync_to_async
@transaction.atomic
def _create_content(data: ContentCreateSchema) -> ContentSchema:
    content = Content.objects.create(
        title=data.title,
        content=data.content,
        tag=data.tag,
        category_id=data.category_id,
        language_id=data.language_id,
        published_at=data.published_at,
        active=data.active,
    )

    content = Content.objects.select_related("category", "language").get(pk=content.pk)

    return ContentSchema.model_validate(content)


@router.post(
    "",
    response_model=ContentSchema,
    dependencies=[Depends(require_permission("content.add_content"))],
)
async def create_content(data: ContentCreateSchema):
    return await _create_content(data)
