from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin

from account.models import Customer
from account.serializers import CustomerSerializer
from language.models import Language


class CustomerView(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Customer.objects.order_by("-id").all()
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SingleCustomerView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
