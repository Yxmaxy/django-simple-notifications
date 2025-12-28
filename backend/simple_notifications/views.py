from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from simple_notifications.services import NotificationService
from simple_notifications.serializers import (
    PushSubscriptionCreateSerializer,
    SubscriptionStatusSerializer,
    PushNotificationResponseSerializer,
)


class PushSubscriptionView(APIView):
    """View for push subscription operations"""

    permission_classes = [IsAuthenticated]

    def post(self, request, app_name: str):
        """Subscribe to push notifications"""
        try:
            serializer = PushSubscriptionCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            endpoint = data["endpoint"]
            p256dh = data["keys"]["p256dh"]
            auth = data["keys"]["auth"]

            NotificationService.create_subscription(
                user=request.user,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
                app_name=app_name,
            )

            response_data = {
                "success": True,
                "message": "Successfully subscribed to push notifications",
            }
            response_serializer = PushNotificationResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            response_data = {"success": False, "error": str(e)}
            response_serializer = PushNotificationResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(
                response_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, app_name: str):
        """Unsubscribe from push notifications"""
        try:
            if not NotificationService.delete_subscription(request.user, app_name):
                response_data = {"success": False, "error": "Failed to unsubscribe"}
                response_serializer = PushNotificationResponseSerializer(
                    data=response_data
                )
                response_serializer.is_valid(raise_exception=True)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_data = {
                "success": True,
                "message": "Successfully unsubscribed from push notifications",
            }
            response_serializer = PushNotificationResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            response_data = {"success": False, "error": str(e)}
            response_serializer = PushNotificationResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(
                response_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubscriptionStatusView(APIView):
    """View for subscription status operations"""

    permission_classes = [IsAuthenticated]

    def get(self, request, app_name: str):
        """Get current subscription status"""
        try:
            subscription = NotificationService.get_user_subscription(request.user, app_name)

            response_data = {
                "success": True,
                "subscribed": subscription is not None,
                "subscription": subscription.to_dict() if subscription else None,
            }
            response_serializer = SubscriptionStatusSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            response_data = {"success": False, "error": str(e)}
            response_serializer = PushNotificationResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(
                response_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name="dispatch")
class ServiceWorkerPushView(APIView):
    """View for service worker push operations"""

    def post(self, request):
        """Endpoint for service worker to receive push messages"""
        # This endpoint is called by the browser's push service
        # We don't need to do anything here as the actual notification
        # is handled by the service worker on the client side
        return Response(status=status.HTTP_200_OK)
