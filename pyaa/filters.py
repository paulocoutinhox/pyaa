import re

from django_admin_extras import InputFilter


class MaskedInputFilter(InputFilter):
    """
    Filter with input mask support. Improves the input field by adding a mask pattern.
    """

    input_mask = None
    template = "admin/filter/masked_input_filter.html"

    def choices(self, changelist):
        # grab only the "all" option and pass the mask information
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        all_choice["input_mask"] = self.input_mask
        yield all_choice


class StringSanitizingFilter(InputFilter):
    """
    Filter that sanitizes input strings before using them in queries.
    Provides helper methods like only_digits() to remove non-numeric characters.
    """

    def sanitize_value(self, value):
        """
        Sanitize the input value. Override in subclasses.
        Default: returns the value unchanged.
        """
        return value

    def only_digits(self, value):
        """
        Remove all non-digit characters from the input value.
        """
        if value:
            return re.sub(r"\D", "", str(value))
        return value

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            value = value.strip()
            value = self.sanitize_value(value)

            # subclass should implement the filter logic here

        return queryset


class DigitsOnlyFilter(MaskedInputFilter, StringSanitizingFilter):
    """
    Combines masked input with automatic digit-only sanitization.
    Perfect for fields like CPF, phone numbers, zip codes, etc.
    """

    def sanitize_value(self, value):
        """
        Remove all non-digit characters.
        """
        return self.only_digits(value)

    def field_query(self, value):
        """
        Override to return a Q object for filtering.
        """
        raise NotImplementedError(
            "Subclasses must implement field_query() method that returns a Q object"
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        value = value.strip()
        value = self.sanitize_value(value)

        # use the field query method to get a "q" object
        q_object = self.field_query(value)
        return queryset.filter(q_object)
