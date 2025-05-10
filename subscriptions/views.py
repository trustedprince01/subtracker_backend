from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import UserSerializer, SubscriptionSerializer, UserActivitySerializer
from .models import Subscription, UserActivity, Profile
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserActivity
from django.contrib.auth import get_user_model
import cloudinary.uploader

def create_user_activity(user, activity_type, description, metadata=None):
    try:
        UserActivity.objects.create(
            user=user,
            type=activity_type,
            description=description,
            metadata=metadata or {}
        )
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Failed to create user activity: {e}")

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionListCreateView(ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubscriptionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        create_user_activity(
            user=self.request.user,
            activity_type='subscription_removed',
            description=f'Removed subscription: {instance.name}',
            metadata={'subscription_id': instance.id}
        )
        instance.delete()

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        subscription = serializer.save(user=self.request.user)
        create_user_activity(
            user=self.request.user,
            activity_type='subscription_added',
            description=f'Added subscription: {subscription.name}',
            metadata={'subscription_id': subscription.id}
        )
        return subscription

    def perform_destroy(self, instance):
        create_user_activity(
            user=self.request.user,
            activity_type='subscription_removed',
            description=f'Removed subscription: {instance.name}',
            metadata={'subscription_id': instance.id}
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'cancelled'
        subscription.save()
        create_user_activity(
            user=self.request.user,
            activity_type='subscription_cancelled',
            description=f'Cancelled subscription: {subscription.name}',
            metadata={'subscription_id': subscription.id}
        )
        return Response({'status': 'subscription cancelled'})

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-timestamp')[:50]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserProfileView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)

    def retrieve(self, request):
        user = request.user
        # Ensure profile exists
        Profile.objects.get_or_create(user=user)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.first_name + ' ' + user.last_name,
            'avatar': user.profile.avatar.url if user.profile.avatar else None,
            'date_joined': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else None,
        }
        return Response(data)

    def partial_update(self, request):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        try:
            # Update user fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'username' in request.data:
                user.username = request.data['username']
            
            # Handle avatar upload to Cloudinary
            if 'avatar' in request.FILES:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    request.FILES['avatar'],
                    folder="profile_avatars",
                    resource_type="image"
                )
                # Update profile with Cloudinary URL
                profile.avatar = result['secure_url']
            
            user.save()
            profile.save()
            
            # Return updated user data
            return self.retrieve(request)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )