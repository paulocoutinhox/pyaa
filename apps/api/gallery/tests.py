import pytest
from django.contrib.sites.models import Site
from django.utils import timezone

from apps.gallery.models import Gallery
from apps.language.models import Language


@pytest.fixture
def site(db):
    return Site.objects.get_current()


@pytest.fixture
def language(db):
    return Language.objects.get(id=1)


@pytest.fixture
def gallery1(site, language):
    return Gallery.objects.create(
        site=site,
        language=language,
        title="Gallery 1",
        tag="gallery-1",
        active=True,
        published_at=timezone.now(),
    )


@pytest.fixture
def gallery2(site, language):
    return Gallery.objects.create(
        site=site,
        language=language,
        title="Gallery 2",
        tag="gallery-2",
        active=True,
        published_at=timezone.now(),
    )


@pytest.fixture
def inactive_gallery(site, language):
    return Gallery.objects.create(
        site=site,
        language=language,
        title="Inactive Gallery",
        tag="inactive-gallery",
        active=False,
        published_at=timezone.now(),
    )


def test_list_galleries(client, gallery1, gallery2, inactive_gallery):
    response = client.get("/api/gallery")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert data["count"] == 2


def test_list_galleries_pagination(client, gallery1, gallery2):
    response = client.get("/api/gallery?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_list_galleries_excludes_inactive(client, gallery1, gallery2, inactive_gallery):
    response = client.get("/api/gallery")
    assert response.status_code == 200
    data = response.json()
    tags = [item["tag"] for item in data["items"]]
    assert "inactive-gallery" not in tags


def test_get_gallery_by_tag(client, gallery1):
    response = client.get("/api/gallery/gallery-1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Gallery 1"
    assert data["tag"] == "gallery-1"


def test_get_gallery_by_tag_not_found(client):
    response = client.get("/api/gallery/non-existent")
    assert response.status_code == 404


def test_get_inactive_gallery(client, inactive_gallery):
    response = client.get("/api/gallery/inactive-gallery")
    assert response.status_code == 404


def test_get_gallery_with_photos(client, site, language):
    from apps.gallery.models import GalleryPhoto
    from io import BytesIO
    from PIL import Image as PILImage
    from django.core.files.uploadedfile import SimpleUploadedFile

    gallery = Gallery.objects.create(
        site=site,
        language=language,
        title="Gallery with Photos",
        tag="gallery-with-photos",
        active=True,
        published_at=timezone.now(),
    )

    img = PILImage.new("RGB", (100, 100), color="red")
    img_io = BytesIO()
    img.save(img_io, format="JPEG")
    img_io.seek(0)

    image = SimpleUploadedFile("photo.jpg", img_io.read(), content_type="image/jpeg")

    GalleryPhoto.objects.create(
        gallery=gallery, image=image, caption="Test Photo", main=True
    )

    response = client.get("/api/gallery/gallery-with-photos")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Gallery with Photos"
    assert len(data["photos"]) == 1
    assert data["photos"][0]["caption"] == "Test Photo"
    assert data["photos"][0]["main"] is True
