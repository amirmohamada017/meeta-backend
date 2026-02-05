import secrets
import string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from .validators import validate_phone_number


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, first_name='', last_name='', **extra_fields):
        if not phone_number:
            raise ValueError(_("Phone number is required"))

        validate_phone_number(phone_number)

        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def clean(self):
        super().clean()
        validate_phone_number(self.phone_number)


class OTP(models.Model):
    phone_number = models.CharField(
        max_length=11,
        primary_key=True,
    )
    otp_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otps'
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")

    def __str__(self):
        return f"{self.phone_number} - {self.otp_code}"

    def is_valid(self):
        return timezone.now() < self.expires_at

    def can_request_new_otp(self):
        from django.conf import settings
        time_elapsed = timezone.now() - self.created_at
        required_wait = timezone.timedelta(minutes=settings.OTP_RATE_LIMIT_MINUTES)
        return time_elapsed >= required_wait

    def time_until_next_request(self):
        from django.conf import settings
        time_elapsed = timezone.now() - self.created_at
        required_wait = timezone.timedelta(minutes=settings.OTP_RATE_LIMIT_MINUTES)
        remaining = required_wait - time_elapsed

        if remaining.total_seconds() <= 0:
            return 0

        return int(remaining.total_seconds())

    def clean(self):
        super().clean()
        validate_phone_number(self.phone_number)

    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(9000) + 1000)
