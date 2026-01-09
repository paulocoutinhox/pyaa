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

Alternatively, you can add `mysqlclient` to your `requirements.txt` file and install all dependencies at once:

```bash
pip install -r requirements.txt
```

> **Note**: If you're using MySQL with Docker, you may also need to install the MySQL client dependency:
>
> ```bash
> apt install default-mysql-client
> ```

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

If you encounter issues while installing the MySQL Client, please refer to the [troubleshooting](troubleshooting.md) documentation.

## Backup Command Usage

The `backup_db` command allows you to back up your database and upload it to an S3 bucket (or other storage service if configured). The command supports options for compressing the backup and controlling access permissions.

### Basic Usage

1. **Without specifying a database**: By default, the command will back up the database configured as `default` in your `settings.DATABASES`.

   ```bash
   python manage.py backup_db
   ```

2. **Specifying a database**: You can choose a specific database by passing its name as a parameter. For example, to back up a database configured under the name `secondary`, use:

   ```bash
   python manage.py backup_db --database secondary
   ```

In both cases, the command will create a backup file in the system's temporary directory, upload it to the specified S3 bucket or storage service, and then delete the local file. Make sure your storage service is properly configured and accessible with the appropriate credentials.

### Additional Options

- **Compression**: To compress the backup file before uploading, use the `--compress` flag. This will save the backup file as a `.gz` archive, reducing storage space and transfer time.

  ```bash
  python manage.py backup_db --compress
  ```

- **Private Access**: To upload the backup with private access (no public read permissions), use the `--private` flag. This sets the file to private access on S3 or the storage service in use.

  ```bash
  python manage.py backup_db --private
  ```

  You can also combine both options if you want a compressed backup with private access:

  ```bash
  python manage.py backup_db --compress --private
  ```

### Storage Configuration

The command will look for AWS S3 credentials prefixed with `BACKUP_*` in your Django settings file. If these are not set, it will fall back to the corresponding environment variables. Below is the list of all possible variables:

- `BACKUP_AWS_ACCESS_KEY_ID` or `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
- `BACKUP_AWS_SECRET_ACCESS_KEY` or `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
- `BACKUP_AWS_REGION` or `AWS_REGION`: The AWS region where your S3 bucket is hosted.
- `BACKUP_AWS_S3_BUCKET_NAME` or `AWS_S3_BUCKET_NAME`: The name of your S3 bucket where backups will be uploaded.

> **Note**: To use this command with MySQL, you need the Python library `mysqlclient` and the `mysqldump` utility from the MySQL client. Install `mysqlclient` with:

> ```bash
> python3 -m pip install mysqlclient
> ```

> and `mysqldump` by installing the MySQL client itself. On macOS, you can install it with Homebrew:

> ```
> brew install mysql-client
> ```

> For Linux, use the package manager (e.g., `sudo apt install default-mysql-client` on Ubuntu). On Windows, download the MySQL client from the [MySQL website](https://dev.mysql.com/downloads/mysql/) and add it to your system path.

## Restore Command Usage

The `restore_db` command allows you to restore your database from a backup file, either from a storage service (e.g., S3) or from a local file. The command also supports `.gz` compressed files, which will be automatically decompressed during the restoration.

### Basic Usage

1. **Restoring from storage service (e.g., S3)**: To restore a database from a file located in your storage service, use the `--storage-path` option to specify the file path.

   ```bash
   python manage.py restore_db --storage-path backups/db/default/backupfile.sql.gz
   ```

2. **Restoring from a local file**: You can also restore directly from a local file by specifying the `--local-path` option.

   ```bash
   python manage.py restore_db --local-path /path/to/backupfile.sql.gz
   ```

3. **Specifying the database**: As with the backup command, you can specify the target database with the `--database` option. If not specified, it will default to `default`.

   ```bash
   python manage.py restore_db --database secondary --local-path /path/to/backupfile.sql.gz
   ```

In all cases, if the backup file is compressed (`.gz`), it will be decompressed automatically before restoration. Ensure your storage credentials and paths are correctly configured in your Django settings.

## Running Migrations in Production from Local

You can run migrations in production from your development machine by specifying the Django settings module for production. This is useful when you need to apply database changes without directly accessing the production server.

### Basic Usage

To run migrations in production, use the `DJANGO_SETTINGS_MODULE` environment variable to point to your production settings file:

```bash
DJANGO_SETTINGS_MODULE=pyaa.settings.prod make migrate
```

Or if you prefer using `python manage.py` directly:

```bash
DJANGO_SETTINGS_MODULE=pyaa.settings.prod python manage.py migrate
```
