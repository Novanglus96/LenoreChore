import apiClient from "@/api/client";

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const output = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) {
    output[i] = raw.charCodeAt(i);
  }
  return output;
}

export function usePush() {
  function isSupported() {
    return (
      "serviceWorker" in navigator &&
      "PushManager" in window &&
      "Notification" in window
    );
  }

  // Register this browser for push: request permission, create a push
  // subscription with the server's VAPID key, and store it on the backend.
  async function subscribe() {
    if (!isSupported()) {
      throw new Error("Push notifications are not supported on this device.");
    }

    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
      throw new Error("Notification permission was not granted.");
    }

    const { data } = await apiClient.get("/push/vapid-key");
    if (!data.public_key) {
      throw new Error("Push notifications are not configured on the server.");
    }

    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(data.public_key),
      });
    }

    const json = subscription.toJSON();
    await apiClient.post("/push/subscribe", {
      endpoint: json.endpoint,
      p256dh: json.keys.p256dh,
      auth: json.keys.auth,
    });
    return true;
  }

  // Remove this browser's subscription from the backend and the push service.
  async function unsubscribe() {
    if (!isSupported()) return;
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await apiClient.post("/push/unsubscribe", {
        endpoint: subscription.endpoint,
      });
      await subscription.unsubscribe();
    }
  }

  // Read the current user's daily reminder preferences.
  async function getPrefs() {
    const { data } = await apiClient.get("/me/notifications");
    return data; // { notify_enabled, notify_time }
  }

  // Persist the current user's daily reminder preferences.
  async function savePrefs(notifyEnabled, notifyTime) {
    const { data } = await apiClient.put("/me/notifications", {
      notify_enabled: notifyEnabled,
      notify_time: notifyTime,
    });
    return data;
  }

  return { isSupported, subscribe, unsubscribe, getPrefs, savePrefs };
}
