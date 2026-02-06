import re
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Profile, Interest
from .utils import ImageUploadUtility


User = get_user_model()


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


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
    interests = InterestSerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        write_only=True,
        required=False,
        source='interests'
    )

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
            'interests',
            'interest_ids',
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

    def validate_interest_ids(self, value):
        if len(value) > Profile.MAX_INTERESTS:
            raise serializers.ValidationError(
                _(f'You cannot add more than {Profile.MAX_INTERESTS} interests.')
            )
        return value

    def update(self, instance, validated_data):
        interests = validated_data.pop('interests', None)
        instance = super().update(instance, validated_data)
        
        if interests is not None:
            instance.interests.set(interests)
        
        return instance


class ProfileDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    interests = InterestSerializer(many=True, read_only=True)

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
            'interests',
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
    interests = InterestSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username',
            'bio',
            'profile_picture_url',
            'instagram_url',
            'linkedin_url',
            'is_host',
            'interests',
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


class ProfileInterestSerializer(serializers.Serializer):
    interest_ids = serializers.ListField(
        child=serializers.IntegerField(),
        max_length=Profile.MAX_INTERESTS
    )

    def validate_interest_ids(self, value):
        if len(value) > Profile.MAX_INTERESTS:
            raise serializers.ValidationError(
                _(f'You cannot add more than {Profile.MAX_INTERESTS} interests.')
            )
        
        existing_interests = Interest.objects.filter(id__in=value)
        if len(existing_interests) != len(value):
            raise serializers.ValidationError(_('Some interests do not exist.'))
        
        return value
