import gzip
import os
import shutil
import subprocess
import tempfile

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Restore the database from a storage service or a local file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Specify the database name from settings.DATABASES (default: 'default')",
        )

        parser.add_argument(
            "--storage-path",
            help="Path to the file in the storage service (e.g., S3) to restore",
        )

        parser.add_argument(
            "--local-path",
            help="Path to a local backup file to restore",
        )

    def handle(self, *args, **options):
        db_name_option = options["database"]
        db_settings = settings.DATABASES.get(db_name_option)
        storage_path = options["storage_path"]
        local_path = options["local_path"]

        if not db_settings:
            self.stderr.write(
                self.style.ERROR(
                    f"Database '{db_name_option}' not found in settings.DATABASES"
                )
            )
            return

        if not storage_path and not local_path:
            self.stderr.write(
                self.style.ERROR("Specify either --storage-path or --local-path.")
            )
            return

        backup_filepath = (
            self.download_from_storage(storage_path) if storage_path else local_path
        )

        if backup_filepath.endswith(".gz"):
            backup_filepath = self.decompress_file(backup_filepath)

        db_engine = db_settings.get("ENGINE")

        if "sqlite" in db_engine:
            self.restore_sqlite(db_settings, backup_filepath)
        elif "mysql" in db_engine:
            self.restore_mysql(db_settings, backup_filepath)
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"Restore for database type '{db_engine}' is not implemented"
                )
            )

    def decompress_file(self, compressed_path):
        decompressed_path = compressed_path.rstrip(".gz")

        with gzip.open(compressed_path, "rb") as f_in:
            with open(decompressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(compressed_path)

        self.stdout.write(self.style.SUCCESS(f"Decompressed file: {decompressed_path}"))

        return decompressed_path

    def restore_sqlite(self, db_settings, backup_filepath):
        db_name = db_settings.get("NAME", "")

        try:
            shutil.copyfile(backup_filepath, db_name)

            self.stdout.write(
                self.style.SUCCESS(f"SQLite database restored from {backup_filepath}")
            )
        except IOError as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to restore SQLite database: {e}")
            )

    def restore_mysql(self, db_settings, backup_filepath):
        db_name = db_settings.get("NAME", "")
        db_host = db_settings.get("HOST", "localhost")
        db_user = db_settings.get("USER", "root")
        db_password = db_settings.get("PASSWORD", "")

        restore_command = [
            "mysql",
            "-h",
            db_host,
            "-u",
            db_user,
            f"-p{db_password}",
            db_name,
        ]

        try:
            with open(backup_filepath, "rb") as f_in:
                subprocess.check_call(restore_command, stdin=f_in)

            self.stdout.write(
                self.style.SUCCESS(f"MySQL database restored from {backup_filepath}")
            )
        except subprocess.CalledProcessError as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to restore MySQL database: {e}")
            )

    def download_from_storage(self, storage_key):
        aws_access_key_id = getattr(
            settings,
            "BACKUP_AWS_ACCESS_KEY_ID",
            os.getenv("AWS_ACCESS_KEY_ID"),
        )

        aws_secret_access_key = getattr(
            settings,
            "BACKUP_AWS_SECRET_ACCESS_KEY",
            os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        region_name = getattr(
            settings,
            "BACKUP_AWS_REGION",
            os.getenv("AWS_REGION"),
        )

        bucket_name = getattr(
            settings,
            "BACKUP_AWS_S3_BUCKET_NAME",
            os.getenv("AWS_S3_BUCKET_NAME"),
        )

        if not bucket_name:
            raise ValueError("S3 bucket not specified in settings or environment")

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

        download_path = os.path.join(
            tempfile.gettempdir(), os.path.basename(storage_key)
        )

        try:
            s3_client.download_file(bucket_name, storage_key, download_path)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Downloaded backup file from storage to {download_path}"
                )
            )

            return download_path
        except (NoCredentialsError, ClientError) as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to download backup file from storage: {e}")
            )

            raise
