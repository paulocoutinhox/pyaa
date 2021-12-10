from django.shortcuts import render
from rest_framework import generics

from language.models import Language
from language.serializers import LanguageSerializer


class LanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.order_by("-id").all()
    serializer_class = LanguageSerializer

    list_display = ["id", "name"]
