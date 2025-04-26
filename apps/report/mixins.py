import calendar
import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.formats import get_format


class DateParserMixin:
    """Mixin to handle date parsing from various formats."""

    def parse_date(self, date_str):
        """
        Parse a date string from any format to a datetime object.
        First tries to parse using Django's date formats, then falls back to parse_datetime.
        """
        if not date_str:
            return None

        # try to parse using django's date formats
        for format in get_format("DATE_INPUT_FORMATS"):
            try:
                date = datetime.datetime.strptime(date_str, format)
                return timezone.make_aware(date)
            except (ValueError, TypeError):
                continue

        # if no format worked, try parse datetime
        try:
            return parse_datetime(date_str)
        except (ValueError, TypeError):
            return None

    def get_month_range(self, date=None):
        """
        Get the start and end of the month for a given date.
        If no date is provided, uses current date.
        """
        if date is None:
            date = timezone.now()

        start_of_month = date.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        last_day = calendar.monthrange(date.year, date.month)[1]

        end_of_month = date.replace(
            day=last_day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )

        return start_of_month, end_of_month
