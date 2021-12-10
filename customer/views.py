from django.shortcuts import render
from rest_framework import generics

from customer.models import Customer
from customer.serializers import CustomerSerializer


class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.order_by("-id").all()
    serializer_class = CustomerSerializer

    list_display = ["id", "name"]
