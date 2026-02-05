import logging
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
logger = logging.getLogger('authentication')


class SMSProvider:
    @staticmethod
    def _validate_settings():
        if not settings.SMSIR_API_KEY:
            logger.critical(
                _("SMS configuration error detected"),
                extra={'config_key': 'SMSIR_API_KEY', 'issue': 'not_configured'}
            )
            raise ImproperlyConfigured(_("SMSIR_API_KEY is not configured in settings"))

        if not settings.SMSIR_TEMPLATE_ID:
            logger.critical(
                _("SMS configuration error detected"),
                extra={'config_key': 'SMSIR_TEMPLATE_ID', 'issue': 'not_configured'}
            )
            raise ImproperlyConfigured(_("SMSIR_TEMPLATE_ID is not configured in settings"))

        try:
            int(settings.SMSIR_TEMPLATE_ID)
        except (ValueError, TypeError):
            logger.critical(
                _("SMS configuration error detected"),
                extra={'config_key': 'SMSIR_TEMPLATE_ID', 'issue': 'invalid_format'}
            )
            raise ImproperlyConfigured(_("SMSIR_TEMPLATE_ID must be a valid integer"))

        if not settings.SMSIR_BASE_URL:
            logger.critical(
                _("SMS configuration error detected"),
                extra={'config_key': 'SMSIR_BASE_URL', 'issue': 'not_configured'}
            )
            raise ImproperlyConfigured(_("SMSIR_BASE_URL is not configured in settings"))

    @staticmethod
    def send_otp(phone_number, otp_code):
        try:
            SMSProvider._validate_settings()
        except ImproperlyConfigured as e:
            logger.critical(
                _("SMS configuration error detected"),
                extra={'error': str(e)}
            )
            return {
                'success': False,
                'internal_error': str(e),
                'error_type': 'configuration_error'
            }

        url = f'{settings.SMSIR_BASE_URL}/send/verify'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-KEY': settings.SMSIR_API_KEY
        }

        payload = {
            "mobile": phone_number,
            "templateId": int(settings.SMSIR_TEMPLATE_ID),
            "parameters": [
                {"name": "CODE", "value": otp_code}
            ]
        }

        if settings.SMSIR_LINE_NUMBER:
            payload['lineNumber'] = settings.SMSIR_LINE_NUMBER

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=10
            )
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 1:
                return {
                    'success': True,
                    'message_id': response_data.get('data', {}).get('messageId')
                }

            provider_message = response_data.get('message', 'Unknown provider error')

            logger.error(
                _("SMS provider returned an error"),
                extra={
                    'phone_number': phone_number[:6] + '*****',
                    'status_code': response.status_code,
                    'provider_message': provider_message,
                    'response_data': response_data
                }
            )

            return {
                'success': False,
                'internal_error': _("SMS provider error: {error}").format(
                    error=provider_message
                ),
                'error_type': 'provider_error'
            }

        except requests.exceptions.Timeout:
            logger.error(
                _("SMS provider timeout occurred"),
                extra={'phone_number': phone_number[:6] + '*****', 'url': url}
            )
            return {
                'success': False,
                'internal_error': _("SMS service timeout"),
                'error_type': 'timeout_error'
            }

        except requests.exceptions.RequestException as e:
            logger.error(
                _("SMS provider connection error occurred"),
                extra={
                    'phone_number': phone_number[:6] + '*****',
                    'url': url,
                    'error': str(e)
                }
            )
            return {
                'success': False,
                'internal_error': _("SMS service connection error"),
                'error_type': 'connection_error'
            }

        except Exception as e:
            logger.exception(
                _("Unexpected error occurred during SMS send"),
                extra={
                    'phone_number': phone_number[:6] + '*****',
                    'error': str(e)
                }
            )
            return {
                'success': False,
                'internal_error': _("Unexpected SMS error: {error}").format(error=str(e)),
                'error_type': 'unknown_error'
            }
