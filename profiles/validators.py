import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    if not value:
        return

    if len(value) < 3:
        raise ValidationError(
            _('Username must be at least 3 characters long.')
        )

    if len(value) > 32:
        raise ValidationError(
            _('Username cannot exceed 32 characters.')
        )

    if not re.match(r'^(?!-)(?!.*--)[A-Za-z][A-Za-z0-9-]{2,31}(?<!-)$', value):
        raise ValidationError(
            _(
                'Username can only contain letters, numbers, and hyphens. '
                'Must be 3-32 characters, start with a letter, no double hyphens, no trailing hyphen.'
            )
        )

    if value[0].isdigit():
        raise ValidationError(
            _('Username cannot start with a number.')
        )

    reserved_usernames = ['admin', 'api', 'www', 'mail', 'root', 'system']
    if value.lower() in reserved_usernames:
        raise ValidationError(
            _('This username is reserved and cannot be used.')
        )


def validate_social_media_url(value, platform='instagram'):
    if not value:
        return

    url_validator = URLValidator()
    url_validator(value)

    if platform == 'instagram':
        if 'instagram.com' not in value.lower():
            raise ValidationError(
                _('Please provide a valid Instagram URL.')
            )
    elif platform == 'linkedin':
        if 'linkedin.com' not in value.lower():
            raise ValidationError(
                _('Please provide a valid LinkedIn URL.')
            )


def validate_instagram_url(value):
    return validate_social_media_url(value, 'instagram')


def validate_linkedin_url(value):
    return validate_social_media_url(value, 'linkedin')
