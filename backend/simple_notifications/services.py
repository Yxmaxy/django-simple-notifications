import json
import logging
from typing import Dict, Any, Optional

from pywebpush import webpush, WebPushException

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from simple_notifications.models import PushSubscription


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
            logger.error("WebPushException: %s", ex)
            if ex.response and ex.response.json():
                logger.error("Response: %s", ex.response.json())
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error sending push notification: %s", e)
            return False

    @staticmethod
    def create_subscription(
        user, endpoint: str, p256dh: str, auth: str, app_name: str
    ) -> PushSubscription:
        """Delete existing subscription and create a new one"""
        NotificationService.delete_subscription(user, app_name)

        subscription = PushSubscription.objects.create(
            user=user,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            app_name=app_name,
        )

        return subscription

    @staticmethod
    def delete_subscription(user, app_name: str) -> bool:
        """Delete push subscription for a user"""
        try:
            PushSubscription.objects.filter(
                content_type=ContentType.objects.get_for_model(user),
                object_id=user.id,
                app_name=app_name
            ).delete()
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    @staticmethod
    def get_user_subscription(user, app_name: str) -> Optional[PushSubscription]:
        """Get push subscription for a user"""
        try:
            return PushSubscription.objects.get(
                content_type=ContentType.objects.get_for_model(user),
                object_id=user.id,
                app_name=app_name
            )
        except PushSubscription.DoesNotExist:
            return None
