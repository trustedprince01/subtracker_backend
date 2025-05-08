from django.db import models
from django.contrib.auth.models import User

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
