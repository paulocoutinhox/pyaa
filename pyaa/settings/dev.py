"""
Django settings for the project.

Generated by 'django-admin startproject' using Django.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# General

DEBUG = True
SECRET_KEY = "myapp-secret-key"

# Hosts

ALLOWED_HOSTS = ["*"]

csrf_trusted_origins = os.getenv("APP_CSRF_TRUSTED_ORIGINS")
if csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = csrf_trusted_origins.split(",")

allowed_hosts = os.getenv("APP_ALLOWED_HOSTS")
if allowed_hosts:
    ALLOWED_HOSTS = allowed_hosts.split(",")

# Application definition

DJANGO_APPS = [
    "pyaa.apps.AppAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "compressor",
    "sass_processor",
    "django_admin_extras",
    "django_cleanup.apps.CleanupConfig",
    "sorl.thumbnail",
    "tinymce",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    "widget_tweaks",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "cache_cleaner",
    "captcha",
]

PROJECT_APPS = [
    "apps.user.apps.UserAppConfig",
    "apps.web.apps.WebAppConfig",
    "apps.customer.apps.CustomerAppConfig",
    "apps.language.apps.LanguageAppConfig",
    "apps.content.apps.ContentAppConfig",
    "apps.gallery.apps.GalleryAppConfig",
    "apps.shop.apps.ShopAppConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "pyaa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pyaa.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "db.sqlite3",
        "TEST": {
            "NAME": BASE_DIR / "db" / "db-test.sqlite3",
        },
    }
}

# Cache
# https://docs.djangoproject.com/en/5.0/topics/cache/
# https://www.honeybadger.io/blog/caching-in-django/

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("language.en")),
    ("pt-br", _("language.pt-br")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

DEFAULT_TIME_ZONE = "America/Sao_Paulo"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    BASE_DIR / "apps" / "web" / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
    "sass_processor.finders.CssFinder",
]

SASS_PROCESSOR_INCLUDE_DIRS = []
SASS_PROCESSOR_AUTO_INCLUDE = False
SASS_PROCESSOR_ROOT = BASE_DIR / "apps" / "web" / "static"

# Compress static files

COMPRESS_ROOT = BASE_DIR / "static"
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# Messages

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Rest framework

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.DjangoModelPermissions",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "1/second", "user": None},
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Spectacular

SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

# Simple JWT

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365 * 1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365 * 1),
}

# Media

MEDIA_URL = os.getenv("APP_MEDIA_URL", "/media/")
MEDIA_ROOT = BASE_DIR / "media"

# Editor

UPLOAD_PATH = "uploads"

TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "100%",
    "menubar": False,
    "plugins": "advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table code help wordcount",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | insertfile image media pageembed template link anchor codesample | charmap emoticons | fullscreen preview save print | a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
    "images_upload_url": "/upload_image/",
    "relative_urls": False,
    "remove_script_host": False,
    "convert_urls": True,
    "valid_elements": "*[*]",
}

# CORS

CORS_ALLOW_ALL_ORIGINS = True

# Auth

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "home"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = "apps.web.adapter.AppAccountAdapter"
ACCOUNT_FORMS = {
    "signup": "apps.customer.forms.CustomerSignupForm",
}
AUTH_USER_MODEL = "user.User"

# Email

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging

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
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "debug.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "DEBUG",
    },
}

# Customer

CUSTOMER_INITIAL_CREDITS = 0

# Stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
