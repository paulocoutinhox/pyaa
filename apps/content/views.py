from rest_framework import generics

from apps.content.models import Content
from apps.content.serializers import ContentSerializer
from pyaa.helpers import AppModelPermissions


class ContentList(generics.ListCreateAPIView):
    queryset = Content.objects.order_by("-id").all()
    serializer_class = ContentSerializer
    permission_classes = [AppModelPermissions]

    list_display = ["id", "title"]
