import logging
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, CompleteSignupSerializer
from .services import OTPService, SignupTokenService
from .validators import mask_phone_number

logger = logging.getLogger('authentication')


class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        result = OTPService.send_otp(phone_number)

        if not result['success']:
            error_type = result.get('error_type', 'unknown_error')

            status_code_map = {
                'rate_limit_error': status.HTTP_429_TOO_MANY_REQUESTS,
                'validation_error': status.HTTP_400_BAD_REQUEST,
                'provider_error': status.HTTP_503_SERVICE_UNAVAILABLE,
                'timeout_error': status.HTTP_504_GATEWAY_TIMEOUT,
                'connection_error': status.HTTP_503_SERVICE_UNAVAILABLE,
                'configuration_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'unknown_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }

            status_code = status_code_map.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)

            response_data = {
                "message": result.get(
                    'error',
                    _("Failed to send OTP. Please try again later")
                )
            }
            response = Response(response_data, status=status_code)

            if error_type == 'rate_limit_error' and 'retry_after' in result:
                response['Retry-After'] = str(result['retry_after'])

            return response

        return Response(
            {"message": _("OTP sent successfully")},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        if not OTPService.verify_otp(phone_number, otp_code):
            logger.warning(
                _("OTP verification failed"),
                extra={'phone_number': mask_phone_number(phone_number)}
            )
            return Response(
                {"error": _("Invalid or Expired OTP code")},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            _("OTP verified successfully"),
            extra={'phone_number': mask_phone_number(phone_number)}
        )

        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            refresh = RefreshToken.for_user(user)

            response = Response(
                {"access": str(refresh.access_token)},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=int(
                    settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
                )
            )

            return response

        signup_token = SignupTokenService.create_signup_token(phone_number)

        return Response(
            {"signup_token": signup_token},
            status=status.HTTP_200_OK
        )


class CompleteSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompleteSignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        signup_token = serializer.validated_data['signup_token']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']

        phone_number = SignupTokenService.verify_and_use_token(signup_token)

        if not phone_number:
            return Response(
                {"error": _("Invalid or expired signup token")},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": _("User with this phone number already exists")},
                status=status.HTTP_409_CONFLICT
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    phone_number=phone_number,
                    first_name=first_name,
                    last_name=last_name
                )

                refresh = RefreshToken.for_user(user)

                response = Response(
                    {"access": str(refresh.access_token)},
                    status=status.HTTP_201_CREATED
                )

                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    max_age=int(
                        settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
                    )
                )

                return response

        except Exception as e:
            logger.exception(
                _("User signup failed"),
                extra={
                    'phone_number': mask_phone_number(phone_number),
                    'error': str(e),
                    'ip': request.META.get('REMOTE_ADDR')
                }
            )
            return Response(
                {"error": _("Failed to create user account")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": _("Refresh token not found")},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            refresh.set_jti()
            refresh.set_exp()
            access_token = str(refresh.access_token)

            response = Response(
                {"access": access_token},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=int(
                    settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
                )
            )

            return response

        except TokenError:
            response = Response(
                {"error": _("Invalid or Expired authentication token")},
                status=status.HTTP_401_UNAUTHORIZED
            )
            response.delete_cookie('refresh_token')
            return response

        except Exception as e:
            logger.exception(
                _("Token refresh failed"),
                extra={
                    'reason': 'unexpected_error',
                    'error': str(e),
                    'ip': request.META.get('REMOTE_ADDR')
                }
            )
            response = Response(
                {"error": _("Invalid or Expired authentication token")},
                status=status.HTTP_401_UNAUTHORIZED
            )
            response.delete_cookie('refresh_token')
            return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

        except TokenError:
            pass
        except Exception as e:
            logger.warning(
                _("Logout attempted but blacklist failed"),
                extra={
                    'user_id': request.user.id if request.user.is_authenticated else None,
                    'error': str(e),
                    'ip': request.META.get('REMOTE_ADDR')
                }
            )

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('refresh_token')
        return response
