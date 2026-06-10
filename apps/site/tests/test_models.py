from django.contrib.sites.models import Site
from django.test import TestCase

from apps.site.models import SiteProfile


class SiteProfileModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Example", domain="profile.example.com")

    def test_site_profile_creation(self):
        profile = SiteProfile.objects.create(
            site=self.site,
            title="Example Title",
            template_folder="example",
        )

        self.assertTrue(SiteProfile.objects.filter(site=self.site).exists())
        self.assertEqual(profile.title, "Example Title")
        self.assertEqual(profile.template_folder, "example")
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_site_profile_str(self):
        profile = SiteProfile.objects.create(site=self.site, title="Example Title")
        self.assertEqual(str(profile), "Example Title")

    def test_site_profile_optional_fields(self):
        profile = SiteProfile.objects.create(site=self.site)

        self.assertIsNone(profile.title)
        self.assertIsNone(profile.template_folder)

    def test_site_profile_related_name(self):
        profile = SiteProfile.objects.create(site=self.site, title="Example Title")
        self.assertEqual(self.site.profile, profile)
