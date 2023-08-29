from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account"
    verbose_name = _("account.app.description")
