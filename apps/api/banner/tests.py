import uuid

import pytest
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner
from apps.language.models import Language


@pytest.fixture
def site(db):
    return Site.objects.get_current()


@pytest.fixture
def language(db):
    return Language.objects.get(id=1)


@pytest.fixture
def banner(site, language):
    image = SimpleUploadedFile(
        "test.jpg",
        b"file_content",
        content_type="image/jpeg",
    )
    return Banner.objects.create(
        site=site,
        language=language,
        zone=BannerZone.HOME,
        title="Test Banner",
        image=image,
        link="https://example.com",
        active=True,
        start_at=timezone.now(),
        end_at=timezone.now() + timezone.timedelta(days=30),
    )


def test_list_banners(client, banner):
    response = client.get(f"/api/banner?zone={BannerZone.HOME.value}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_banners_with_language(client, banner):
    response = client.get(f"/api/banner?zone={BannerZone.HOME.value}&language=en")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_banners_with_site(client, banner, site):
    response = client.get(f"/api/banner?zone={BannerZone.HOME.value}&site={site.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_track_banner_access_view(client, banner):
    response = client.get(
        f"/api/banner/access/{banner.token}?type={BannerAccessType.VIEW.value}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_track_banner_access_click(client, banner):
    response = client.get(
        f"/api/banner/access/{banner.token}?type={BannerAccessType.CLICK.value}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_track_banner_access_not_found(client):
    invalid_uuid = uuid.uuid4()
    response = client.get(
        f"/api/banner/access/{invalid_uuid}?type={BannerAccessType.VIEW.value}"
    )
    assert response.status_code == 404


def test_track_banner_access_invalid_type(client, banner):
    response = client.get(f"/api/banner/access/{banner.token}?type=invalid")
    assert response.status_code == 400
