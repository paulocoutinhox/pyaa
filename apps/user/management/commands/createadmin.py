import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands.createsuperuser import (
    Command as BaseCommand,
)
from django.core.management import CommandError
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = "Create a superuser with additional fields like email, CPF, mobile phone and password."

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--email",
            type=str,
            help="Email for the superuser",
        )

        parser.add_argument(
            "--cpf",
            type=str,
            help="CPF for the superuser",
        )

        parser.add_argument(
            "--mobile_phone",
            type=str,
            help="Mobile phone for the superuser",
        )

        parser.add_argument(
            "--password",
            type=str,
            help="Password for the superuser",
        )

    def handle(self, *args, **options):
        username = options.get("username")
        email = options.get("email")
        cpf = options.get("cpf")
        mobile_phone = options.get("mobile_phone")
        password = options.get("password")
        database = options.get("database")

        if not username:
            username = str(uuid.uuid4())

        if not any([email, cpf, mobile_phone]):
            raise CommandError(_("error.at-least-one-login-provider-is-required"))

        if not password:
            raise CommandError(_("error.password-required"))

        UserModel = get_user_model()

        try:
            UserModel.objects.db_manager(database).create_superuser(
                username=username,
                password=password,
                email=email,
                cpf=cpf,
                mobile_phone=mobile_phone,
            )

            self.stdout.write(
                self.style.SUCCESS(_("message.superuser-created-successfully"))
            )
        except Exception as e:
            raise CommandError(
                _("error.superuser-creation-failed: {error}").format(error=str(e))
            )
