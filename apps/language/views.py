from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.language.models import Language
from apps.language.serializers import LanguageSerializer


class LanguageList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Language.objects.order_by("-id").all()
    serializer_class = LanguageSerializer
