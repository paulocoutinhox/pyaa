from datetime import datetime

from django.db import connection


class DatabaseHelper:
    @staticmethod
    def get_now():
        """
        Fetches the current timestamp in UTC directly from the database.
        Works with SQLite, MySQL, and PostgreSQL.

        Returns:
            datetime: A datetime object representing the current timestamp in UTC.
        """
        with connection.cursor() as cursor:
            if connection.vendor == "sqlite":
                # sqlite always returns UTC
                cursor.execute("SELECT datetime('now')")
            elif connection.vendor == "postgresql":
                # postgre in UTC
                cursor.execute("SELECT NOW() AT TIME ZONE 'UTC'")
            elif connection.vendor == "mysql":
                # mysql in UTC
                cursor.execute("SELECT UTC_TIMESTAMP()")
            else:
                raise NotImplementedError(
                    f"Unsupported database vendor: {connection.vendor}"
                )

            db_now = cursor.fetchone()[0]

            # convert to a python datetime object if needed because SQLite returns ISO-8601 strings
            if isinstance(db_now, str):
                return datetime.fromisoformat(db_now)
            return db_now
