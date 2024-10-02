import os
import uuid

from django_resized import ResizedImageField


class CustomerImageField(ResizedImageField):
    def generate_filename(self, instance, filename):
        _, ext = os.path.splitext(filename)
        name = f"{uuid.uuid4().hex}{ext}"
        return super().generate_filename(instance, name)
