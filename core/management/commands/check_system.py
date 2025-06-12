from django.db import connection
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Проверяет состояние системы и конфигурации"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Проверка системы ==="))

        # Проверка базы данных
        self.check_database()

        # Проверка кэша
        self.check_cache()

        # Проверка статических файлов
        self.check_static_files()

        # Проверка медиа файлов
        self.check_media_files()

        # Проверка логов
        self.check_logs()

        # Проверка безопасности
        self.check_security()

        # Проверка email
        self.check_email()

        self.stdout.write(self.style.SUCCESS("=== Проверка завершена ==="))

    def check_database(self):
        self.stdout.write("\n📊 Проверка базы данных...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS("✅ База данных доступна"))

                    # Проверка количества записей
                    from core.models import CompanyInfo, Product, Category

                    company_count = CompanyInfo.objects.count()
                    product_count = Product.objects.count()
                    category_count = Category.objects.count()

                    self.stdout.write(f"   Компаний: {company_count}")
                    self.stdout.write(f"   Товаров: {product_count}")
                    self.stdout.write(f"   Категорий: {category_count}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка подключения к БД: {e}"))

    def check_cache(self):
        self.stdout.write("\n🗂️  Проверка кэша...")
        try:
            test_key = "system_check_test"
            test_value = "test_value"

            cache.set(test_key, test_value, 60)
            cached_value = cache.get(test_key)

            if cached_value == test_value:
                self.stdout.write(self.style.SUCCESS("✅ Кэш работает"))
                cache.delete(test_key)
            else:
                self.stdout.write(self.style.ERROR("❌ Кэш не работает"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка кэша: {e}"))

    def check_static_files(self):
        self.stdout.write("\n📁 Проверка статических файлов...")

        static_root = getattr(settings, "STATIC_ROOT", None)

        if static_root and static_root.exists():
            file_count = len(list(static_root.rglob("*")))
            self.stdout.write(
                self.style.SUCCESS(f"✅ Статические файлы: {file_count} файлов")
            )
            self.stdout.write(f"   Путь: {static_root}")
        else:
            self.stdout.write(self.style.WARNING("⚠️  Статические файлы не собраны"))

    def check_media_files(self):
        self.stdout.write("\n🖼️  Проверка медиа файлов...")

        media_root = getattr(settings, "MEDIA_ROOT", None)

        if media_root and media_root.exists():
            file_count = len(list(media_root.rglob("*")))
            self.stdout.write(
                self.style.SUCCESS(f"✅ Медиа файлы: {file_count} файлов")
            )
            self.stdout.write(f"   Путь: {media_root}")
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  Директория медиа файлов не найдена")
            )

    def check_logs(self):
        self.stdout.write("\n📝 Проверка логов...")

        log_dir = getattr(settings, "LOG_DIR", settings.BASE_DIR / "logs")

        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            if log_files:
                total_size = sum(f.stat().st_size for f in log_files)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Лог файлы: {len(log_files)} файлов")
                )
                self.stdout.write(f"   Общий размер: {self.format_bytes(total_size)}")
            else:
                self.stdout.write(self.style.WARNING("⚠️  Лог файлы не найдены"))
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Директория логов не найдена: {log_dir}")
            )

    def check_security(self):
        self.stdout.write("\n🔒 Проверка безопасности...")

        # Проверка DEBUG
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING("⚠️  DEBUG=True (только для разработки!)")
            )
        else:
            self.stdout.write(self.style.SUCCESS("✅ DEBUG=False"))

        # Проверка SECRET_KEY
        if hasattr(settings, "SECRET_KEY") and settings.SECRET_KEY:
            if len(settings.SECRET_KEY) >= 50:
                self.stdout.write(self.style.SUCCESS("✅ SECRET_KEY установлен"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  SECRET_KEY слишком короткий"))
        else:
            self.stdout.write(self.style.ERROR("❌ SECRET_KEY не установлен"))

        # Проверка HTTPS настроек для продакшена
        if not settings.DEBUG:
            https_settings = [
                "SECURE_SSL_REDIRECT",
                "SESSION_COOKIE_SECURE",
                "CSRF_COOKIE_SECURE",
                "SECURE_HSTS_SECONDS",
            ]

            for setting_name in https_settings:
                if hasattr(settings, setting_name) and getattr(settings, setting_name):
                    self.stdout.write(self.style.SUCCESS(f"✅ {setting_name} включен"))
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {setting_name} не настроен")
                    )

    def check_email(self):
        self.stdout.write("\n📧 Проверка email настроек...")

        email_settings = ["EMAIL_HOST", "EMAIL_HOST_USER", "DEFAULT_FROM_EMAIL"]

        for setting_name in email_settings:
            if hasattr(settings, setting_name) and getattr(settings, setting_name):
                self.stdout.write(self.style.SUCCESS(f"✅ {setting_name} настроен"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  {setting_name} не настроен"))

    def format_bytes(self, bytes_size):
        """Форматирует размер в байтах в читаемый вид"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

