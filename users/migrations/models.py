# users/models.py

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    """ Custom manager for our User model to handle user and superuser creation. """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
            
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """ The primary User model for the platform, replacing Django's default User. """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, help_text="User's full name.")
    is_active = models.BooleanField(default=False, help_text="Designates whether this user should be treated as active.")
    is_staff = models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.")
    date_joined = models.DateTimeField(default=timezone.now)
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_creator = models.BooleanField(default=False, help_text="Designates whether the user has applied to be a creator.")
    CREATOR_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    creator_status = models.CharField(max_length=10, choices=CREATOR_STATUS_CHOICES, null=True, blank=True)
    creator_approved_at = models.DateTimeField(null=True, blank=True)
    creator_rejected_at = models.DateTimeField(null=True, blank=True)
    creator_reapplication_allowed_from = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def can_reapply_as_creator(self):
        if self.creator_status != 'rejected' or not self.creator_reapplication_allowed_from:
            return False
        return timezone.now() >= self.creator_reapplication_allowed_from

class CreatorReviewLog(models.Model):
    """ Creates an immutable audit trail for creator approval/rejection actions. """
    class Action(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    subject_user = models.ForeignKey(CustomUser, related_name="review_logs", on_delete=models.CASCADE)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews_performed", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    notes = models.TextField(blank=True, null=True, help_text="Admin notes, e.g., reason for rejection.")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user.email} {self.action} {self.subject_user.email} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
