import pytest
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.testclient import TestClient

from pyaa.fastapi import cors
from pyaa.fastapi.routes import router


@pytest.fixture(scope="session")
def app():
    from django.core.wsgi import get_wsgi_application

    app = FastAPI(
        title=_("site.small-name"),
        debug=settings.DEBUG,
    )

    app.include_router(router, prefix="/api")
    cors.setup(app)

    django_app = get_wsgi_application()
    app.mount("/", WSGIMiddleware(django_app))

    return app


@pytest.fixture
def client(app, transactional_db):
    from django.db import connections

    for conn in connections.all():
        conn.inc_thread_sharing()

    try:
        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client
    finally:
        for conn in connections.all():
            conn.dec_thread_sharing()


@pytest.fixture(autouse=True)
def load_fixtures(db):
    from django.core.management import call_command

    call_command("loaddata", "initial")
