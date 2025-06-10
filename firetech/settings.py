import os
import socket
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

HOST_NAMES = ["RogStrix", "MacBook-Pro.local", "MacbookPro"]

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


DEBUG = socket.gethostname() in HOST_NAMES
ENVIRONMENT = "development" if DEBUG else "production"

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

DB_TYPE = os.getenv("DB_TYPE", "sqlite3").lower()


EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", f"<{EMAIL_HOST_USER}>")

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Error getting local IP: {e}")
        ip_address = "127.0.0.1"
    return ip_address

def get_external_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            external_ip = s.getsockname()[0]
    except Exception as e:
        print(f"Error getting external IP: {e}")
        external_ip = "127.0.0.1"
    return external_ip

LOCAL_IP = get_local_ip()
EXTERNAL_IP = get_external_ip()


if DEBUG:
    ALLOWED_HOSTS = ["*", LOCAL_IP, EXTERNAL_IP, "localhost", "127.0.0.1"]
else:
    ALLOWED_HOSTS = [
        "vympel45.ru",
        "www.vympel45.ru", 
        os.getenv("DOMAIN_NAME", "example.com"),
        LOCAL_IP,
        EXTERNAL_IP
    ]

# Настройки безопасности для продакшена
if not DEBUG:
    # HTTPS и безопасность
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_AGE = 3600  # 1 час
    
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    
else:
    SESSION_COOKIE_AGE = 86400  # 24 часа
    CSRF_COOKIE_AGE = 86400

# Приложения
DJANGO_APPS = [
    "daphne",
    "channels",
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS = [
    # Здесь можно добавить сторонние приложения
    "debug_toolbar", 
    "django_extensions", 
]

LOCAL_APPS = [
    "core",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",

]


ROOT_URLCONF = "firetech.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.current_year",
                "core.context_processors.company_info",
            ],
            "debug": DEBUG,
        },
    },
]

ASGI_APPLICATION = "firetech.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": (
            "channels.layers.InMemoryChannelLayer"
            if DEBUG
            else "channels_redis.core.RedisChannelLayer"
        ),
        "CONFIG": {} if DEBUG else {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Кэширование
if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
            "TIMEOUT": 300,
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
            }
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 20,
                    "retry_on_timeout": True,
                },
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            },
            "KEY_PREFIX": "vympel45",
            "TIMEOUT": 300,
        }
    }

DATABASES = {"default": {}}

if DEBUG:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        }
    }
else:
    if DB_TYPE == "mysql":
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    elif DB_TYPE == "postgresql":
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "OPTIONS": {
                "sslmode": "prefer",
            }
        }
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

if not DEBUG:
    DATABASES["default"]["CONN_MAX_AGE"] = 60

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticroot"
STATICFILES_DIRS = [BASE_DIR / "static"]

if not DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

def clean_old_logs(log_directory, days_to_keep=7):
    try:
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_to_keep)
        
        for log_file in log_directory.glob("*.log*"):
            try:
                file_modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_modified_time < cutoff_date:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
            except (OSError, ValueError) as e:
                print(f"Error processing log file {log_file}: {e}")
    except Exception as e:
        print(f"Error cleaning logs: {e}")

clean_old_logs(LOG_DIR, days_to_keep=7)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {process:d} {thread:d} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["require_debug_true"] if DEBUG else [],
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "security.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "verbose",
            "filters": ["require_debug_false"],
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "mail_admins"] if not DEBUG else ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_NAME = "vympel45_sessionid"
SESSION_SAVE_EVERY_REQUEST = False

# Настройки сообщений
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx']

GRAPPELLI_ADMIN_TITLE = "Админ-панель Вымпел-45"

# Настройки для отладки (только для разработки)
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1", LOCAL_IP, EXTERNAL_IP]
    
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

USE_GZIP = True
if USE_GZIP and not DEBUG:
    MIDDLEWARE.insert(1, "django.middleware.gzip.GZipMiddleware")

# Настройки для работы с прокси (nginx, cloudflare и т.д.)
if not DEBUG:
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# CORS_ALLOW_ALL_ORIGINS = DEBUG
# CORS_ALLOWED_ORIGINS = ["https://vympel45.ru"] if not DEBUG else []

# Дополнительные middleware для продакшена
if not DEBUG:
    # Можно добавить middleware для rate limiting, security headers и т.д.
    pass

print(f"🚀 Django running in {ENVIRONMENT} mode")
print(f"📊 Debug: {DEBUG}")
print(f"🗄️  Database: {DB_TYPE}")
print(f"🌐 Allowed hosts: {ALLOWED_HOSTS}")
if DEBUG:
    print(f"🔗 Local IP: {LOCAL_IP}")
    print(f"🔗 External IP: {EXTERNAL_IP}")