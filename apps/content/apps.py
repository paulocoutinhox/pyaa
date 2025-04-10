from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.content"
    verbose_name = _("apps.content.description")
