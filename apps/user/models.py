from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.language.helpers import LanguageHelper


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("first_name", "Super")
        extra_fields.setdefault("last_name", "User")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Meta:
        db_table = "user"

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    username = None
    email = models.EmailField(_("model.field.email"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def has_subscription(self):
        return False


@receiver(user_signed_up)
def on_user_signed_up(request, user: User, **kwargs):
    language = LanguageHelper.get_current()
    timezone = settings.DEFAULT_TIME_ZONE

    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "language": language,
            "timezone": timezone,
        },
    )

    if not created:
        customer.language = language
        customer.timezone = timezone
        customer.save()
