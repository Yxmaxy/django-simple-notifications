from django.urls import path

from simple_notifications import views

app_name = "simple_notifications"

urlpatterns = [
    path(
        "subscription/",
        views.PushSubscriptionView.as_view(),
        name="push_subscription"
    ),
    path(
        "service-worker-push/",
        views.ServiceWorkerPushView.as_view(),
        name="service_worker_push",
    ),
]
