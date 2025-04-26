from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SystemLogAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system_log"
    verbose_name = _("apps.system_log.description")
