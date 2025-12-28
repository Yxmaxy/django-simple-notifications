from django.contrib import admin

from simple_notifications.models import PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "endpoint",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = (
        "user__username",
        "user__email",
        "endpoint",
    )
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        # NOTE: Subscriptions should only be created via the API
        return False
