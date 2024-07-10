import pathlib
import uuid


class FileHelper:
    @staticmethod
    def generate_filename(file_obj):
        file_name_suffix = pathlib.Path(file_obj.name).suffix
        return str(uuid.uuid4()) + file_name_suffix.lower()
