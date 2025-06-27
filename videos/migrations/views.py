import requests
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Video

class RequestUploadURLView(APIView):
    """
    Creates a Video record and returns a pre-signed URL for a direct-to-cloud upload.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not (user.is_creator and user.creator_status == 'approved'):
            return Response({"detail": "Only approved creators can upload content."}, status=status.HTTP_403_FORBIDDEN)
        
        # Create the video record first to get a stable ID for the object name
        video = Video.objects.create(uploaded_by=user, status='uploading')
        
        object_name = f"videos/{user.id}/{video.id}.mp4"
        final_file_url = f"https://cdn.yourplatform.com/{object_name}"  # The URL for streaming later

        # --- Real-world Cloud Provider Logic ---
        # This is a placeholder. In production, you would use a library like boto3 for AWS S3.
        # Example using boto3:
        # s3_client = boto3.client('s3')
        # presigned_data = s3_client.generate_presigned_post(Bucket=settings.S3_BUCKET_NAME, Key=object_name, ExpiresIn=3600)
        # upload_url = presigned_data['url']
        # For now, we'll use a placeholder URL.
        upload_url = f"https://your-s3-bucket.s3.amazonaws.com/{object_name}"

        video.file_url = final_file_url
        video.save(update_fields=['file_url'])

        return Response({
            "upload_url": upload_url,  # The URL the client's browser will POST the file to
            "video_id": str(video.id),
        })

class FinalizeUploadView(APIView):
    """
    After the client successfully uploads to the cloud, it calls this endpoint
    to confirm the upload and update the video's status.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        video_id = request.data.get("video_id")
        title = request.data.get("title")
        description = request.data.get("description", "")

        if not video_id or not title:
            return Response({"detail": "Video ID and title are required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            video = Video.objects.get(id=video_id, uploaded_by=request.user)
        except Video.DoesNotExist:
            return Response({"detail": "Video not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)
        
        if video.status != 'uploading':
            return Response({"detail": "This upload has already been finalized or is in an invalid state."}, status=status.HTTP_400_BAD_REQUEST)
        
        # --- File Verification Step ---
        try:
            # Use a HEAD request to check if the file exists in cloud storage without downloading it.
            response = requests.head(video.file_url, timeout=5)
            if response.status_code != 200 or int(response.headers.get("Content-Length", 0)) == 0:
                # If verification fails, delete the record to allow a clean retry.
                video.delete()
                return Response({"detail": "File verification failed. The uploaded file could not be found. Please retry."}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException:
            return Response({"detail": "Could not contact the storage provider to verify the upload."}, status=status.HTTP_502_BAD_GATEWAY)
        
        video.title = title
        video.description = description
        video.status = 'uploaded'  # Ready for the next step in the pipeline
        video.save(update_fields=['title', 'description', 'status'])
        
        # TODO: Dispatch a Celery task to begin video processing (transcoding, thumbnails, etc.)
        # process_video.delay(video.id)

        return Response({"detail": "Upload finalized and is now queued for processing.", "video_id": str(video.id)}, status=status.HTTP_200_OK)

class RetryUploadURLView(APIView):
    """
    Allows a user to get a new pre-signed URL for an upload that previously failed.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        video_id = request.data.get("video_id")
        if not video_id:
            return Response({"detail": "Missing video_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Allow retry only if the upload was initiated or if processing failed.
            video = Video.objects.get(id=video_id, uploaded_by=request.user, status__in=['uploading', 'processing_failed'])
        except Video.DoesNotExist:
            return Response({"detail": "Retry not allowed for this video. It may already be processed or you may not have permission."}, status=status.HTTP_404_NOT_FOUND)

        object_name = f"videos/{request.user.id}/{video.id}.mp4"
        # Generate a NEW pre-signed URL for the same object
        # upload_url = generate_presigned_post(...)
        upload_url = f"https://your-s3-bucket.s3.amazonaws.com/{object_name}"  # Placeholder

        return Response({
            "upload_url": upload_url,
            "video_id": str(video.id)
        })
