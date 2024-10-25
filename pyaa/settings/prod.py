from .dev import *  # noqa F401

DEBUG = False

SECRET_KEY = "my-prod-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "error.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "ERROR",
    },
}

# Storage

# STORAGES["default"] = STORAGES["s3"]
# MEDIA_URL = f"https://{STORAGES["default"]["options"]["bucket_name"]}.s3.amazonaws.com/"

# Security
# More details here: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # one year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

# Email

# EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
# DEFAULT_FROM_EMAIL = "your-email@gmail.com"
# DEFAULT_TO_EMAIL = "your-email@gmail.com"

# Anymail

# https://anymail.dev/en/stable/esps/amazon_ses/

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "region_name": os.getenv("AWS_REGION"),
    },
}
