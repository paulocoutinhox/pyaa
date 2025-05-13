from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.system_log.helpers import SystemLogHelper
from pyaa.mixins import OptionalJWTAuthenticationMixin


class SystemLogAPIView(OptionalJWTAuthenticationMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # check if system log api is enabled
        if not settings.SYSTEM_LOG_API_ENABLED:
            return Response(
                {"error": "System log API is disabled"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # get required fields
        level = request.data.get("level")
        description = request.data.get("description")

        # validate required fields
        if not level or not description:
            return Response(
                {"error": "Level and description are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # optional fields
        category = request.data.get("category")

        # get customer if logged in
        customer = None
        if request.user.is_authenticated and request.user.has_customer():
            customer = request.user.customer

        # create log entry
        try:
            SystemLogHelper.create(
                level=level,
                description=description,
                category=category,
                customer=customer,
            )

            return Response({"success": True})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
