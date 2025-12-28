/**
 * Configuration options for the Push Subscription Helper
 */
export interface PushSubscriptionHelperConfig {
    /** Base URL for the API (e.g., "https://api.example.com/notifications") */
    baseUrl: string;

    /** App name for the push subscription (e.g., "website-visitor-geolocator") */
    appName: string;

    /** VAPID public key for the push subscription (e.g., "BN_VAPID_PUBLIC_KEY") */
    vapidPublicKey: string;

    /** Timeout for the push subscription initialization in milliseconds (e.g., 5000) */
    timeout: number;

    /** Additional parameters for the fetch request to the backend (e.g., { credentials: "include" }) */
    serverRequestParameters?: RequestInit;
}
