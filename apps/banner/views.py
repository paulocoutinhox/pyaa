from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.banner.enums import BannerAccessType
from apps.banner.helpers import BannerHelper
from apps.banner.serializers import BannerSerializer
from pyaa.mixins import OptionalJWTAuthenticationMixin


class BannerListAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer

    def get(self, request):
        zone = request.GET.get("zone")
        if not zone:
            return Response(
                {"error": "Zone parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        language = request.GET.get("language")
        site_id = request.GET.get("site")

        banners = BannerHelper.get_banners(
            zone=zone,
            language=language,
            site_id=site_id,
        )

        serializer = self.serializer_class(banners, many=True)
        return Response(serializer.data)


class BannerAccessAPIView(OptionalJWTAuthenticationMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        banner = BannerHelper.get_banner_by_token(token)

        if not banner:
            return Response(
                {"error": "Banner not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        access_type = request.GET.get("type")

        if access_type == BannerAccessType.VIEW.value:
            tracked = BannerHelper.track_banner_access(
                request, banner, BannerAccessType.VIEW
            )
        elif access_type == BannerAccessType.CLICK.value:
            tracked = BannerHelper.track_banner_access(
                request, banner, BannerAccessType.CLICK
            )
        else:
            return Response(
                {"error": "Invalid access type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"success": tracked})
