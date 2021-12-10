import os
import uuid

from sorl.thumbnail import ImageField


class CustomerImageField(ImageField):
    def generate_filename(self, instance, filename):
        _, ext = os.path.splitext(filename)
        name = f"{uuid.uuid4().hex}{ext}"
        return super().generate_filename(instance, name)
