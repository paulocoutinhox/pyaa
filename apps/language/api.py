from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination

from apps.language.models import Language
from apps.language.schemas import LanguageCreateSchema, LanguageSchema

router = Router()


@router.get("/", response=list[LanguageSchema], auth=None)
@paginate(LimitOffsetPagination)
def list_languages(request):
    return Language.objects.order_by("-id")


@router.post("/", response=LanguageSchema, auth=None)
def create_language(request, data: LanguageCreateSchema):
    return Language.objects.create(**data.dict())
