import { PushSubscriptionHelperConfig } from "./types";


class PushSubscriptionHelper {
    private readonly baseUrl: string;
    private readonly appName: string;
    private readonly vapidPublicKey: string;
    private readonly timeout: number = 5000;
    private readonly serverRequestParameters: RequestInit = {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
    };

    private isInitialized: boolean = false;
    private registration: ServiceWorkerRegistration | null = null;
    private subscription: PushSubscription | null = null;

    constructor(config: PushSubscriptionHelperConfig) {
        this.baseUrl = config.baseUrl;
        this.appName = config.appName;
        this.vapidPublicKey = config.vapidPublicKey;
        this.timeout = config.timeout ?? this.timeout;
        this.serverRequestParameters = config.serverRequestParameters ?? this.serverRequestParameters;

        if (this.baseUrl.endsWith("/"))
            this.baseUrl = this.baseUrl.slice(0, -1);

        this.isInitialized = false;
    }

   async initialize(): Promise<boolean> {
        if (this.isInitialized) {
            return true;
        }

        try {
            // Check if service workers are supported
            if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
                console.warn("Push notifications are not supported in this browser");
                return false;
            }

            // Service worker registration is handled by the user's code
            this.registration = await Promise.race([
                navigator.serviceWorker.ready,
                new Promise<never>((_, reject) =>
                    setTimeout(() => reject(new Error("Timed out waiting for service worker registration")), this.timeout)
                )
            ]);

            if (!this.registration) {
                return false;
            }

            // Check if we already have a subscription
            this.subscription = await this.registration.pushManager.getSubscription();

            this.isInitialized = true;
            return true;
        } catch (error) {
            console.error("Error initializing push notifications:", error);
            return false;
        }
    }

    async requestPermission(): Promise<NotificationPermission> {
        if (!("Notification" in window)) {
            throw new Error("Notifications are not supported");
        }

        const permission = await Notification.requestPermission();
        return permission;
    }

    async subscribe(): Promise<boolean> {
        try {
            if (!this.registration) {
                throw new Error("Service worker not registered");
            }

            const permission = await this.requestPermission();
            if (permission !== "granted") {
                throw new Error("Notification permission denied");
            }

            if (!this.vapidPublicKey) {
                throw new Error("VAPID public key not configured");
            }

            // Subscribe to push notifications
            const subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
            });

            this.subscription = subscription;

            // Send subscription to backend
            const success = await this.sendSubscriptionToServer(subscription);
            return success;
        } catch (error) {
            console.error("Error subscribing to push notifications:", error);
            return false;
        }
    }

    async unsubscribe(): Promise<boolean> {
        try {
            if (!this.subscription) {
                return true;
            }

            await this.subscription.unsubscribe();
            this.subscription = null;

            // Notify backend about unsubscription
            await this.removeSubscriptionFromServer();
            return true;
        } catch (error) {
            console.error("Error unsubscribing from push notifications:", error);
            return false;
        }
    }

    async isSubscribed(): Promise<boolean> {
        if (!this.registration) {
            return false;
        }

        const subscription = await this.registration.pushManager.getSubscription();
        return subscription !== null;
    }

    private async sendSubscriptionToServer(subscription: PushSubscription): Promise<boolean> {
        try {
            await fetch(`${this.baseUrl}/subscribe/${this.appName}/`, {
                method: "POST",
                ...this.serverRequestParameters,
                body: JSON.stringify({
                    endpoint: subscription.endpoint,
                    keys: {
                        p256dh: this.arrayBufferToBase64(subscription.getKey("p256dh")!),
                        auth: this.arrayBufferToBase64(subscription.getKey("auth")!)
                    },
                }),
            });
            return true;
        } catch (error) {
            console.error("Error sending subscription to server:", error);
            return false;
        }
    }

    private async removeSubscriptionFromServer(): Promise<boolean> {
        try {
            await fetch(`${this.baseUrl}/unsubscribe/${this.appName}/`, {
                method: "DELETE",
                ...this.serverRequestParameters,
            });
            return true;
        } catch (error) {
            console.error("Error removing subscription from server:", error);
            return false;
        }
    }

    private urlBase64ToUint8Array(base64String: string): BufferSource {
        const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, "+")
            .replace(/_/g, "/");

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i)!;
        }
        return outputArray;
    }

    private arrayBufferToBase64(buffer: ArrayBuffer): string {
        const bytes = new Uint8Array(buffer);
        let binary = "";
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]!);
        }
        return window.btoa(binary);
    }
}

export default PushSubscriptionHelper;
