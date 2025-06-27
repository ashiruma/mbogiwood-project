from django.contrib.auth import authenticate
from django.conf import settings
from django.core import signing
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# from ratelimit.decorators import ratelimit  # Uncomment after installing django-ratelimit

from .models import CustomUser
from .serializers import UserSerializer
# from .serializers import UserSignupSerializer  # If you have a signup serializer

# ------------- SIGNUP -------------
class SignupView(APIView):
    """
    Handles new user registration.
    In a real implementation, this would use a serializer for robust validation.
    """
    def post(self, request):
        # For a production app, use a serializer to validate this data.
        # e.g., serializer = UserSignupSerializer(data=request.data)
        # if serializer.is_valid():
        #    user = serializer.save()
        #    ... send email and return success ...
        
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        is_creator = request.data.get('is_creator', False)

        if not all([email, name, password]):
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"detail": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # This logic should ideally live inside a serializer's create() method
        creator_status = 'pending' if is_creator else None
        user = CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_creator=is_creator,
            creator_status=creator_status
        )

        # Generate a secure token for email verification
        token = signing.dumps(user.email, salt='email-verification')
        # This URL should point to your frontend page that will handle verification
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        # TODO: Dispatch an email sending task (e.g., via Celery)
        # send_mail(
        #     subject="Verify your Mbogiwood account",
        #     message=f"Welcome to Mbogiwood! Please click the link to verify your account: {verification_link}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        # )

        return Response(
            {"detail": "Verification email sent. Please check your inbox."},
            status=status.HTTP_201_CREATED
        )

# ------------- VERIFY EMAIL -------------
class VerifyEmailView(APIView):
    """
    Handles the verification link clicked by the user from their email.
    """
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Missing verification token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # max_age is in seconds (e.g., 48 hours)
            email = signing.loads(token, salt='email-verification', max_age=48*3600)
        except signing.SignatureExpired:
            # TODO: Redirect to a frontend page that allows resending the link
            return Response({"detail": "This verification link has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except signing.BadSignature:
            # TODO: Redirect to a frontend error page
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, email=email)
        
        if user.is_email_verified:
            # TODO: Redirect to login page with a "already verified" message
            return Response({"detail": "Your email has already been verified."}, status=status.HTTP_200_OK)

        user.is_email_verified = True
        user.is_active = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=['is_email_verified', 'is_active', 'email_verified_at'])
        
        # TODO: Redirect to a "Success! You can now log in" page on your frontend
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)

# ------------- LOGIN -------------
class LoginView(APIView):
    """
    Handles user login and returns JWT access and refresh tokens.
    """
    # In a real project, you would uncomment this decorator after installing django-ratelimit
    # @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(username=email, password=password)

        if user is not None:
            # Check if the user's account is active
            if not user.is_active:
                return Response({"detail": "Account not active. Please verify your email."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Serialize user data
            user_serializer = UserSerializer(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_serializer.data
            })
        
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

# ------------- LOGOUT -------------
class LogoutView(APIView):
    """
    Handles user logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
