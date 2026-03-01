from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from simple_notifications.services import (
    NotificationService,
    NotificationSubscriptionService,
)
from simple_notifications.serializers import (
    PushSubscriptionCreateSerializer,
    PushSubscriptionSerializer,
    PushSubscriptionUnsubscribeSerializer,
)


class PushSubscriptionView(APIView):
    """View for push subscription operations"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new push subscription"""
        serializer = PushSubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        subscription = NotificationService.create_subscription(
            user=request.user,
            endpoint=data["endpoint"],
            p256dh=data["keys"]["p256dh"],
            auth=data["keys"]["auth"],
            metadata=data.get("metadata") or {},
        )

        return Response(
            PushSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        """Delete a push subscription"""
        serializer = PushSubscriptionUnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        endpoint = serializer.validated_data["endpoint"]
        deleted = NotificationSubscriptionService.delete_user_subscription(
            request.user,
            endpoint=endpoint
        )

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Subscription not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ServiceWorkerPushView(APIView):
    """Endpoint for the browser push service"""

    def post(self, request):
        """Endpoint for service worker to receive push messages"""
        # This endpoint is called by the browser's push service
        # We don't need to do anything here as the actual notification
        # is handled by the service worker on the client side
        return Response(status=status.HTTP_200_OK)
