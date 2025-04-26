import re

from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.authentication import JWTAuthentication


class OptionalJWTAuthenticationMixin:
    """Mixin that provides optional JWT authentication."""

    authentication_classes = [JWTAuthentication]

    def perform_authentication(self, request):
        try:
            super().perform_authentication(request)
        except Exception:
            pass


class ReadonlyLinksMixin:
    @staticmethod
    def _make_link_widget(field_name, admin_view):
        def link_widget(instance):
            # get the field value
            field = getattr(instance, field_name, None)

            if field is None:
                return "None"

            # generate the link to the related object
            link = reverse(admin_view, args=(field.id,))

            return mark_safe('<a href="%s">%s</a>' % (link, escape(str(field))))

        return link_widget

    def get_readonly_fields(self, request, obj=None):
        # cache readonly fields to avoid admin inconsistencies
        try:
            return self._link_readonly_fields
        except AttributeError:
            pass

        # get initial readonly fields from the parent admin
        initial_readonly_fields = super().get_readonly_fields(request, obj)
        link_readonly_fields = list(initial_readonly_fields)  # ensure it's a list

        # check if readonly_fields_links is defined
        if hasattr(self, "readonly_fields_links"):
            for field_name in self.readonly_fields_links:
                try:
                    # get field metadata to determine its admin view
                    field = getattr(obj, field_name) if obj else None
                    app_label = field._meta.app_label
                    model_name = field._meta.model_name
                except AttributeError:
                    # if it's not a related model, add it as a normal readonly field
                    link_readonly_fields.append(field_name)
                    continue

                # define the admin view for the link
                admin_view = f"admin:{app_label}_{model_name}_change"

                link_widget = self._make_link_widget(field_name, admin_view)
                link_widget.short_description = self.model._meta.get_field(
                    field_name
                ).verbose_name

                link_readonly_fields.append(field_name)

        self._link_readonly_fields = link_readonly_fields

        return link_readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # remove editable widgets for readonly_links fields
        if hasattr(self, "readonly_fields_links"):
            for field_name in self.readonly_fields_links:
                if field_name in form.base_fields:
                    del form.base_fields[field_name]

        return form


class SanitizeDigitFieldsMixin:
    """
    Mixin to automatically sanitize specified fields by removing all non-digit characters.
    """

    digit_only_fields = []

    def clean(self):
        cleaned_data = super().clean()

        for field in getattr(self, "digit_only_fields", []):
            value = cleaned_data.get(field)
            if value:
                cleaned_data[field] = re.sub(r"\D", "", str(value))

        return cleaned_data
