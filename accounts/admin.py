# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, CreatorReviewLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'is_staff', 'is_active', 'is_creator', 'creator_status')
    list_filter = ('is_active', 'is_staff', 'is_creator', 'creator_status')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Creator Info'), {'fields': (
            'is_creator', 'creator_status', 'creator_approved_at', 
            'creator_rejected_at', 'creator_reapplication_allowed_from'
        )}),
        (_('Verification'), {'fields': ('is_email_verified', 'email_verified_at')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

@admin.register(CreatorReviewLog)
class CreatorReviewLogAdmin(admin.ModelAdmin):
    list_display = ('subject_user', 'admin_user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('subject_user__email', 'admin_user__email')
