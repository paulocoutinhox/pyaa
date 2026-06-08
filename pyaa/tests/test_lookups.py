from django.test import TestCase

from apps.banner.enums import BannerZone
from apps.banner.models import Banner

# importing registers the bitwise lookups on IntegerField
import pyaa.lookups.integer  # noqa: F401


class BitwiseLookupTest(TestCase):
    def setUp(self):
        # sort_order is used here as a bit flag holder
        self.banner_flag_1 = Banner.objects.create(
            title="Flag 1",
            image="a.jpg",
            zone=BannerZone.HOME,
            sort_order=0b001,
        )
        self.banner_flag_3 = Banner.objects.create(
            title="Flag 3",
            image="b.jpg",
            zone=BannerZone.HOME,
            sort_order=0b011,
        )
        self.banner_flag_4 = Banner.objects.create(
            title="Flag 4",
            image="c.jpg",
            zone=BannerZone.HOME,
            sort_order=0b100,
        )

    def test_bitand_present_matches_records_with_bit(self):
        result = Banner.objects.filter(sort_order__bitand_present=0b001)
        self.assertCountEqual(result, [self.banner_flag_1, self.banner_flag_3])

    def test_bitand_present_matches_higher_bit(self):
        result = Banner.objects.filter(sort_order__bitand_present=0b100)
        self.assertCountEqual(result, [self.banner_flag_4])

    def test_bitand_not_present_excludes_records_with_bit(self):
        result = Banner.objects.filter(sort_order__bitand_not_present=0b001)
        self.assertCountEqual(result, [self.banner_flag_4])

    def test_bitand_not_present_for_unset_bit(self):
        result = Banner.objects.filter(sort_order__bitand_not_present=0b100)
        self.assertCountEqual(result, [self.banner_flag_1, self.banner_flag_3])
