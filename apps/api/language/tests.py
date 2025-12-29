from apps.language.models import Language


def test_list_languages(client):
    response = client.get("/api/language")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) > 0


def test_list_languages_with_pagination(client):
    response = client.get("/api/language?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2


def test_create_language(client):
    language_data = {
        "name": "Test Language",
        "nativeName": "Test Native",
        "codeIso6391": "tl",
        "codeIsoLanguage": "test",
    }

    response = client.post("/api/language", json=language_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Language"
    assert data["codeIso6391"] == "tl"

    language = Language.objects.get(code_iso_639_1="tl")
    assert language.name == "Test Language"
