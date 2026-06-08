from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase

from apps.content.helpers import ContentHelper
from apps.content.models import Content


class ContentHelperBranchTest(TestCase):
    def setUp(self):
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.content = Content.objects.create(
            site=self.site,
            title="Branch Content",
            content="body",
            tag="branch-content",
            active=True,
        )

    def tearDown(self):
        cache.clear()

    def test_get_content_with_explicit_site_id(self):
        # passing site_id skips the get_current() lookup (13->18)
        result = ContentHelper.get_content(
            content_id=self.content.id, site_id=self.site.id
        )
        self.assertEqual(result, self.content)

    def test_get_content_by_id_not_found(self):
        # a missing content id skips the cache.set call (52->56)
        result = ContentHelper.get_content(content_id=999999)
        self.assertIsNone(result)

    def test_get_content_by_tag_with_falsy_language(self):
        # get_language returning None skips the lower() branches (25->27, 63->66)
        with patch("apps.content.helpers.get_language", return_value=None):
            result = ContentHelper.get_content(content_tag="branch-content")
            self.assertEqual(result, self.content)
