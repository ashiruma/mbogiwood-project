# accounts/utils.py

from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token

def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = f"{settings.FRONTEND_URL}/verify-email/?uid={uid}&token={token}"

    send_mail(
        subject="Verify your email",
        message=f"Click the link to verify your email: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
