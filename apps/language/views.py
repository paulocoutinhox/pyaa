from rest_framework import generics

from apps.language.models import Language
from apps.language.serializers import LanguageSerializer
from pyaa.helpers.rest import AppModelPermissions


class LanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.order_by("-id").all()
    serializer_class = LanguageSerializer
    permission_classes = [AppModelPermissions]
