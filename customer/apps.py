from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customer"
    verbose_name = _("customer.app.description")
