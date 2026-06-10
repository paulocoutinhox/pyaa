from datetime import datetime
from unittest.mock import MagicMock, patch

from django.test import TestCase

from pyaa.helpers.database import DatabaseHelper


def _mock_connection(vendor, value):
    connection = MagicMock()
    connection.vendor = vendor
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (value,)
    return connection


class DatabaseHelperTest(TestCase):
    def test_get_now_returns_datetime(self):
        result = DatabaseHelper.get_now()
        self.assertIsInstance(result, datetime)

    def test_get_now_is_close_to_utcnow(self):
        before = datetime.utcnow()
        result = DatabaseHelper.get_now()
        after = datetime.utcnow()

        # the database timestamp should fall within the call window
        self.assertGreaterEqual(
            result.replace(microsecond=0), before.replace(microsecond=0)
        )
        self.assertLessEqual((result - after).total_seconds(), 5)

    def test_get_now_parses_sqlite_iso_string(self):
        connection = _mock_connection("sqlite", "2025-06-08T10:30:00")

        with patch("pyaa.helpers.database.connection", connection):
            result = DatabaseHelper.get_now()

        self.assertEqual(result, datetime(2025, 6, 8, 10, 30, 0))

    def test_get_now_returns_postgresql_datetime(self):
        moment = datetime(2025, 6, 8, 12, 0, 0)
        connection = _mock_connection("postgresql", moment)

        with patch("pyaa.helpers.database.connection", connection):
            result = DatabaseHelper.get_now()

        self.assertEqual(result, moment)

    def test_get_now_returns_mysql_datetime(self):
        moment = datetime(2025, 6, 8, 12, 0, 0)
        connection = _mock_connection("mysql", moment)

        with patch("pyaa.helpers.database.connection", connection):
            result = DatabaseHelper.get_now()

        self.assertEqual(result, moment)

    def test_get_now_raises_for_unsupported_vendor(self):
        connection = _mock_connection("oracle", None)

        with patch("pyaa.helpers.database.connection", connection):
            with self.assertRaises(NotImplementedError):
                DatabaseHelper.get_now()
