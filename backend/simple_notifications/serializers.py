from rest_framework import serializers

from simple_notifications.models import PushSubscription


class PushSubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating push subscriptions.

    Accepts the Web Push API subscription format with nested keys rather than flat model fields.
    """

    endpoint = serializers.URLField()
    keys = serializers.DictField(child=serializers.CharField())
    app_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=255, default=None)
    metadata = serializers.DictField(child=serializers.CharField(), required=False, default=dict)

    def validate_keys(self, value):
        for key in ("p256dh", "auth"):
            if key not in value:
                raise serializers.ValidationError(f"Missing required key: {key}")
            if not value[key]:
                raise serializers.ValidationError(f"Key {key} cannot be empty")
        return value


class PushSubscriptionUnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribe requests"""

    endpoint = serializers.URLField()


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for listing/detailing subscriptions"""

    class Meta:
        model = PushSubscription
        fields = ["id", "app_name", "name", "metadata", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
