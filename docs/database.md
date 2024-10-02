# Database

Django supports various databases, including SQLite, MySQL, PostgreSQL, and others. By default, Django uses SQLite for development purposes, but you can switch to other databases based on your needs.

## SQLite

Django uses SQLite by default. It requires no additional configuration and stores the database in a file. It's ideal for development and small projects.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "db.sqlite3",
    },
}
```

## MySQL

To use MySQL, you need to install the `mysqlclient` dependency. You can do this by running:

```bash
python3 -m pip install mysqlclient
```

Once installed, configure your database settings for MySQL like this:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db-name",
        "USER": "db-user",
        "PASSWORD": "db-pass",
        "HOST": "db-host",
        "PORT": "3306",
    },
}
```

Make sure that the MySQL server is running and accessible, and that you've replaced the placeholders (db-name, db-user, db-pass, etc.) with your actual database credentials.
