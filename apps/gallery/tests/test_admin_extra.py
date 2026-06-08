from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.gallery.admin import GalleryAdmin
from apps.gallery.models import Gallery


class GalleryAdminSiteNameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = GalleryAdmin(Gallery, AdminSite())
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()

    def test_site_name_with_site(self):
        gallery = Gallery.objects.create(
            site=self.site,
            title="With Site",
            tag="with-site",
        )
        self.assertEqual(self.admin.site_name(gallery), self.site.name)

    def test_site_name_without_site(self):
        gallery = Gallery.objects.create(
            site=None,
            title="No Site",
            tag="no-site",
        )
        self.assertIsNone(self.admin.site_name(gallery))
