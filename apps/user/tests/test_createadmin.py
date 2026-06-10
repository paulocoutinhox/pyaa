from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import CommandError, call_command
from django.test import TestCase

User = get_user_model()


class CreateAdminCommandTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()

    def test_create_admin_with_email(self):
        # creating a new admin user with an email should succeed
        out = StringIO()

        call_command(
            "createadmin",
            email="admin@example.com",
            password="strongpass",
            site_id=self.site.id,
            stdout=out,
        )

        user = User.objects.get(email="admin@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("strongpass"))
        self.assertEqual(user.site_id, self.site.id)
        self.assertIn("successfully", out.getvalue())

    def test_create_admin_with_cpf_only(self):
        # at least one login provider (cpf here) is enough
        out = StringIO()

        call_command(
            "createadmin",
            cpf="52998224725",
            password="strongpass",
            stdout=out,
        )

        self.assertTrue(User.objects.filter(cpf="52998224725").exists())

    def test_create_admin_generates_username_when_missing(self):
        # without a username the command generates a uuid one
        out = StringIO()

        call_command(
            "createadmin",
            email="autouser@example.com",
            password="strongpass",
            stdout=out,
        )

        user = User.objects.get(email="autouser@example.com")
        self.assertTrue(user.username)

    def test_missing_login_provider_raises(self):
        # without email, cpf or mobile phone the command must fail
        with self.assertRaises(CommandError) as ctx:
            call_command("createadmin", password="strongpass")

        self.assertIn("At least one login method is required.", str(ctx.exception))

    def test_missing_password_raises(self):
        # password is mandatory
        with self.assertRaises(CommandError) as ctx:
            call_command("createadmin", email="nopass@example.com")

        self.assertIn("Password is required.", str(ctx.exception))

    def test_duplicate_user_raises_creation_failed(self):
        # creating a second admin with the same email triggers the failure branch
        call_command(
            "createadmin",
            email="dup@example.com",
            password="strongpass",
            site_id=self.site.id,
            stdout=StringIO(),
        )

        with self.assertRaises(CommandError) as ctx:
            call_command(
                "createadmin",
                email="dup@example.com",
                password="strongpass",
                site_id=self.site.id,
            )

        self.assertIn("Super user creation failed", str(ctx.exception))
