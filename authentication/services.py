import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.exceptions import TokenError
from .models import OTP
from .validators import validate_phone_number, mask_phone_number
from .sms_provider import SMSProvider

logger = logging.getLogger('authentication')


class OTPService:
    @staticmethod
    def send_otp(phone_number):
        try:
            validate_phone_number(phone_number)
        except Exception:
            return {
                'success': False,
                'error': _("Phone number must be 11 digits starting with 09"),
                'error_type': 'validation_error'
            }

        try:
            otp_record = OTP.objects.get(phone_number=phone_number)

            if not otp_record.can_request_new_otp():
                seconds_remaining = otp_record.time_until_next_request()
                return {
                    'success': False,
                    'error': _("Too many OTP requests. Please try again later"),
                    'error_type': 'rate_limit_error',
                    'retry_after': seconds_remaining
                }

            otp_record.delete()

        except OTP.DoesNotExist:
            pass

        otp_code = OTP.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        sms_result = SMSProvider.send_otp(phone_number, otp_code)

        if not sms_result['success']:
            logger.error(
                _("OTP send failed"),
                extra={
                    'phone_number': mask_phone_number(phone_number),
                    'error_type': sms_result.get('error_type', 'unknown'),
                    'internal_error': sms_result.get('internal_error', 'Unknown error')
                }
            )
            return {
                'success': False,
                'error': _("Failed to send OTP. Please try again later"),
                'error_type': sms_result.get('error_type', 'provider_error')
            }

        otp_record = OTP.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )

        return {
            'success': True,
            'otp': otp_record
        }

    @staticmethod
    def verify_otp(phone_number, otp_code):
        try:
            validate_phone_number(phone_number)
        except Exception:
            return False

        if not otp_code.isdigit() or len(otp_code) != 4:
            return False

        try:
            otp_record = OTP.objects.get(phone_number=phone_number)

            if otp_record.otp_code == otp_code and otp_record.is_valid():
                otp_record.delete()
                return True

            return False

        except OTP.DoesNotExist:
            return False


class SignupToken(Token):
    token_type = 'signup'
    lifetime = timedelta(minutes=settings.SIGNUP_TOKEN_EXPIRY_MINUTES)


class SignupTokenService:
    @staticmethod
    def create_signup_token(phone_number):
        try:
            validate_phone_number(phone_number)
        except Exception as e:
            raise ValueError(_("Phone number must be 11 digits starting with 09"))

        token = SignupToken()
        token['phone_number'] = phone_number
        token['type'] = 'signup'

        return str(token)

    @staticmethod
    def verify_and_use_token(token):
        try:
            decoded_token = SignupToken(token)

            if decoded_token.get('type') != 'signup':
                return None

            phone_number = decoded_token.get('phone_number')

            if not phone_number:
                return None

            try:
                validate_phone_number(phone_number)
            except Exception:
                return None

            return phone_number

        except TokenError:
            return None
        except Exception as e:
            logger.error(
                _("Signup token validation failed"),
                extra={
                    'reason': 'unexpected_error',
                    'error': str(e)
                }
            )
            return None