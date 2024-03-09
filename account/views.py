from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated

from account.models import Customer
from account.serializers import CustomerSerializer


class CustomerView(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Customer.objects.order_by("-id").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SingleCustomerView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
