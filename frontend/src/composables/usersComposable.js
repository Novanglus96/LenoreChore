import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useChoreStore } from "@/stores/chores";

const apiClient = axios.create({
  baseURL: "/api/v2",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

function handleApiError(error, message) {
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
  const queryClient = useQueryClient();
  const { data: users, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: getUsersFunction,
    select: response => response,
    client: queryClient,
  });

  return {
    users,
    isLoading,
  };
}

export async function loginUser(credentials) {
  const chorestore = useChoreStore();

  try {
    const response = await apiClient.post("/auth/login", credentials);
    chorestore.showSnackbar("User logged in successfully!", "success");
    const user = response.data;
    return user;
  } catch (error) {
    handleApiError(error, "User not logged in: ");
  }
}
