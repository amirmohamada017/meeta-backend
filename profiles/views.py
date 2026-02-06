from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import UserRateThrottle
from .models import Profile
from .serializers import (
    ProfileSerializer,
    ProfileDetailSerializer,
    ProfileImageUploadSerializer,
    PublicProfileSerializer,
)


User = get_user_model()


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self):
        profile, created = Profile.objects.with_full_details().get_or_create(
            user=self.request.user,
            defaults={'user': self.request.user}
        )
        return profile

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileDetailSerializer
        return ProfileSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProfileImageUploadThrottle(UserRateThrottle):
    rate = '10/hour'


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ProfileImageUploadThrottle]

    def get_object(self):
        profile, created = Profile.objects.with_basic_details().get_or_create(
            user=self.request.user,
            defaults={'user': self.request.user}
        )
        return profile

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.profile_picture:
            try:
                old_picture = instance.profile_picture
                instance.profile_picture = None
                instance.save(update_fields=['profile_picture'])
                old_picture.delete(save=False)
            except Exception as e:
                pass
        
        serializer = ProfileImageUploadSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
        except IntegrityError:
            raise drf_serializers.ValidationError({'username': _('This username is already taken.')})

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.profile_picture:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        instance.profile_picture.delete(save=False)
        instance.profile_picture = None
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = PublicProfileSerializer
    permission_classes = []
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        return Profile.objects.filter(username__isnull=False).exclude(username='').with_public_details()

    def get_object(self):
        username = self.kwargs.get('username', '').lower()
        return get_object_or_404(self.get_queryset(), username__iexact=username)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.with_full_details()
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options']
