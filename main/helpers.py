import pathlib
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
    def generate_filename(file_obj):
        file_name_suffix = pathlib.Path(file_obj.name).suffix
        return str(uuid.uuid4()) + file_name_suffix.lower()
