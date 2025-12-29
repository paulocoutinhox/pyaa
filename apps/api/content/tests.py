import pytest
from django.contrib.sites.models import Site

from apps.content.models import Content, ContentCategory
from apps.language.models import Language


@pytest.fixture
def site(db):
    return Site.objects.get_current()


@pytest.fixture
def language(db):
    return Language.objects.get(id=1)


@pytest.fixture
def category(db):
    return ContentCategory.objects.create(name="Test Category", tag="test-category")


@pytest.fixture
def content(site, language, category):
    return Content.objects.create(
        site=site,
        language=language,
        category=category,
        title="Test Content",
        tag="test-content",
        content="Test content text",
        active=True,
    )


def test_get_content_by_tag(client, content):
    response = client.get("/api/content/test-content")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Content"
    assert data["tag"] == "test-content"
    assert data["content"] == "Test content text"


def test_get_content_by_tag_not_found(client):
    response = client.get("/api/content/non-existent")
    assert response.status_code == 404


def test_get_inactive_content(client, content):
    content.active = False
    content.save()

    response = client.get("/api/content/test-content")
    assert response.status_code == 404
