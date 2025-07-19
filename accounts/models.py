# accounts/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
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

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_creator = models.BooleanField(default=False)

    CREATOR_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    creator_status = models.CharField(max_length=10, choices=CREATOR_STATUS_CHOICES, null=True, blank=True)
    creator_approved_at = models.DateTimeField(null=True, blank=True)
    creator_rejected_at = models.DateTimeField(null=True, blank=True)
    creator_reapplication_allowed_from = models.DateTimeField(null=True, blank=True)

    ROLE_CHOICES = (
        ('subscriber', 'Subscriber'),
        ('filmmaker', 'Filmmaker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='subscriber')

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def can_reapply_as_creator(self):
        if self.creator_status != 'rejected' or not self.creator_reapplication_allowed_from:
            return False
        return timezone.now() >= self.creator_reapplication_allowed_from

    def is_subscriber(self):
        return self.role == 'subscriber'

    def is_filmmaker(self):
        return self.role == 'filmmaker'

class CreatorReviewLog(models.Model):
    class Action(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    subject_user = models.ForeignKey(CustomUser, related_name="review_logs", on_delete=models.CASCADE)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews_performed", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user.email} {self.action} {self.subject_user.email} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_token")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    def __str__(self):
        return f"Token for {self.user.email}"

# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(email, token):
    verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}/"
    subject = "Verify your email"
    message = f"Click the link to verify your account: {verification_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, EmailVerificationToken
from .utils import send_verification_email

@receiver(post_save, sender=CustomUser)
def handle_user_creation(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:
        token, _ = EmailVerificationToken.objects.get_or_create(user=instance)
        send_verification_email(instance.email, token.token)

# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmailVerificationToken
from django.utils import timezone

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            record = EmailVerificationToken.objects.get(token=token)

            if record.is_expired():
                return Response({'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)

            user = record.user
            user.is_active = True
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
            user.save()

            record.delete()

            return Response({'message': 'Email verified successfully.'})
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_404_NOT_FOUND)

# accounts/urls.py
from django.urls import path
from .views import VerifyEmailView

urlpatterns = [
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
]

# settings.py additions
FRONTEND_URL = "http://localhost:3000"  # Adjust as needed
DEFAULT_FROM_EMAIL = "no-reply@yourdomain.com"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # For testing
