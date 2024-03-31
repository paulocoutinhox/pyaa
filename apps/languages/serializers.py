from rest_framework import serializers

from apps.languages.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "id",
            "name",
        ]
