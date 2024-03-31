import pathlib
import re
import uuid

from rest_framework.permissions import DjangoModelPermissions


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


class AppModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
