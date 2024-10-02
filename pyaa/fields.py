from django import forms

from pyaa.helpers.string import StringHelper


class OnlyNumberCharField(forms.CharField):
    def clean(self, value):
        data = super().clean(value)
        data = StringHelper.only_numbers(data)
        return data
