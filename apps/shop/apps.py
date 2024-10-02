from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShopAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shop"
    verbose_name = _("apps.shop.description")
