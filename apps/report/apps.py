from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReportAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.report"
    verbose_name = _("apps.report.description")

    def ready(self):
        import apps.report.admin.customer_gender  # noqa F401
        import apps.report.admin.banner_access  # noqa F401
