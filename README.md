# Django Simple Notifications 🔔

A simple Django library for sending push notifications to web browsers using the Web Push API.

## Installation

### Backend (Django)

1. Install the package in your environment:
```bash
pip install git+https://github.com/Yxmaxy/django-simple-notifications.git

# additionaly provide the version of the package
pip install git+https://github.com/Yxmaxy/django-simple-notifications.git@v2.0.0
```

2. Add the app to your Django settings:
```python
INSTALLED_APPS = [
    # ...
    "simple_notifications",
]
```

3. Generate VAPID keys (for example using this tool: https://tools.reactpwa.com/vapid) and set Django settings.
```python
NOTIFICATIONS_VAPID_PUBLIC_KEY = "your-public-key"
NOTIFICATIONS_VAPID_PRIVATE_KEY = "your-private-key"
NOTIFICATIONS_VAPID_EMAIL = "your-email"
```

4. Add the notification URLs to your main URL configuration to access the endpoints:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("notifications/", include("simple_notifications.urls")),
]
```

5. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```


### Frontend (eg. Vite)

1. Install the package in your environment:
```bash
npm install git+ssh://git@github.com:Yxmaxy/django-simple-notifications.git --save

# or with specific version
npm install git+ssh://git@github.com:Yxmaxy/django-simple-notifications.git#v2.0.0 --save
```

2. Add the push event listener to your service worker (`src/sw.js`):
```javascript
import { serviceWorkerPushHandler } from "django-simple-notifications";

self.addEventListener("push", (event) => {
    serviceWorkerPushHandler(self.registration, event);
});
```

3. Add code which allows the user to subscribe to push notifications. For example, this code is taken from a "Notification Toggle Button":

```javascript
const pushService = new PushSubscriptionHelper({
    baseUrl: "http://localhost:8000/notifications/",
    vapidPublicKey: "your-public-key",
});

const handleToggle = async () => {
    const supported = await pushService.initialize();

    if (!supported) {
        return;
    }

    const subscribed = await pushService.isSubscribed();

    if (subscribed) {
        const success = await pushService.unsubscribe();
    } else {
        const success = await pushService.subscribe();
    }
};
```
