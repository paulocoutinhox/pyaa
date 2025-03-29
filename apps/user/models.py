import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.site.models import Site
from apps.user.helpers import UserHelper


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username=None, password=None, **extra_fields):
        site_id = settings.SITE_ID
        if not site_id:
            raise ValidationError({"site_id": _("error.site-id-required")})

        email = extra_fields.get("email")
        cpf = extra_fields.get("cpf")
        mobile_phone = extra_fields.get("mobile_phone")

        if not any([email, cpf, mobile_phone]):
            raise ValidationError(
                {"non_field_errors": _("error.at-least-one-login-provider-is-required")}
            )

        UserHelper.validate_unique_fields(
            email=email,
            cpf=cpf,
            mobile_phone=mobile_phone,
            site_id=site_id,
        )

        user = self.model(site_id=site_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError({"is_staff": _("Superuser must have is_staff=True.")})

        if extra_fields.get("is_superuser") is not True:
            raise ValidationError(
                {"is_superuser": _("Superuser must have is_superuser=True.")}
            )

        email = extra_fields.get("email")
        cpf = extra_fields.get("cpf")
        mobile_phone = extra_fields.get("mobile_phone")

        if not any([email, cpf, mobile_phone]):
            raise ValidationError(
                {"non_field_errors": _("error.at-least-one-login-provider-is-required")}
            )

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = _("model.user.name")
        verbose_name_plural = _("model.user.name.plural")
        unique_together = (("email", "site"), ("cpf", "site"), ("mobile_phone", "site"))

        indexes = [
            models.Index(
                fields=["first_name"],
                name="{0}_first_name".format(db_table),
            ),
            models.Index(
                fields=["last_name"],
                name="{0}_last_name".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    username = models.CharField(
        _("model.field.admin-username"),
        max_length=255,
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    email = models.EmailField(
        _("model.field.email"),
        max_length=255,
        blank=True,
        null=True,
    )

    cpf = models.CharField(
        _("model.field.cpf"),
        max_length=11,
        blank=True,
        null=True,
    )

    mobile_phone = models.CharField(
        _("model.field.mobile-phone"),
        max_length=11,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        super().clean()

        if self.pk is None:
            site_id = self.site_id or settings.SITE_ID

            if not site_id:
                raise ValidationError({"site_id": _("error.site-id-required")})

            if not self.email and not self.cpf and not self.mobile_phone:
                raise ValidationError(
                    {
                        "non_field_errors": _(
                            "error.at-least-one-login-provider-is-required"
                        )
                    }
                )

            UserHelper.validate_unique_fields(
                email=self.email,
                cpf=self.cpf,
                mobile_phone=self.mobile_phone,
                site_id=site_id,
            )

    def save(self, *args, **kwargs):
        if not self.site_id:
            self.site_id = settings.SITE_ID

        self.full_clean()

        super().save(*args, **kwargs)

    def get_customer(self):
        from apps.customer.models import Customer

        if self.is_authenticated:
            try:
                return self.customer
            except Customer.DoesNotExist:
                return None

        return None

    def validate_unique(self, exclude=None):
        pass

    def has_customer(self):
        if self.is_authenticated:
            try:
                if self.customer != None:
                    return True
            except:
                return False

        return False

    def get_full_name(self):
        full_name = self.first_name + " " + self.last_name
        return full_name.strip()

    def __str__(self):
        result = ""

        if self.first_name or self.last_name:
            result = self.first_name + " " + self.last_name
            result = result.strip()

        if self.email:
            if result:
                result += " - " + self.email
            else:
                result += self.email

        site = getattr(self, "site", None)

        if site:
            if result:
                result += " - " + site.name
            else:
                result += site.name

        return result
