from rest_framework import generics

from language.models import Language
from language.serializers import LanguageSerializer
from main.helpers import AppModelPermissions


class LanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.order_by("-id").all()
    serializer_class = LanguageSerializer
    permission_classes = [AppModelPermissions]

    list_display = ["id", "name"]
