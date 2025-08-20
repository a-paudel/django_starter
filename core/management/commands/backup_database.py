from datetime import UTC, datetime
from pathlib import Path
import subprocess
from typing import Any
from django.core.management import BaseCommand
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
import shutil
import os
import tempfile
from minio import Minio
import gzip

BACKUP_CLIENT = Minio(
    endpoint=os.getenv("BACKUP_S3_ENDPOINT", ""),
    access_key=os.getenv("BACKUP_S3_ACCESS_KEY"),
    secret_key=os.getenv("BACKUP_S3_SECRET_KEY"),
    secure=os.getenv("BACKUP_S3_SECURE", "").lower() == "true",
)
BACKUP_BUCKET = os.getenv("BACKUP_S3_BUCKET", "")


class Command(BaseCommand):
    def _dump_postgres(self, conn: BaseDatabaseWrapper):
        pgdump_path = shutil.which("pg_dump")
        if not pgdump_path:
            raise Exception("Failed to backup database. pg_dump not found in path")
        temp_dir = tempfile.mkdtemp()

        dump_file = Path(temp_dir) / "db.sql.gz"

        db_data = conn.settings_dict
        database_url = f"postgresql://{db_data['USER']}:{db_data['PASSWORD']}@{db_data['HOST']}:{db_data['PORT']}/{db_data['NAME']}"

        with gzip.open(dump_file, "wb") as f_out:
            pgdump_process = subprocess.Popen([pgdump_path, "--dbname", database_url], stdout=subprocess.PIPE)

            if not pgdump_process.stdout:
                return None

            shutil.copyfileobj(pgdump_process.stdout, f_out)

            pgdump_process.wait()

        return dump_file

    def _dump_sqlite(self, conn: BaseDatabaseWrapper):
        # get the sqlite file path
        db_path = Path(conn.settings_dict["NAME"])
        if db_path.exists():
            with tempfile.TemporaryDirectory(delete=False) as tmp_dir:
                target_path = Path(tmp_dir) / db_path.name
                shutil.copy(db_path, target_path)
                return target_path
        return None

    def _upload_dump_to_s3(self, dump_file: Path):
        if BACKUP_BUCKET not in [b.name for b in BACKUP_CLIENT.list_buckets()]:
            BACKUP_CLIENT.make_bucket(BACKUP_BUCKET)
        timestamp = (
            datetime.now(UTC)
            .isoformat()
            .replace(" ", "_")
            .replace(":", "_")
            .replace("-", "_")
            .replace("T", "_")
            .replace(".", "_")
            .replace("+", "_")
            .replace("Z", "")
        )
        object_name = f"backups/{timestamp}/database/{dump_file.name}"
        BACKUP_CLIENT.fput_object(
            BACKUP_BUCKET,
            object_name,
            str(dump_file.resolve()),
        )

    def _delete_dump(self, dump_file: Path):
        shutil.rmtree(dump_file.parent)

    SUPPORTED_DATABASES = {"sqlite": _dump_sqlite, "postgresql": _dump_postgres}

    def handle(self, *args: Any, **options: Any) -> str | None:
        for connection_name in connections:
            conn = connections[connection_name]

            if conn.vendor not in self.SUPPORTED_DATABASES.keys():
                raise NotImplementedError(
                    f"The current database {conn.vendor} is not supported.",
                    f"Supported databases are: {self.SUPPORTED_DATABASES.keys()}",
                )

            fun = self.SUPPORTED_DATABASES[conn.vendor]
            dump_file = fun(self, conn)

            if not dump_file:
                print("Failed to create database backup")
                return

            self._upload_dump_to_s3(dump_file)
            self._delete_dump(dump_file)
