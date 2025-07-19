from rest_framework import generics
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from .tokens import email_verification_token

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class VerifyEmailView(generics.GenericAPIView):
    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        if not uidb64 or not token:
            return Response({"error": "Missing parameters."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid UID."}, status=400)

        if email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully."})
        return Response({"error": "Invalid or expired token."}, status=400)
