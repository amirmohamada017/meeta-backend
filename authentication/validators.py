import re
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


PHONE_NUMBER_REGEX = r"^09\d{9}$"
PHONE_NUMBER_LENGTH = 11
OTP_CODE_LENGTH = 4


def validate_phone_number(value):
    if not value or not isinstance(value, str):
        raise serializers.ValidationError(_("Phone number is required"))
    
    value = value.strip()
    
    if not re.match(PHONE_NUMBER_REGEX, value):
        raise serializers.ValidationError(_("Phone number must be 11 digits starting with 09"))
    
    return value


def validate_otp_code(value):
    if not isinstance(value, str):
        raise serializers.ValidationError(_("OTP code must be a string"))
    
    value = value.strip()
    
    if not value.isdigit():
        raise serializers.ValidationError(_("OTP code must contain only digits"))
    
    if len(value) != OTP_CODE_LENGTH:
        raise serializers.ValidationError(_(f"OTP code must be exactly {OTP_CODE_LENGTH} digits"))
    
    return value


def validate_first_name(value):
    if not isinstance(value, str):
        raise serializers.ValidationError(_("First name must be a string"))
    
    value = value.strip()
    
    if not value:
        raise serializers.ValidationError(_("First name cannot be empty"))
    
    if len(value) < 2:
        raise serializers.ValidationError(_("First name must be at least 2 characters long"))
    
    if len(value) > 150:
        raise serializers.ValidationError(_("First name cannot exceed 150 characters"))
    
    return value


def validate_last_name(value):
    if not isinstance(value, str):
        raise serializers.ValidationError(_("Last name must be a string"))
    
    value = value.strip()
    
    if not value:
        raise serializers.ValidationError(_("Last name cannot be empty"))
    
    if len(value) < 2:
        raise serializers.ValidationError(_("Last name must be at least 2 characters long"))
    
    if len(value) > 150:
        raise serializers.ValidationError(_("Last name cannot exceed 150 characters"))
    
    return value


def mask_phone_number(phone_number):
    if len(phone_number) != PHONE_NUMBER_LENGTH:
        return '***'
    return phone_number[:4] + '****' + phone_number[-3:]
