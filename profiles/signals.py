import logging
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import Profile


logger = logging.getLogger('profiles')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_signup(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        profile = Profile.objects.create(user=instance, is_host=False)

        logger.info(
            str(_('Profile created for new user')),
            extra={
                'user_id': instance.id,
                'phone_number': instance.phone_number[:6] + '*****',
                'profile_id': profile.id,
            },
        )

    except Exception as e:
        logger.exception(
            str(_('Profile creation failed during user signup')),
            extra={
                'user_id': instance.id,
                'phone_number': instance.phone_number[:6] + '*****',
                'error': str(e),
                'exception_type': type(e).__name__,
            },
        )


@receiver(pre_delete, sender=Profile)
def delete_profile_picture_on_profile_delete(sender, instance, **kwargs):
    if not instance.profile_picture:
        return

    try:
        instance.profile_picture.delete(save=False)

    except Exception as e:
        logger.warning(
            str(_('Failed to delete profile picture file during profile deletion')),
            extra={
                'profile_id': instance.id,
                'user_id': instance.user.id if instance.user else None,
                'error': str(e),
            },
        )
