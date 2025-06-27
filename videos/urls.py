from django.urls import path
from .views import (
    RequestUploadURLView, 
    FinalizeUploadView, 
    RetryUploadURLView, 
    FilmListView
)

app_name = 'videos'

urlpatterns = [
    # Public endpoint for listing all approved films
    # e.g., /api/v1/videos/
    path('', FilmListView.as_view(), name='film-list'),

    # Creator-only endpoints for the upload process
    path('request-upload/', RequestUploadURLView.as_view(), name='request-upload-url'),
    path('finalize-upload/', FinalizeUploadView.as_view(), name='finalize-upload'),
    path('retry-upload/', RetryUploadURLView.as_view(), name='retry-upload-url'),
]
