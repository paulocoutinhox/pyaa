from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.site"
    verbose_name = _("apps.site.description")
