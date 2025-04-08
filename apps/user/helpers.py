from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from pycpfcnpj import cpf


class UserHelper:
    @staticmethod
    def validate_unique_email(email, site_id, pk=None, error_class=ValidationError):
        from apps.user.models import User

        if email:
            query = User.objects.filter(email=email, site_id=site_id)

            if pk:
                query = query.exclude(pk=pk)

            if query.exists():
                raise error_class({"email": _("error.email-already-used-by-other")})

    @staticmethod
    def validate_unique_cpf(cpf, site_id, pk=None, error_class=ValidationError):
        from apps.user.models import User

        if cpf:
            query = User.objects.filter(cpf=cpf, site_id=site_id)

            if pk:
                query = query.exclude(pk=pk)

            if query.exists():
                raise error_class({"cpf": _("error.cpf-already-used-by-other")})

    @staticmethod
    def validate_unique_mobile_phone(
        mobile_phone, site_id, pk=None, error_class=ValidationError
    ):
        from apps.user.models import User

        if mobile_phone:
            query = User.objects.filter(mobile_phone=mobile_phone, site_id=site_id)

            if pk:
                query = query.exclude(pk=pk)

            if query.exists():
                raise error_class(
                    {"mobile_phone": _("error.mobile-phone-already-used-by-other")}
                )

    @staticmethod
    def validate_unique_fields(
        email=None,
        cpf=None,
        mobile_phone=None,
        site_id=None,
        pk=None,
        error_class=ValidationError,
    ):
        UserHelper.validate_unique_email(email, site_id, pk, error_class)
        UserHelper.validate_unique_cpf(cpf, site_id, pk, error_class)
        UserHelper.validate_unique_mobile_phone(mobile_phone, site_id, pk, error_class)

    @staticmethod
    def validate_cpf(value):
        if value:
            if not cpf.validate(value):
                raise ValidationError(_("error.invalid-cpf"))

        return value
