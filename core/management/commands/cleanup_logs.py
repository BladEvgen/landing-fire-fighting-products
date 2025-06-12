from django.conf import settings
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Очищает старые лог файлы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Количество дней для хранения логов (по умолчанию: 7)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать какие файлы будут удалены без фактического удаления",
        )

    def handle(self, *args, **options):
        days_to_keep = options["days"]
        dry_run = options["dry_run"]

        log_dir = getattr(settings, "LOG_DIR", settings.BASE_DIR / "logs")

        if not log_dir.exists():
            self.stdout.write(
                self.style.WARNING(f"Директория логов не найдена: {log_dir}")
            )
            return

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        total_size = 0

        self.stdout.write(f"Поиск лог файлов старше {days_to_keep} дней...")

        for log_file in log_dir.glob("*.log*"):
            try:
                file_modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                file_size = log_file.stat().st_size

                if file_modified_time < cutoff_date:
                    if dry_run:
                        self.stdout.write(
                            f"Будет удален: {log_file.name} "
                            f"(размер: {self.format_bytes(file_size)}, "
                            f"изменен: {file_modified_time.strftime('%Y-%m-%d %H:%M')})"
                        )
                    else:
                        log_file.unlink()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Удален: {log_file.name} "
                                f"(размер: {self.format_bytes(file_size)})"
                            )
                        )

                    deleted_count += 1
                    total_size += file_size

            except (OSError, ValueError) as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка обработки файла {log_file}: {e}")
                )

        if deleted_count > 0:
            action = "будет удалено" if dry_run else "удалено"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Итого {action}: {deleted_count} файлов "
                    f"({self.format_bytes(total_size)})"
                )
            )
        else:
            self.stdout.write("Старых лог файлов не найдено")

    def format_bytes(self, bytes_size):
        """Форматирует размер в байтах в читаемый вид"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
