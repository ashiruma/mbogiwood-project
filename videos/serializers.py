# videos/serializers.py

from rest_framework import serializers
from .models import Video

class VideoListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for the film list/grid view.
    It only includes the essential fields needed for display, making the API fast.
    """
    # To add a 'slug' field, you would typically define it on your model.
    # For now, we'll derive it or omit it for simplicity.
    
    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'file_url', # In this context, we'll assume this points to the poster
            'status',   # Useful for the frontend to know if it's 'approved'
            # 'genre',  # You would add genre and year fields to your Video model
            # 'year',
        ]

class VideoDetailSerializer(serializers.ModelSerializer):
    """
    A more detailed serializer for the single film detail page.
    """
    class Meta:
        model = Video
        fields = '__all__' # Includes all fields from the Video model
