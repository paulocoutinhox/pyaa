from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q


class MultiFieldModelBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        site_id = settings.SITE_ID

        if not site_id:
            return None

        # try to find the user using email, cpf or mobile_phone
        user = (
            UserModel.objects.filter(site_id=site_id)
            .filter(Q(email=username) | Q(cpf=username) | Q(mobile_phone=username))
            .first()
        )

        # check if the provided password is correct
        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        UserModel = get_user_model()

        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
