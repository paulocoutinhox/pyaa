from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from apps.banner.api import router as banner_router
from apps.content.api import router as content_router
from apps.customer.api import router as customer_router
from apps.gallery.api import router as gallery_router
from apps.language.api import router as language_router
from apps.system_log.api import router as system_log_router

api = NinjaExtraAPI(
    title="PYAA API",
    version="1.0.0",
)

api.register_controllers(NinjaJWTDefaultController)

api.add_router("/customer", customer_router, tags=["Customer"])
api.add_router("/language", language_router, tags=["Language"])
api.add_router("/content", content_router, tags=["Content"])
api.add_router("/gallery", gallery_router, tags=["Gallery"])
api.add_router("/banner", banner_router, tags=["Banner"])
api.add_router("/system-log", system_log_router, tags=["System Log"])
