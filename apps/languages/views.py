from rest_framework import generics

from apps.languages.models import Language
from apps.languages.serializers import LanguageSerializer
from pyaa.helpers import AppModelPermissions


class LanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.order_by("-id").all()
    serializer_class = LanguageSerializer
    permission_classes = [AppModelPermissions]

    list_display = ["id", "name"]
