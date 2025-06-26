# users/admin.py

from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, CreatorReviewLog

@admin.action(description="Approve selected creator applications")
def approve_creators(modeladmin, request, queryset):
    users_to_approve = queryset.filter(is_creator=True, creator_status='pending')
    count = users_to_approve.count()
    for user in users_to_approve:
        user.creator_status = 'approved'
        user.creator_approved_at = timezone.now()
        user.creator_rejected_at = None
        user.creator_reapplication_allowed_from = None
        user.save(update_fields=['creator_status', 'creator_approved_at', 'creator_rejected_at', 'creator_reapplication_allowed_from'])
        CreatorReviewLog.objects.create(subject_user=user, admin_user=request.user, action=CreatorReviewLog.Action.APPROVED)
    modeladmin.message_user(request, f"{count} creator(s) have been approved.")

@admin.action(description="Reject selected creator applications")
def reject_creators(modeladmin, request, queryset):
    users_to_reject = queryset.filter(is_creator=True, creator_status='pending')
    count = users_to_reject.count()
    for user in users_to_reject:
        user.creator_status = 'rejected'
        user.creator_rejected_at = timezone.now()
        user.creator_reapplication_allowed_from = timezone.now() + timedelta(days=30)
        user.save(update_fields=['creator_status', 'creator_rejected_at', 'creator_reapplication_allowed_from'])
        CreatorReviewLog.objects.create(subject_user=user, admin_user=request.user, action=CreatorReviewLog.Action.REJECTED, notes="Application did not meet platform guidelines.")
    modeladmin.message_user(request, f"{count} creator(s) have been rejected.")

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_creator', 'creator_status', 'is_active', 'is_email_verified', 'date_joined')
    list_filter = ('is_creator', 'creator_status', 'is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('-date_joined',)
    actions = [approve_creators, reject_creators]
    readonly_fields = ('last_login', 'date_joined', 'email_verified_at', 'creator_approved_at', 'creator_rejected_at', 'creator_reapplication_allowed_from')
    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Creator Status', {'fields': ('is_creator', 'creator_status', 'creator_approved_at', 'creator_rejected_at', 'creator_reapplication_allowed_from')}),
        ('Verification', {'fields': ('is_email_verified', 'email_verified_at')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(CreatorReviewLog)
class CreatorReviewLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'subject_user', 'action', 'admin_user')
    list_filter = ('action',)
    search_fields = ('subject_user__email', 'admin_user__email')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'subject_user', 'action', 'admin_user', 'notes')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
