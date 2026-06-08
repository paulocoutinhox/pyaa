from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.banner.enums import BannerZone
from apps.banner.models import Banner
from apps.language import models as language_models


class HomeIndexViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()

        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Home Banner",
            image="home_banner.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

    def test_home_renders_with_banners(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home/index.html")
        self.assertIn("banners", response.context)
        self.assertIn(self.banner, list(response.context["banners"]))


class SetLanguageViewTest(TestCase):
    @override_settings(
        LANGUAGES=[("en", "English"), ("pt-br", "Portuguese")],
        LANGUAGE_CODE="en-us",
    )
    def test_set_language_with_supported_code(self):
        response = self.client.get(
            reverse("set_language", kwargs={"language_code": "en"})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

        cookie = response.cookies.get("django_language")
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, "en")

    @override_settings(
        LANGUAGES=[("en", "English")],
        LANGUAGE_CODE="en-us",
    )
    def test_set_language_with_unsupported_code_falls_back(self):
        response = self.client.get(
            reverse("set_language", kwargs={"language_code": "zz"})
        )

        self.assertEqual(response.status_code, 302)
        cookie = response.cookies.get("django_language")
        self.assertEqual(cookie.value, "en")
