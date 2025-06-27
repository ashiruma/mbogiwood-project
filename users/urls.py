from django.urls import path
from .views import SignupView, VerifyEmailView, LoginView, LogoutView

app_name = 'users'

urlpatterns = [
    # e.g., /api/v1/users/signup/
    path('signup/', SignupView.as_view(), name='signup'),

    # e.g., /api/v1/users/verify-email/
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),

    # Authentication Endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
