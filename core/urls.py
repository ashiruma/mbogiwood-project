# core/urls.py

from django.contrib import admin
from django.urls import path
from accounts.views import RegisterView, VerifyEmailView
from django.views.generic import TemplateView

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # API Endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/', VerifyEmailView.as_view(), name='verify-email'),

    # Website Pages
    path('', TemplateView.as_view(template_name="index.html"), name="home"),
    path('films/', TemplateView.as_view(template_name="films.html"), name="films"),
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('careers/', TemplateView.as_view(template_name="careers.html"), name="careers"),
    path('news/', TemplateView.as_view(template_name="news.html"), name="news"),
    path('news-article/', TemplateView.as_view(template_name="news-article.html"), name="news-article"),
    path('register/', TemplateView.as_view(template_name="register.html"), name="register-page"),
    path('login/', TemplateView.as_view(template_name="login.html"), name="login"),
    path('subscription/', TemplateView.as_view(template_name="subscription.html"), name="subscription"),
    path('account/', TemplateView.as_view(template_name="account.html"), name="account"),
]
