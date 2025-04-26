from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.system_log import enums
from apps.system_log.models import SystemLog


class SystemLogHelper:
    @staticmethod
    def create(
        level: enums.LogLevel,
        description: str,
        category: str | None = None,
        customer: Customer | None = None,
        site: Site | None = None,
    ) -> SystemLog:
        """
        Create a new system log entry

        :param level: The log level (debug, info, warning, error, success)
        :param description: The log description
        :param category: Optional category for the log
        :param customer: Optional customer associated with the log
        :param site: Optional site associated with the log. If not provided, uses current site
        :return: The created SystemLog instance
        """
        if not site:
            site = Site.objects.get_current()

        return SystemLog.objects.create(
            site=site,
            level=level,
            category=category,
            description=description,
            customer=customer,
        )
