from fastapi import APIRouter

from apps.api.auth.routes import router as auth_router
from apps.api.banner.routes import router as banner_router
from apps.api.content.routes import router as content_router
from apps.api.customer.routes import router as customer_router
from apps.api.gallery.routes import router as gallery_router
from apps.api.language.routes import router as language_router
from apps.api.shop.routes import router as shop_router
from apps.api.system_log.routes import router as system_log_router

router = APIRouter()

router.include_router(auth_router, prefix="/token", tags=["Authentication"])
router.include_router(customer_router, prefix="/customer", tags=["Customer"])
router.include_router(language_router, prefix="/language", tags=["Language"])
router.include_router(content_router, prefix="/content", tags=["Content"])
router.include_router(gallery_router, prefix="/gallery", tags=["Gallery"])
router.include_router(banner_router, prefix="/banner", tags=["Banner"])
router.include_router(shop_router, prefix="/shop", tags=["Shop"])
router.include_router(system_log_router, prefix="/system-log", tags=["System Log"])
