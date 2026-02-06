import re
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Profile
from .utils import ImageUploadUtility


User = get_user_model()


class ProfileImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture']

    def validate_profile_picture(self, value):
        if not value:
            return value

        try:
            ImageUploadUtility.validate_image(value)
            return ImageUploadUtility.process_image(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'username',
            'bio',
            'profile_picture',
            'profile_picture_url',
            'instagram_url',
            'linkedin_url',
            'is_host',
        ]
        read_only_fields = ['id', 'is_host']
        extra_kwargs = {
            'profile_picture': {'write_only': True},
        }

    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None

        request = self.context.get('request')
        return (
            request.build_absolute_uri(obj.profile_picture.url)
            if request
            else obj.profile_picture.url
        )

    def validate_username(self, value):
        return value.lower() if value else value


class ProfileDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'user_id',
            'phone_number',
            'username',
            'bio',
            'profile_picture_url',
            'instagram_url',
            'linkedin_url',
            'is_host',
        ]
        read_only_fields = fields

    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None

        request = self.context.get('request')
        return (
            request.build_absolute_uri(obj.profile_picture.url)
            if request
            else obj.profile_picture.url
        )


class PublicProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'username',
            'bio',
            'profile_picture_url',
            'instagram_url',
            'linkedin_url',
            'is_host',
        ]
        read_only_fields = fields

    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None

        request = self.context.get('request')
        return (
            request.build_absolute_uri(obj.profile_picture.url)
            if request
            else obj.profile_picture.url
        )
