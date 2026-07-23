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
