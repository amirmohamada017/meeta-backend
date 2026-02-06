from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileRetrieveUpdateView,
    ProfileImageView,
    PublicProfileView,
    ProfileViewSet,
    InterestViewSet,
    ProfileInterestView,
)

app_name = 'profiles'

router = DefaultRouter()
router.register(r'users', ProfileViewSet, basename='users')
router.register(r'interests', InterestViewSet, basename='interests')

urlpatterns = [
    path('me/', ProfileRetrieveUpdateView.as_view(), name='profile-me'),
    path('me/image/', ProfileImageView.as_view(), name='profile-image'),
    path('me/interests/', ProfileInterestView.as_view(), name='profile-interests'),
    path('<str:username>/', PublicProfileView.as_view(), name='public-profile'),
    path('', include(router.urls)),
]
