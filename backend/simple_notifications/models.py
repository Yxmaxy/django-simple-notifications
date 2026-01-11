from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PushSubscription(models.Model):
    """Model to store push notification subscriptions for clients"""

    user = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

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
