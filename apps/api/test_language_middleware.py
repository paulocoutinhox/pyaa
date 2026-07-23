import pytest
from django.utils import translation
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pyaa.fastapi import language


@pytest.fixture
def lang_client():
    # build a minimal app with only the language middleware so we can
    # observe the active translation per request
    app = FastAPI()

    @app.get("/lang")
    async def get_lang():
        return {"lang": translation.get_language()}

    language.setup(app)

    with TestClient(app) as test_client:
        yield test_client


def test_no_header_uses_default_language(lang_client):
    # without an accept-language header it falls back to settings.LANGUAGE_CODE
    response = lang_client.get("/lang")

    assert response.status_code == 200
    assert response.json()["lang"] == "en"


def test_exact_match_pt_br(lang_client):
    response = lang_client.get("/lang", headers={"Accept-Language": "pt-BR"})

    assert response.status_code == 200
    assert response.json()["lang"] == "pt-br"


def test_exact_match_en(lang_client):
    response = lang_client.get("/lang", headers={"Accept-Language": "en"})

    assert response.status_code == 200
    assert response.json()["lang"] == "en"


def test_base_language_match(lang_client):
    # "pt" is not an exact supported language, base "pt" matches "pt-br"
    response = lang_client.get("/lang", headers={"Accept-Language": "pt"})

    assert response.status_code == 200
    assert response.json()["lang"] == "pt-br"


def test_multiple_languages_uses_first(lang_client):
    # only the first language in the list is considered
    response = lang_client.get("/lang", headers={"Accept-Language": "pt-br,en;q=0.9"})

    assert response.status_code == 200
    assert response.json()["lang"] == "pt-br"


def test_unsupported_language_falls_back_to_default(lang_client):
    # "fr-fr" has no exact match and base "fr" matches nothing, so it falls
    # back to settings.LANGUAGE_CODE
    response = lang_client.get("/lang", headers={"Accept-Language": "fr-FR"})

    assert response.status_code == 200
    assert response.json()["lang"] == "en-us"


def test_translation_deactivated_after_request(lang_client):
    # after the request completes the middleware deactivates the translation
    lang_client.get("/lang", headers={"Accept-Language": "pt-br"})

    assert translation.get_language() != "pt-br"
