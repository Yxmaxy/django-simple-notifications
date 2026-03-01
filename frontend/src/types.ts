/**
 * Configuration options for the Push Subscription Helper
 */
export interface PushSubscriptionHelperConfig {
    /** Base URL for the API (e.g., "https://api.example.com/notifications") */
    baseUrl: string;

    /** VAPID public key for the push subscription (e.g., "BN_VAPID_PUBLIC_KEY") */
    vapidPublicKey: string;

    /** Timeout for the push subscription initialization in milliseconds (e.g., 5000) */
    timeout?: number;

    /** Additional parameters for the fetch request to the backend (e.g., { credentials: "include" }) */
    serverRequestParameters?: RequestInit;

    /** Optional extra metadata to merge into auto-detected metadata (e.g., { app_version: "1.2.3" }) */
    metadata?: Record<string, string>;
}
