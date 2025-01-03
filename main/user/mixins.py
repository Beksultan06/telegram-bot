from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from normilize_phone_number import normalize_phone_number
from utils import validate_kyrgyz_phone_number


class PhoneNumberValidateMixin:

    def validate_new_phone_number(self, value):
        value = normalize_phone_number(value)
        if not validate_kyrgyz_phone_number(value):
            raise serializers.ValidationError(
                _("Неверный формат номера телефона")
            )
        return value

    def validate_phone_number(self, value):
        value = normalize_phone_number(value)
        if not validate_kyrgyz_phone_number(value):
            raise serializers.ValidationError(
                _("Неверный формат номера телефона")
            )
        return value
