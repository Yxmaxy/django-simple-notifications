import json
import logging
import random
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo

from pywebpush import webpush, WebPushException

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import QuerySet

from simple_notifications.models import PushSubscription, NotificationPreferences


logger = logging.getLogger(__name__)


class NotificationService:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @staticmethod
    def send_push_notification(
        subscription: PushSubscription,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
        silent: bool = False,
        icon: str = None,
        badge: str = None,
    ) -> bool:
        """Send a push notification to a specific subscription using pywebpush"""
        try:
            if (
                not settings.NOTIFICATIONS_VAPID_PRIVATE_KEY
                or not settings.NOTIFICATIONS_VAPID_PUBLIC_KEY
                or not settings.NOTIFICATIONS_VAPID_EMAIL
            ):
                raise ValueError("VAPID keys or email are not set")

            if not NotificationService._should_send_notification(subscription):
                logger.debug("Skipping notification due to subscription preferences")
                return False

            notification_payload = {
                "title": title,
                "body": body,
                "data": data or {},
                "silent": silent,
                "icon": icon,
                "badge": badge,
            }

            payload = json.dumps(notification_payload)

            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth,
                },
            }

            webpush(
                subscription_info,
                payload,
                vapid_private_key=settings.NOTIFICATIONS_VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": f"mailto:{settings.NOTIFICATIONS_VAPID_EMAIL}",
                },
            )
            return True

        except WebPushException as ex:
            if ex.response is not None and ex.response.status_code == 410:
                logger.info("Subscription expired (410 Gone), deleting: %s", subscription.pk)
                subscription.delete()
                return False
            logger.error("WebPushException: %s", ex)
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error sending push notification: %s", e)
            return False
    
    @staticmethod
    def _should_send_notification(subscription: PushSubscription) -> bool:
        """Returns True/False based on the subscription preferences"""
        preferences = subscription.get_subscription_preferences()

        # frequency
        preference_frequency = preferences.get("notification_frequency", 100)
        if preference_frequency != 100 and random.randint(0, 100) > preference_frequency:
            return False

        # quiet hours
        quiet_start = preferences.get("quiet_hours_start")
        quiet_end = preferences.get("quiet_hours_end")
        if quiet_start is not None and quiet_end is not None:
            tz_name = preferences.get("quiet_hours_timezone", "UTC")
            tz = ZoneInfo(tz_name)
            now_local = timezone.now().astimezone(tz).time()

            # account for overnight ranges
            if quiet_start <= quiet_end:
                return quiet_start <= now_local <= quiet_end
            return now_local >= quiet_start or now_local <= quiet_end

        return True

    @staticmethod
    def create_subscription(
        user,
        endpoint: str,
        p256dh: str,
        auth: str,
        metadata: Dict[str, Any] = None,
    ) -> PushSubscription:
        """Create or update a subscription keyed on endpoint. Generate a name from metadata"""
        content_type = ContentType.objects.get_for_model(user)
        metadata = metadata or {}

        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "content_type": content_type,
                "object_id": user.pk,
                "p256dh": p256dh,
                "auth": auth,
                "metadata": metadata,
            },
        )

        if created and not subscription.name:
            browser = metadata.get("browser", "")
            os_name = metadata.get("os", "")
            if browser or os_name:
                parts = [p for p in [browser, os_name] if p]
                subscription.name = " on ".join(parts)
            else:
                subscription.name = "Unknown device"
            subscription.save(update_fields=["name"])

        return subscription


class NotificationSubscriptionService:
    @staticmethod
    def get_user_subscriptions(user) -> QuerySet:
        """Return all subscriptions for a user."""
        content_type = ContentType.objects.get_for_model(user)
        return PushSubscription.objects.filter(
            content_type=content_type,
            object_id=user.pk,
        )

    @staticmethod
    def get_user_subscription(user, subscription_id: int = None, endpoint: str = None) -> Optional[PushSubscription]:
        """Get a user subscription by ID or endpoint"""
        if not subscription_id and not endpoint:
            raise ValueError("Either subscription_id or endpoint must be provided")

        kwargs = {
            "content_type": ContentType.objects.get_for_model(user),
            "object_id": user.pk,
        }
        if subscription_id:
            kwargs["pk"] = subscription_id
        if endpoint:
            kwargs["endpoint"] = endpoint

        try:
            return PushSubscription.objects.get(**kwargs)
        except PushSubscription.DoesNotExist:
            return None

    @staticmethod
    def delete_user_subscription(user, subscription_id: int = None, endpoint: str = None) -> bool:
        """Delete a user subscription by ID or endpoint"""
        subscription = NotificationSubscriptionService.get_user_subscription(user, subscription_id, endpoint)
        if not subscription:
            return False
        subscription.delete()
        return True


class NotificationPreferencesService:
    @staticmethod
    def get_or_create_user_preferences(user, subscription_id: int = None) -> NotificationPreferences:
        """Get or create user or subscription preferences."""
        kwargs = {}
        if subscription_id:
            kwargs["content_type"] = ContentType.objects.get_for_model(PushSubscription)
            kwargs["object_id"] = subscription_id
        else:
            kwargs["content_type"] = ContentType.objects.get_for_model(user)
            kwargs["object_id"] = user.pk
        preferences, _ = NotificationPreferences.objects.get_or_create(**kwargs)
        return preferences

    @staticmethod
    def update_user_preferences(user, subscription_id: int = None, data: Dict[str, Any] = None) -> NotificationPreferences:
        """Update user or subscription notification preferences."""
        preferences = NotificationService.get_or_create_user_preferences(user, subscription_id)
        if not data:
            return preferences
        for field, value in data.items():
            setattr(preferences, field, value)
        preferences.save()
        return preferences
