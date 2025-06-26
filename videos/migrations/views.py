# File: videos/views.py

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Video
import uuid

class RequestUploadURLView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if not user.is_creator or user.creator_status != 'approved':
            return Response({"detail": "Only approved creators can upload."}, status=status.HTTP_403_FORBIDDEN)
        video = Video.objects.create(uploaded_by=user, status='uploading')
        object_name = f"videos/{user.id}/{video.id}.mp4"
        final_file_url = f"[https://cdn.yourplatform.com/](https://cdn.yourplatform.com/){object_name}"
        # In a real app, use boto3 to generate a pre-signed URL here
        upload_url = f"[https://placeholder-bucket.s3.amazonaws.com/](https://placeholder-bucket.s3.amazonaws.com/){object_name}"
        video.file_url = final_file_url
        video.save()
        return Response({"upload_url": upload_url, "video_id": str(video.id)})

class FinalizeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        video_id = request.data.get("video_id")
        title = request.data.get("title")
        description = request.data.get("description", "")
        if not video_id or not title:
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            video = Video.objects.get(id=video_id, uploaded_by=request.user)
        except Video.DoesNotExist:
            return Response({"detail": "Invalid video ID."}, status=status.HTTP_404_NOT_FOUND)
        if video.status != 'uploading':
            return Response({"detail": "Upload already finalized."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = requests.head(video.file_url, timeout=5)
            if response.status_code != 200 or int(response.headers.get("Content-Length", 0)) == 0:
                video.delete()
                return Response({"detail": "File not found. Please retry upload."}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException:
            return Response({"detail": "Could not verify file with storage provider."}, status=status.HTTP_502_BAD_GATEWAY)
        video.title = title
        video.description = description
        video.status = 'uploaded'
        video.save()
        return Response({"detail": "Upload finalized.", "video_id": str(video.id)}, status=status.HTTP_200_OK)

class RetryUploadURLView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        video_id = request.data.get("video_id")
        if not video_id:
            return Response({"detail": "Missing video_id."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            video = Video.objects.get(id=video_id, uploaded_by=request.user, status__in=['uploading', 'processing_failed'])
        except Video.DoesNotExist:
            return Response({"detail": "Retry not allowed for this video."}, status=status.HTTP_404_NOT_FOUND)
        object_name = f"videos/{request.user.id}/{video.id}.mp4"
        upload_url = f"[https://placeholder-bucket.s3.amazonaws.com/](https://placeholder-bucket.s3.amazonaws.com/){object_name}"
        return Response({"upload_url": upload_url, "video_id": str(video.id)})
```python
# File: videos/urls.py

from django.urls import path
from .views import RequestUploadURLView, FinalizeUploadView, RetryUploadURLView

urlpatterns = [
    path('request-upload/', RequestUploadURLView.as_view(), name='request-upload-url'),
    path('finalize-upload/', FinalizeUploadView.as_view(), name='finalize-upload'),
    path('retry-upload/', RetryUploadURLView.as_view(), name='retry-upload-url'),
]

