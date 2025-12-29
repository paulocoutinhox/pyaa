from asgiref.sync import sync_to_async
from fastapi import APIRouter, Query

from apps.api.language.schemas import (
    LanguageCreateSchema,
    LanguageSchema,
    PaginatedLanguageListResponse,
)
from apps.language.models import Language

router = APIRouter()


@router.get("/", response_model=PaginatedLanguageListResponse)
async def list_languages(limit: int = Query(100, ge=1), offset: int = Query(0, ge=0)):
    queryset = Language.objects.order_by("-id")
    total_count = await queryset.acount()
    languages = await sync_to_async(list)(queryset[offset : offset + limit])

    items = [LanguageSchema.model_validate(lang) for lang in languages]
    return PaginatedLanguageListResponse(count=total_count, items=items)


@router.post("/", response_model=LanguageSchema)
async def create_language(data: LanguageCreateSchema):
    language = await Language.objects.acreate(
        name=data.name,
        native_name=data.native_name,
        code_iso_639_1=data.code_iso_639_1,
        code_iso_language=data.code_iso_language,
    )

    return LanguageSchema.model_validate(language)
