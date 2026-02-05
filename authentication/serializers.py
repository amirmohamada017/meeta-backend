from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import User
from .validators import (
    validate_phone_number,
    validate_otp_code,
    validate_first_name,
    validate_last_name,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        error_messages={
            "required": _("Phone number is required"),
            "blank": _("Phone number is required"),
            "min_length": _("Phone number must be exactly 11 digits"),
            "max_length": _("Phone number must be exactly 11 digits"),
        },
    )

    def validate_phone_number(self, value):
        return validate_phone_number(value)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        error_messages={
            "required": _("Phone number is required"),
            "blank": _("Phone number is required"),
            "min_length": _("Phone number must be exactly 11 digits"),
            "max_length": _("Phone number must be exactly 11 digits"),
        },
    )
    otp_code = serializers.CharField(
        max_length=4,
        min_length=4,
        error_messages={
            "required": _("OTP code is required"),
            "blank": _("OTP code is required"),
            "min_length": _("OTP code must be exactly 4 digits"),
            "max_length": _("OTP code must be exactly 4 digits"),
        },
    )

    def validate_phone_number(self, value):
        return validate_phone_number(value)

    def validate_otp_code(self, value):
        return validate_otp_code(value)


class CompleteSignupSerializer(serializers.Serializer):
    signup_token = serializers.CharField(
        error_messages={
            "required": _("Signup token is required"),
            "blank": _("Signup token is required"),
        },
    )
    first_name = serializers.CharField(
        max_length=150,
        error_messages={
            "required": _("First name cannot be empty"),
            "blank": _("First name cannot be empty"),
        },
    )
    last_name = serializers.CharField(
        max_length=150,
        error_messages={
            "required": _("Last name cannot be empty"),
            "blank": _("Last name cannot be empty"),
        },
    )

    def validate_first_name(self, value):
        return validate_first_name(value)

    def validate_last_name(self, value):
        return validate_last_name(value)
