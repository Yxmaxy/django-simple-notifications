from rest_framework import serializers


class PushSubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating push subscriptions.

    Accepts the Web Push API subscription format with nested keys rather than flat model fields.
    """

    endpoint = serializers.URLField()
    keys = serializers.DictField(child=serializers.CharField())
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
