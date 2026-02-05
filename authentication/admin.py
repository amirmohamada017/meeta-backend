from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import User, OTP


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ['phone_number', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    readonly_fields = ['last_login', 'date_joined']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'created_at', 'expires_at', 'validity_status', 'time_remaining']
    list_filter = ['created_at']
    search_fields = ['phone_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def validity_status(self, obj):
        if obj.is_valid():
            return mark_safe('<span style="color: green; font-weight: bold;">✓ Valid</span>')
        return mark_safe('<span style="color: red; font-weight: bold;">✗ Expired</span>')
    validity_status.short_description = 'Status'
    
    def time_remaining(self, obj):
        now = timezone.now()
        
        if now >= obj.expires_at:
            return mark_safe('<span style="color: gray;">Expired</span>')
        
        time_to_expiry = obj.expires_at - now
        minutes_to_expiry = int(time_to_expiry.total_seconds() / 60)
        seconds_to_expiry = int(time_to_expiry.total_seconds() % 60)
        
        if not obj.can_request_new_otp():
            seconds_until_request = obj.time_until_next_request()
            minutes_until = seconds_until_request // 60
            secs_until = seconds_until_request % 60
            return mark_safe(
                f'<span style="color: orange;">Rate limited: {minutes_until}m {secs_until}s</span><br>'
                f'<span style="color: blue;">Expires in: {minutes_to_expiry}m {seconds_to_expiry}s</span>'
            )
        
        return mark_safe(f'<span style="color: blue;">Expires in: {minutes_to_expiry}m {seconds_to_expiry}s</span>')
    time_remaining.short_description = 'Time Info'
