from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileRetrieveUpdateView,
    ProfileImageView,
    PublicProfileView,
    ProfileViewSet,
)

app_name = 'profiles'

router = DefaultRouter()
router.register(r'users', ProfileViewSet, basename='users')

urlpatterns = [
    path('me/', ProfileRetrieveUpdateView.as_view(), name='profile-me'),
    path('me/image/', ProfileImageView.as_view(), name='profile-image'),
    path('<str:username>/', PublicProfileView.as_view(), name='public-profile'),
    path('', include(router.urls)),
]
