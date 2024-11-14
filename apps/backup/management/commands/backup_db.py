import gzip
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup the database and upload it to a storage service"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Specify the database name from settings.DATABASES (default: 'default')",
        )

        parser.add_argument(
            "--compress",
            action="store_true",
            help="Compress the backup file as a .gz archive before uploading",
        )

        parser.add_argument(
            "--private",
            action="store_true",
            help="Upload the backup file with private access (no public read permissions)",
        )

    def handle(self, *args, **options):
        # get database settings from the specified or default database
        db_name_option = options["database"]
        db_settings = settings.DATABASES.get(db_name_option)
        compress = options["compress"]
        private = options["private"]

        if not db_settings:
            self.stderr.write(
                self.style.ERROR(
                    f"Database '{db_name_option}' not found in settings.DATABASES"
                )
            )
            return

        db_engine = db_settings.get("ENGINE")

        # determine backup type based on database engine
        if "sqlite" in db_engine:
            self.backup_sqlite(db_settings, db_name_option, compress, private)
        elif "mysql" in db_engine:
            self.backup_mysql(db_settings, db_name_option, compress, private)
        else:
            # unsupported database type
            self.stderr.write(
                self.style.ERROR(
                    f"Backup for database type '{db_engine}' is not implemented"
                )
            )

    def backup_sqlite(self, db_settings, db_name_option, compress, private):
        # extract sqlite file path and setup backup path
        db_name = db_settings.get("NAME", "")
        backup_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{timestamp}.sqlite3"
        backup_filepath = os.path.join(backup_dir, backup_filename)

        try:
            # copy sqlite database file to backup location using shutil
            shutil.copyfile(db_name, backup_filepath)
            self.stdout.write(
                self.style.SUCCESS(f"SQLite backup created: {backup_filepath}")
            )

            # compress file if compress option is set
            if compress:
                compressed_filepath = f"{backup_filepath}.gz"
                with open(backup_filepath, "rb") as f_in:
                    with gzip.open(compressed_filepath, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_filepath)
                backup_filepath = compressed_filepath
                backup_filename += ".gz"
                self.stdout.write(
                    self.style.SUCCESS(f"Compressed backup file: {backup_filepath}")
                )

            # add db_name_option as part of storage path slug
            storage_key = f"backups/db/{db_name_option}/{backup_filename}"
            self.upload_to_storage(backup_filepath, storage_key, private)

            # delete local backup file after upload
            os.remove(backup_filepath)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backup uploaded to storage and local file deleted: {backup_filename}"
                )
            )

        except IOError as e:
            self.stderr.write(self.style.ERROR(f"Failed to create SQLite backup: {e}"))
        except (NoCredentialsError, ClientError) as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to upload SQLite backup to storage: {e}")
            )

    def backup_mysql(self, db_settings, db_name_option, compress, private):
        # extract mysql database settings and setup backup path
        db_name = db_settings.get("NAME", "")
        db_host = db_settings.get("HOST", "localhost")
        db_user = db_settings.get("USER", "root")
        db_password = db_settings.get("PASSWORD", "")
        backup_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{timestamp}.sql"
        backup_filepath = os.path.join(backup_dir, backup_filename)

        # prepare mysqldump command
        dump_command = [
            "mysqldump",
            "-h",
            db_host,
            "-u",
            db_user,
            f"-p{db_password}",
            db_name,
            "--result-file",
            backup_filepath,
        ]

        try:
            # execute mysqldump command
            subprocess.check_call(dump_command)
            self.stdout.write(
                self.style.SUCCESS(f"MySQL backup created: {backup_filepath}")
            )

            # compress file if --compress is set
            if compress:
                compressed_filepath = f"{backup_filepath}.gz"
                with open(backup_filepath, "rb") as f_in:
                    with gzip.open(compressed_filepath, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_filepath)
                backup_filepath = compressed_filepath
                backup_filename += ".gz"
                self.stdout.write(
                    self.style.SUCCESS(f"Compressed backup file: {backup_filepath}")
                )

            # add db_name_option as part of storage path slug
            storage_key = f"backups/db/{db_name_option}/{backup_filename}"
            self.upload_to_storage(backup_filepath, storage_key, private)

            # delete local backup file after upload
            os.remove(backup_filepath)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backup uploaded to storage and local file deleted: {backup_filename}"
                )
            )

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Failed to create MySQL backup: {e}"))
        except (NoCredentialsError, ClientError) as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to upload MySQL backup to storage: {e}")
            )

    def upload_to_storage(self, file_path, storage_key, private):
        # retrieve storage credentials and settings for S3
        aws_access_key_id = getattr(
            settings, "BACKUP_AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID")
        )

        aws_secret_access_key = getattr(
            settings, "BACKUP_AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        region_name = getattr(settings, "BACKUP_AWS_REGION", os.getenv("AWS_REGION"))
        bucket_name = getattr(settings, "BACKUP_S3_BUCKET", os.getenv("S3_BUCKET"))

        if not bucket_name:
            raise ValueError("S3 bucket not specified in settings or environment")

        # create boto3 S3 client with credentials
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

        # determine ACL permission based on 'private' boolean
        acl_permission = "private" if private else "public-read"

        # upload file to storage with specified ACL permission
        s3_client.upload_file(
            file_path, bucket_name, storage_key, ExtraArgs={"ACL": acl_permission}
        )
