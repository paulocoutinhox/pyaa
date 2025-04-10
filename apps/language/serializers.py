from rest_framework import serializers

from apps.language.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "id",
            "name",
            "native_name",
            "code_iso_639_1",
            "code_iso_language",
        ]
