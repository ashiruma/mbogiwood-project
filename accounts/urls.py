from django.contrib import admin
from django.urls import path
from accounts.views import RegisterView, VerifyEmailView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('films/', TemplateView.as_view(template_name="films.html"), name="films"),
]
