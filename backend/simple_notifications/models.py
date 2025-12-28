from django.db import models
from django.contrib.auth import get_user_model


class PushSubscription(models.Model):
    """Model to store push notification subscriptions for clients"""

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )
    app_name = models.CharField(max_length=255, default="default")

    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Push subscription for {self.user}"

    def to_dict(self):
        """Convert subscription to dictionary format for web push"""
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }
