from django.test import TestCase

from apps.banner.enums import BannerAccessType, BannerZone


class BannerEnumsTest(TestCase):

    def test_banner_zone_get_choices(self):
        choices = BannerZone.get_choices()
        self.assertIsInstance(choices, tuple)
        self.assertGreater(len(choices), 0)

        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)

    def test_banner_access_type_get_choices(self):
        choices = BannerAccessType.get_choices()
        self.assertIsInstance(choices, tuple)
        self.assertGreater(len(choices), 0)

        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
