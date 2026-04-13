import axios from "axios";
import router from "@/router";

const apiClient = axios.create({
  baseURL: "/api/v2",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

let redirectingToLogin = false;

const MUTATION_METHODS = ["post", "put", "patch", "delete"];

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 401: clear session and redirect to login
    if (error.response?.status === 401 && !redirectingToLogin) {
      redirectingToLogin = true;
      import("@/stores/user").then(({ useUserStore }) => {
        useUserStore().logoutUser();
      });
      router.push("/login").finally(() => {
        redirectingToLogin = false;
      });
    }

    // Network error on a mutation: queue for offline sync rather than surfacing an error
    const isNetworkError =
      !error.response &&
      (error.code === "ERR_NETWORK" ||
        error.code === "ECONNABORTED" ||
        !navigator.onLine);
    const isMutation = MUTATION_METHODS.includes(
      error.config?.method?.toLowerCase()
    );

    if (isNetworkError && isMutation) {
      const { useOfflineStore } = await import("@/stores/offline");
      const offlineStore = useOfflineStore();

      offlineStore.enqueue({
        method: error.config.method,
        url: error.config.url,
        data: error.config.data ? JSON.parse(error.config.data) : null,
      });

      const queuedError = new Error("Queued for offline sync");
      queuedError.queued = true;
      return Promise.reject(queuedError);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
