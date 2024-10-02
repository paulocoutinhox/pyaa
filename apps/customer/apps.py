from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomerAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customer"
    verbose_name = _("apps.customer.description")
