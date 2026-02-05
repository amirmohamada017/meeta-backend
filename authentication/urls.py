from django.urls import path
from .views import RequestOTPView, VerifyOTPView, CompleteSignupView, RefreshTokenView, LogoutView

urlpatterns = [
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('complete-signup/', CompleteSignupView.as_view(), name='complete-signup'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
