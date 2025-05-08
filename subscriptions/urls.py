from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, SubscriptionListCreateView, SubscriptionDetailView, SubscriptionViewSet, UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'user/profile', UserProfileView, basename='user-profile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscriptions'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('', include(router.urls)),
]