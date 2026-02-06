import uuid
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from .validators import validate_username, validate_instagram_url, validate_linkedin_url
from .querysets import ProfileQuerySet


def user_profile_image_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f'profiles/{instance.user.id}/profile_{timestamp}_{unique_id}.{ext}'


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='interest_name_idx'),
        ]


class Profile(models.Model):
    MAX_INTERESTS = 10

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    is_host = models.BooleanField(default=False)
    username = models.CharField(max_length=32, blank=True, null=True, validators=[validate_username])
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True)
    instagram_url = models.URLField(max_length=200, blank=True, validators=[validate_instagram_url])
    linkedin_url = models.URLField(max_length=200, blank=True, validators=[validate_linkedin_url])
    interests = models.ManyToManyField(Interest, related_name='profiles', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileQuerySet.as_manager()

    def clean(self):
        if self.username:
            if Profile.objects.exclude(pk=self.pk).filter(username__iexact=self.username).exists():
                raise ValidationError({'username': _("This username is already taken.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user}"

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('username'),
                name='unique_username_ci',
                condition=Q(username__isnull=False))
        ]
        indexes = [
            models.Index(fields=['username'], name='profile_username_idx'),
            models.Index(fields=['-created_at'], name='profile_created_at_idx'),
        ]
