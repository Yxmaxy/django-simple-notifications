export function serviceWorkerPushHandler(registration: ServiceWorkerRegistration, event: any): void {
    // default options
    let options: NotificationOptions = {
        data: {},
        requireInteraction: false,
    }
    let title: string = "New Notification";

    // override default options
    if (event?.data) {
        try {
            const pushData = event?.data?.json();
            title = pushData?.title || title;
            options = { ...options, ...pushData };
        } catch (e) {
            console.error("Error parsing push data:", e);
        }
    }

    event.waitUntil(
        registration.showNotification(title, options)
    );
}
