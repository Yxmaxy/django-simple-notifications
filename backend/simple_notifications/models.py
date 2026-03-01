from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationPreferences(models.Model):
    """Notification preferences for a specific object - User or PushSubscription"""

    object = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    notification_frequency = models.IntegerField(default=100)  # 0-100
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_timezone = models.CharField(max_length=50, default="UTC")

    class Meta:
        unique_together = [("content_type", "object_id")]

    def __str__(self):
        return f"Notification preferences for {self.object}"

    def to_dict(self):
        return {
            "notification_frequency": self.notification_frequency,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "quiet_hours_timezone": self.quiet_hours_timezone,
        }


class PushSubscription(models.Model):
    """Model to store push notification subscriptions for clients"""

    user = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)

    name = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Push subscription for {self.user} ({self.name or self.endpoint[:40]})"

    def to_dict(self):
        """Convert subscription to dictionary format for web push"""
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }
    
    @staticmethod
    def preferences_cache_key(subscription_pk: int) -> str:
        return f"simple_notifications_prefs_{subscription_pk}"

    def get_subscription_preferences(self):
        """Get the notification preferences for the user and the subscription"""
        key = self.preferences_cache_key(self.pk)
        cached = cache.get(key)
        if cached is not None:
            return cached
        
        from simple_notifications.services import NotificationService
        user_preferences = NotificationService.get_or_create_user_preferences(self.user)
        subscription_preferences = NotificationService.get_or_create_user_preferences(self.user, self.pk)

        result = {
            **user_preferences.to_dict(),
            **subscription_preferences.to_dict(),
        }
        cache.set(key, result, timeout=None)
        return result


@receiver([post_save, post_delete], sender=NotificationPreferences)
def bust_subscription_preferences_cache(sender, instance: NotificationPreferences, **kwargs):
    """Clear cached preferences when a NotificationPreferences record changes."""
    push_ct = ContentType.objects.get_for_model(PushSubscription)
    if instance.content_type_id == push_ct.id:
        cache.delete(PushSubscription.preferences_cache_key(instance.object_id))
    else:
        pks = PushSubscription.objects.filter(
            content_type_id=instance.content_type_id,
            object_id=instance.object_id,
        ).values_list("pk", flat=True)
        cache.delete_many([PushSubscription.preferences_cache_key(pk) for pk in pks])
