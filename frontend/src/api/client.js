import axios from "axios";

// NOTE: the router is imported lazily inside the interceptor below, never at
// module scope. `@/router` statically imports every view, so a top-level import
// here pulls the entire component graph into anything that touches the API
// client. That closed a cycle as soon as a Pinia store imported this module:
//
//   stores/user -> api/client -> router -> SettingsView -> HelloWorld
//                      ^                                        |
//                      +--------- stores/user <-----------------+
//
// HelloWorld called mapState(useUserStore, ...) at MODULE scope rather than
// inside a function, so it read the binding before stores/user had finished
// initialising: "Cannot access 'useUserStore' before initialization".
//
// Rollup's hoisting hid this -- the production build was clean -- so it only
// surfaced under Vite's native ESM in dev.
//
// That particular pair of files is gone (both were Vue CLI scaffold), so the
// cycle above no longer has a component to close it. The dynamic imports stay
// deliberately: any future view that touches a store at module scope would
// reopen exactly the same hole. Keep both of this module's cross-imports
// dynamic.

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
      const [{ useUserStore }, { default: router }] = await Promise.all([
        import("@/stores/user"),
        import("@/router"),
      ]);
      useUserStore().logoutUser();
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
