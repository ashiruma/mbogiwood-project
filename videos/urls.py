# videos/urls.py

from django.urls import path
from .views import RequestUploadURLView, FinalizeUploadView, RetryUploadURLView

app_name = 'videos'

urlpatterns = [
    path('request-upload/', RequestUploadURLView.as_view(), name='request-upload-url'),
    path('finalize-upload/', FinalizeUploadView.as_view(), name='finalize-upload'),
    path('retry-upload/', RetryUploadURLView.as_view(), name='retry-upload-url'),
]
