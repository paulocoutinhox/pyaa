import os
import re
import uuid


class StringHelper:
    @staticmethod
    def only_numbers(value):
        if value:
            data = re.sub("[^0-9]", "", value)
            return data
        else:
            return None


class FileHelper:
    @staticmethod
    def ckeditor_generate_filename(filename, request):
        _, ext = os.path.splitext(filename)
        name = f"{uuid.uuid4().hex}{ext}"
        return name
