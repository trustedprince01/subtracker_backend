from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Subscription

from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    last_login_location = serializers.SerializerMethodField()
    plan_type = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name', 
            'creation_date', 'last_login', 'last_login_location', 
            'plan_type', 'payment_method', 'profile_image'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_creation_date(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S') if obj.date_joined else None

    def get_last_login(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S') if obj.last_login else None

    def get_last_login_location(self, obj):
        # Placeholder for future implementation of login tracking
        return 'Unknown'

    def get_plan_type(self, obj):
        # Retrieve from subscription or default
        try:
            subscription = obj.subscription_set.first()
            return subscription.name if subscription else 'Free'
        except:
            return 'Free'

    def get_payment_method(self, obj):
        # Placeholder for future payment method tracking
        return 'Not set'

    def get_profile_image(self, obj):
        # Retrieve profile image from associated profile
        try:
            return obj.profile.avatar if hasattr(obj, 'profile') and obj.profile.avatar else None
        except:
            return None

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user
        name = data.get('name')
        # For create
        if self.instance is None:
            if Subscription.objects.filter(user=user, name=name).exists():
                raise serializers.ValidationError({'name': f"You already have a subscription named '{name}'."})
        # For update
        else:
            if Subscription.objects.filter(user=user, name=name).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({'name': f"You already have a subscription named '{name}'."})
        return data
