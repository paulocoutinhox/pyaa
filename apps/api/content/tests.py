import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from apps.content.models import Content, ContentCategory
from apps.language.models import Language
from pyaa.fastapi.jwt import create_access_token

User = get_user_model()


def _build_user(email):
    return User.objects.create_user(
        username=email,
        email=email,
        password="testpassword",
        first_name="Content",
        last_name="User",
        mobile_phone="1234567890",
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    user = _build_user("content-admin@example.com")
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser"])
    return user


@pytest.fixture
def user_without_permission(db):
    return _build_user("content-plain@example.com")


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


def test_create_content(client, admin_user):
    token = create_access_token(admin_user)
    response = client.post(
        "/api/content",
        json={"title": "New Content", "content": "Body text"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Content"
    assert data["tag"] == "new-content"
    assert Content.objects.filter(tag="new-content").exists()


def test_create_content_requires_authentication(client):
    response = client.post("/api/content", json={"title": "No Auth"})
    assert response.status_code == 401


def test_create_content_forbidden_without_permission(client, user_without_permission):
    token = create_access_token(user_without_permission)
    response = client.post(
        "/api/content",
        json={"title": "New Content", "content": "Body text"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
