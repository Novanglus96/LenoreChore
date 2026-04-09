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

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 && !redirectingToLogin) {
      redirectingToLogin = true;
      import("@/stores/user").then(({ useUserStore }) => {
        useUserStore().logoutUser();
      });
      router.push("/login").finally(() => {
        redirectingToLogin = false;
      });
    }
    return Promise.reject(error);
  }
);

export default apiClient;
