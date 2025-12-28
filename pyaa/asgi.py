"""
ASGI config for the project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyaa.settings.dev")
apps.populate(settings.INSTALLED_APPS)

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles

from pyaa.fastapi import cors, rate_limiter
from pyaa.fastapi.routes import router


def get_application() -> FastAPI:
    # -------------------------------------------------
    # fastapi docs urls
    # -------------------------------------------------
    docs_url = None
    redoc_url = None
    openapi_url = None

    if settings.PYAA_ENABLE_FASTAPI:
        api_prefix = settings.PYAA_API_PREFIX

        docs_url = f"{api_prefix}/docs"
        redoc_url = f"{api_prefix}/redoc"
        openapi_url = f"{api_prefix}/openapi.json"

    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # -------------------------------------------------
    # fastapi api
    # -------------------------------------------------
    if settings.PYAA_ENABLE_FASTAPI:
        app.include_router(
            router,
            prefix=settings.PYAA_API_PREFIX,
        )

        rate_limiter.setup(app)
        cors.setup(app)

    # -------------------------------------------------
    # static / media
    # -------------------------------------------------
    if settings.PYAA_ENABLE_DJANGO and not settings.DEBUG:
        if settings.STATIC_URL.startswith("/"):
            app.mount(
                settings.STATIC_URL,
                StaticFiles(directory=settings.STATIC_ROOT),
                name="static",
            )

        if settings.MEDIA_URL.startswith("/"):
            app.mount(
                settings.MEDIA_URL,
                StaticFiles(directory=settings.MEDIA_ROOT),
                name="media",
            )

    # -------------------------------------------------
    # django
    # -------------------------------------------------
    if settings.PYAA_ENABLE_DJANGO:
        app.mount(
            "/",
            WSGIMiddleware(get_wsgi_application()),
        )

    return app


application = get_application()
