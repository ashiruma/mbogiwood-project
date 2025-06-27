# users/serializers.py

from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model, used to safely expose
    user data in API responses.
    """
    class Meta:
        model = CustomUser
        # Define the fields to include in the API response
        fields = [
            'id', 
            'email', 
            'name', # Changed from 'full_name' to match your model
            'is_creator', 
            'creator_status'
            # We will add 'is_subscribed' and 'profile_picture_url' later
            # when those features are built.
        ]
