from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase

from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery


class GalleryHelperBranchTest(TestCase):
    def setUp(self):
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.gallery = Gallery.objects.create(
            site=self.site,
            title="Branch Gallery",
            tag="branch-gallery",
            active=True,
        )

    def tearDown(self):
        cache.clear()

    def test_get_gallery_with_explicit_site_id(self):
        # passing site_id skips the get_current() lookup (13->18)
        result = GalleryHelper.get_gallery(
            gallery_id=self.gallery.id, site_id=self.site.id
        )
        self.assertEqual(result, self.gallery)

    def test_get_gallery_by_id_not_found(self):
        # a missing gallery id skips the cache.set call (53->57)
        result = GalleryHelper.get_gallery(gallery_id=999999)
        self.assertIsNone(result)

    def test_get_gallery_by_tag_with_falsy_language(self):
        # get_language returning None skips the lower() branches (25->27, 63->66)
        with patch("apps.gallery.helpers.get_language", return_value=None):
            result = GalleryHelper.get_gallery(gallery_tag="branch-gallery")
            self.assertEqual(result, self.gallery)

    def test_get_gallery_list_with_explicit_site_id(self):
        # passing site_id skips the get_current() lookup (109->113)
        result = GalleryHelper.get_gallery_list(site_id=self.site.id)
        self.assertIsNotNone(result)

    def test_get_gallery_list_with_falsy_language(self):
        # get_language returning None skips the lower() branch (115->119)
        with patch("apps.gallery.helpers.get_language", return_value=None):
            result = GalleryHelper.get_gallery_list(site_id=self.site.id)
            self.assertIsNotNone(list(result))
