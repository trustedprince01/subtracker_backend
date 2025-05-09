from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = CloudinaryField('avatar', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cycle = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    next_billing_date = models.DateField()
    category = models.CharField(max_length=50)
    logo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        unique_together = ('user', 'name')

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('subscription_added', 'Subscription Added'),
        ('subscription_removed', 'Subscription Removed'),
        ('profile_updated', 'Profile Updated'),
        ('login', 'User Login'),
        ('password_changed', 'Password Changed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.type} at {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User Activities'
