from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class LogLevel(TextChoices):
    DEBUG = "debug", _("enum.log-level.debug")
    INFO = "info", _("enum.log-level.info")
    SUCCESS = "success", _("enum.log-level.success")
    WARNING = "warning", _("enum.log-level.warning")
    ERROR = "error", _("enum.log-level.error")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)
