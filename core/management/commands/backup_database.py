import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает резервную копию базы данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default=str(settings.BASE_DIR / "backups"),
            help="Директория для сохранения резервных копий",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        db_config = settings.DATABASES["default"]
        engine = db_config["ENGINE"]

        if "sqlite3" in engine:
            self.backup_sqlite(db_config, output_dir, timestamp)
        elif "postgresql" in engine:
            self.backup_postgresql(db_config, output_dir, timestamp)
        elif "mysql" in engine:
            self.backup_mysql(db_config, output_dir, timestamp)
        else:
            self.stdout.write(
                self.style.ERROR(f"Неподдерживаемая база данных: {engine}")
            )

    def backup_sqlite(self, db_config, output_dir, timestamp):
        db_path = db_config["NAME"]
        backup_path = f"{output_dir}/backup_sqlite_{timestamp}.db"

        try:
            import shutil

            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f"✅ SQLite резервная копия создана: {backup_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка создания резервной копии: {e}")
            )

    def backup_postgresql(self, db_config, output_dir, timestamp):
        backup_path = f"{output_dir}/backup_postgresql_{timestamp}.sql"

        cmd = [
            "pg_dump",
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}",
            f"--file={backup_path}",
            "--no-password",
            "--verbose",
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = db_config["PASSWORD"]

        try:
            subprocess.run(cmd, env=env, check=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ PostgreSQL резервная копия создана: {backup_path}"
                )
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка создания резервной копии: {e}")
            )

    def backup_mysql(self, db_config, output_dir, timestamp):
        backup_path = f"{output_dir}/backup_mysql_{timestamp}.sql"

        cmd = [
            "mysqldump",
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            db_config["NAME"],
        ]

        try:
            with open(backup_path, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            self.stdout.write(
                self.style.SUCCESS(f"✅ MySQL резервная копия создана: {backup_path}")
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка создания резервной копии: {e}")
            )
