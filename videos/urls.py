from django.urls import path
from .views import RequestUploadURLView, FinalizeUploadView, RetryUploadURLView, FilmListView

app_name = 'videos'

urlpatterns = [
    # New public endpoint for listing films
    path('', FilmListView.as_view(), name='film-list'),

    # Existing creator-only endpoints
    path('request-upload/', RequestUploadURLView.as_view(), name='request-upload-url'),
    path('finalize-upload/', FinalizeUploadView.as_view(), name='finalize-upload'),
    path('retry-upload/', RetryUploadURLView.as_view(), name='retry-upload-url'),
]
