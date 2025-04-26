from rest_framework import serializers

from apps.banner.models import Banner


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = [
            "title",
            "image",
            "link",
            "target_blank",
            "zone",
            "token",
            "sort_order",
            "start_at",
            "end_at",
        ]
