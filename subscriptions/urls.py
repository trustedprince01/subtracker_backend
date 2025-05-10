from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RegisterView, SubscriptionListCreateView, SubscriptionDetailView, 
    SubscriptionViewSet, UserProfileView, UserActivityViewSet)
from .user_views import UserProfileAvatarUploadView, UserProfileUpdateView
from rest_framework_simplejwt.views import TokenRefreshView
from .custom_auth import CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'user/profile', UserProfileView, basename='user-profile')
router.register(r'user/activities', UserActivityViewSet, basename='user-activities')

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/upload-avatar/', UserProfileAvatarUploadView.as_view(), name='user-avatar-upload'),
    path('user/profile/<int:pk>/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('user/profile/', UserProfileView.as_view({'get': 'me'}), name='user-profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscriptions'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/', include('dj_rest_auth.registration.urls')),
    path('', include(router.urls)),
]