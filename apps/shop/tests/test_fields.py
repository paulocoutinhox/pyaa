from django.test import TestCase

from apps.shop.fields import PlanImageField, ProductFileField, ProductImageField


class ShopFieldsTest(TestCase):
    def test_product_image_field_generates_uuid_name(self):
        field = ProductImageField(upload_to="images/product/%Y/%m/%d")

        first = field.generate_filename(None, "Photo.JPG")
        second = field.generate_filename(None, "Photo.JPG")

        self.assertTrue(first.endswith(".JPG"))
        self.assertNotEqual(first, second)

    def test_plan_image_field_generates_uuid_name(self):
        field = PlanImageField(upload_to="images/plan/%Y/%m/%d")

        filename = field.generate_filename(None, "banner.png")

        self.assertTrue(filename.endswith(".png"))

    def test_product_file_field_generates_uuid_name(self):
        field = ProductFileField(upload_to="files/product/%Y/%m/%d")

        first = field.generate_filename(None, "document.pdf")
        second = field.generate_filename(None, "document.pdf")

        self.assertTrue(first.endswith(".pdf"))
        self.assertNotEqual(first, second)
