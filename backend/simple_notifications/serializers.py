from rest_framework import serializers

from simple_notifications.models import PushSubscription


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for PushSubscription model"""

    class Meta:
        model = PushSubscription
        fields = ["id", "endpoint", "p256dh", "auth", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PushSubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating push subscriptions"""

    endpoint = serializers.URLField()
    keys = serializers.DictField(child=serializers.CharField())

    def validate_keys(self, value):
        """Validate keys object"""
        required_keys = ["p256dh", "auth"]
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Missing required key: {key}")
            if not value[key]:
                raise serializers.ValidationError(f"Key {key} cannot be empty")
        return value

    def create(self, validated_data): ...
    def update(self, instance, validated_data): ...


class SubscriptionStatusSerializer(serializers.Serializer):
    """Serializer for subscription status response"""

    success = serializers.BooleanField()
    subscribed = serializers.BooleanField()
    subscription = PushSubscriptionSerializer(allow_null=True)

    def create(self, validated_data): ...
    def update(self, instance, validated_data): ...


class PushNotificationResponseSerializer(serializers.Serializer):
    """Serializer for push notification responses"""

    success = serializers.BooleanField()
    message = serializers.CharField(allow_blank=True)
    error = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data): ...
    def update(self, instance, validated_data): ...
