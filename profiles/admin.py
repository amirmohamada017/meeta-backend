from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Profile, Interest


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'username',
        'is_host_badge',
        'profile_image_thumbnail',
        'created_at'
    ]
    list_filter = [
        'is_host',
        'created_at',
        'updated_at'
    ]
    search_fields = ['user__phone_number', 'username', 'bio']
    readonly_fields = [
        'created_at',
        'updated_at',
        'profile_image_preview'
    ]
    filter_horizontal = ['interests']
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'is_host')
        }),
        ('Profile Information', {
            'fields': ('username', 'bio', 'profile_picture', 'profile_image_preview')
        }),
        ('Interests', {
            'fields': ('interests',)
        }),
        ('Social Networks', {
            'fields': ('instagram_url', 'linkedin_url')
        }),
        ('Time Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_host_badge(self, obj):
        if obj.is_host:
            return mark_safe(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Host</span>'
            )
        return mark_safe(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">User</span>'
        )
    is_host_badge.short_description = 'Type'

    def profile_image_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return '-'
    profile_image_thumbnail.short_description = 'Image'

    def profile_image_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="200" style="border-radius: 10px;" />',
                obj.profile_picture.url
            )
        return 'No image uploaded'
    profile_image_preview.short_description = 'Image Preview'
