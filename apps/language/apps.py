from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LanguageAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.language"
    verbose_name = _("apps.language.description")
