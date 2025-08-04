# Django Simple Notifications 🔔

A simple Django library for sending push notifications to web browsers using the Web Push API.

## Installation

1. Install the package in your environment:
```bash
pip install git+https://github.com/Yxmaxy/django-simple-notifications.git

# additionaly provide the version of the package
pip install git+https://github.com/Yxmaxy/django-simple-notifications.git@v0.0.1
```

2. Install the requirements from the [requirements.txt](requirements.txt) file (and add the requirements to your project's requirements.txt file)

3. Add the app to your Django settings:
```python
INSTALLED_APPS = [
    # ...
    "simple_notifications",
]
```

4. Generate VAPID keys (for example using this tool: https://tools.reactpwa.com/vapid) and set Django settings.
```python
NOTIFICATIONS_VAPID_PUBLIC_KEY = "your-public-key"
NOTIFICATIONS_VAPID_PRIVATE_KEY = "your-private-key"
NOTIFICATIONS_VAPID_EMAIL = "your-email"
```

5. Add the notification URLs to your main URL configuration to access the endpoints:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("notifications/", include("simple_notifications.urls")),
]
```

6. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

## Multiple frontend apps on the same backend

The app is designed to allow multiple frontend apps to share the same backend.

1. Call the `subscribe/<APP_NAME>/` endpoint to register a subscription for the frontend app.

2. Reference the subscription using the `<APP_NAME>` to manage the subscription.
