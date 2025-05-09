from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import cloudinary.uploader
import os
from .models import Profile
from .serializers import UserSerializer

User = get_user_model()

class UserProfileAvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        avatar_file = request.FILES.get('avatar')

        if not avatar_file:
            return Response({'error': 'No avatar file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate Cloudinary configuration
            config = cloudinary.config()
            if not config.cloud_name or not config.api_key or not config.api_secret:
                return Response({
                    'error': 'Cloudinary configuration is missing',
                    'details': 'Cloud name, API key, or API secret is not set'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                avatar_file, 
                folder=f'subtracker/avatars/{user.username}',
                overwrite=True,
                unique_filename=True
            )

            # Ensure user has a profile
            profile, _ = Profile.objects.get_or_create(user=user)
            
            # Update user's avatar URL
            profile.avatar = upload_result['secure_url']
            profile.save()

            return Response({
                'avatar': upload_result['secure_url'],
                'message': 'Avatar uploaded successfully'
            }, status=status.HTTP_200_OK)

        except cloudinary.exceptions.Error as cloud_error:
            return Response({
                'error': 'Cloudinary upload failed',
                'details': str(cloud_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                'error': 'Failed to upload avatar',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        user = request.user
        
        try:
            # Validate input data
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            username = request.data.get('username', '').strip()

            if not first_name or not last_name or not username:
                return Response({
                    'error': 'Validation failed',
                    'details': 'First name, last name, and username are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.save()

            # Serialize and return updated user data
            serializer = UserSerializer(user)
            return Response(serializer.data)

        except Exception as e:
            print(f"Error updating profile: {e}")
            return Response({
                'error': 'Failed to update profile',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
