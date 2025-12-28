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
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
    )

    # fastapi api
    app.include_router(router, prefix="/api")

    rate_limiter.setup(app)
    cors.setup(app)

    # serve static/media
    if not settings.DEBUG:
        # static files
        if settings.STATIC_URL.startswith("/"):
            app.mount(
                settings.STATIC_URL,
                StaticFiles(directory=settings.STATIC_ROOT),
                name="static",
            )

        # media files
        if settings.MEDIA_URL.startswith("/"):
            app.mount(
                settings.MEDIA_URL,
                StaticFiles(directory=settings.MEDIA_ROOT),
                name="media",
            )

    # django handles everything else
    app.mount(
        "/",
        WSGIMiddleware(get_wsgi_application()),
    )

    return app


application = get_application()
