import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery } from "@tanstack/vue-query";
import axios from "axios";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";

function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const chorestore = useChoreStore();
  if (error.response) {
    console.error("Response error:", error.response.data);
    console.error("Status code:", error.response.status);
    console.error("Headers", error.response.headers);
  } else if (error.request) {
    console.error("No response received:", error.request);
  } else {
    console.error("Error during request setup:", error.message);
  }
  chorestore.showSnackbar(message + "Error #" + error.response.status, "error");
  throw error;
}

async function getUsersFunction() {
  try {
    const response = await apiClient.get("/users");
    return response.data;
  } catch (error) {
    handleApiError(error, "Users not fetched: ");
  }
}

export function useUsers() {
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const { data: users, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: getUsersFunction,
    select: response => response,
    enabled: isAuthenticated,
  });

  return {
    users,
    isLoading,
  };
}

export async function loginUser(credentials) {
  const chorestore = useChoreStore();

  try {
    await axios.post("/_allauth/browser/v1/auth/login", credentials);
  } catch (error) {
    // 409 means already authenticated — proceed to fetch user
    if (!error.response || error.response.status !== 409) {
      handleApiError(error, "User not logged in: ");
      return;
    }
  }

  try {
    const meResponse = await apiClient.get("/me");
    chorestore.showSnackbar("User logged in successfully!", "success");
    return meResponse.data;
  } catch (error) {
    handleApiError(error, "User not logged in: ");
  }
}

export async function logoutUser() {
  try {
    await axios.delete("/_allauth/browser/v1/auth/session");
  } catch {
    // Session may already be invalid — proceed with local cleanup
  }
}
