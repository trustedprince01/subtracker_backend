from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow authentication with email instead of username
        username = attrs.get('username', '')
        
        # Check if the input is an email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                self.fail('no_active_account')
        
        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Update last_login for the user
        username = request.data.get('username', '')
        if '@' in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return response
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return response
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return response
