from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BannerAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.banner"
    verbose_name = _("apps.banner.description")
